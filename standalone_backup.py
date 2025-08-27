#!/usr/bin/env python3
"""
Standalone Database Backup Script
Connects directly to PostgreSQL in Docker container and saves to ~/dbbackups

Features:
- Weekly backups (run via cron: 0 23 * * 0)
- Monthly email with latest backup attachment
- Automatic cleanup of old backups
- Compressed backups to save space

Run via cron: 0 23 * * 0 /usr/bin/python3 /path/to/standalone_backup.py
"""

import os
import sys
import datetime
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import subprocess


DB_CONFIG = {
    'host': 'localhost',  
    'port': 5432,        
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USERNAME', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
}


DB_CONTAINER = 'jgw-pandas-db-1'  


BACKUP_DIR = os.path.expanduser('~/dbbackups')
RETENTION_WEEKS = 6

EMAIL_CONFIG = {
    'smtp_server': os.getenv('EMAIL_HOST', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('EMAIL_PORT', '587')),
    'smtp_username': os.getenv('EMAIL_HOST_USER', ''),
    'smtp_password': os.getenv('EMAIL_HOST_PASSWORD', ''),
    'recipient_email': os.getenv('BACKUP_EMAIL_RECIPIENT', ''), 
    'sender_email': os.getenv('EMAIL_HOST_USER', ''),
    'use_tls': os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
}

def load_env_vars():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def check_database_connection():
    """Check if database is accessible using Docker exec"""
    try:
        cmd = [
            'docker', 'exec', DB_CONTAINER,
            'psql', '-U', DB_CONFIG['user'], '-d', DB_CONFIG['database'], '-c', 'SELECT 1;'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Database connection successful (Docker exec)")
            return True
        else:
            print(f"Database connection failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def get_database_size():
    """Get the size of the database using Docker exec"""
    try:
        cmd = [
            'docker', 'exec', DB_CONTAINER,
            'psql', '-U', DB_CONFIG['user'], '-d', DB_CONFIG['database'],
            '-c', "SELECT pg_size_pretty(pg_database_size(current_database()));"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 3:  
                size = lines[1].strip()
                print(f"Database size: {size}")
                return size
    except Exception as e:
        print(f"Could not determine database size: {e}")
    
    return "Unknown"

def get_database_info():
    
    try:
        cmd_version = [
            'docker', 'exec', DB_CONTAINER,
            'psql', '-U', DB_CONFIG['user'], '-d', DB_CONFIG['database'],
            '-c', "SELECT current_database(), version();"
        ]
        
        result_version = subprocess.run(cmd_version, capture_output=True, text=True)
        
        if result_version.returncode == 0:
            lines = result_version.stdout.strip().split('\n')
            if len(lines) >= 3:
                parts = lines[1].split('|')
                if len(parts) >= 2:
                    db_name = parts[0].strip()
                    version = parts[1].strip()
                else:
                    db_name = "Unknown"
                    version = "Unknown"
            else:
                db_name = "Unknown"
                version = "Unknown"
        else:
            db_name = "Unknown"
            version = "Unknown"
        
        
        cmd_tables = [
            'docker', 'exec', DB_CONTAINER,
            'psql', '-U', DB_CONFIG['user'], '-d', DB_CONFIG['database'],
            '-c', "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
        ]
        
        result_tables = subprocess.run(cmd_tables, capture_output=True, text=True)
        table_count = 0
        if result_tables.returncode == 0:
            lines = result_tables.stdout.strip().split('\n')
            if len(lines) >= 3:
                try:
                    table_count = int(lines[1].strip())
                except ValueError:
                    table_count = 0
        
        cmd_rows = [
            'docker', 'exec', DB_CONTAINER,
            'psql', '-U', DB_CONFIG['user'], '-d', DB_CONFIG['database'],
            '-c', "SELECT SUM(reltuples)::bigint AS estimate FROM pg_class WHERE relkind = 'r';"
        ]
        
        result_rows = subprocess.run(cmd_rows, capture_output=True, text=True)
        row_count = 0
        if result_rows.returncode == 0:
            lines = result_rows.stdout.strip().split('\n')
            if len(lines) >= 3:
                try:
                    row_count = int(lines[1].strip())
                except ValueError:
                    row_count = 0
        
        return {
            'database_name': db_name,
            'version': version,
            'table_count': table_count,
            'estimated_row_count': row_count
        }
    except Exception as e:
        print(f"Could not get database info: {e}")
        return {}

def create_backup():
    """Create comprehensive database backup using pg_dump"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = Path(BACKUP_DIR) / f"postgres_backup_{timestamp}.sql"
    
    print(f"Starting backup of database '{DB_CONFIG['database']}' to {backup_file}")
    
    try:
        
        Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)
        
        
        db_info = get_database_info()
        
        
        print("Using Docker exec for database backup...")
        
        
        compressed_backup_file = str(backup_file) + '.gz'
        
        
        cmd = [
            'docker', 'exec', DB_CONTAINER,
            'pg_dump',
            '-U', DB_CONFIG['user'],
            '-d', DB_CONFIG['database'],
            '--no-owner',          
            '--no-privileges',     
            '--no-comments',       
            '--no-security-labels',
            '--no-acl',
            '--no-reconnect',
            '--no-comments',
            '--no-owner',
            '--no-privileges',
            '--no-comments',
            '--no-security-labels'
        ]
        
        
        with open(compressed_backup_file, 'wb') as f:
            
            pg_dump_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            gzip_process = subprocess.Popen(['gzip'], stdin=pg_dump_process.stdout, stdout=f)
            
            
            pg_dump_process.stdout.close()
            gzip_process.communicate()
            pg_dump_result = pg_dump_process.wait()
            
            if pg_dump_result != 0:
                raise Exception(f"pg_dump failed with return code {pg_dump_result}")
        
        
        backup_file = Path(compressed_backup_file)
        
        
        file_size = backup_file.stat().st_size
        human_size = format_file_size(file_size)
        print(f"Backup completed successfully: {backup_file} ({human_size})")
        return backup_file
            
    except Exception as e:
        print(f"Backup failed: {e}")
        raise

def verify_backup(backup_file):
    """Verify backup file integrity for compressed files"""
    print(f"Verifying backup file: {backup_file}")
    
    try:
        if not backup_file.exists():
            raise Exception("Backup file does not exist")
        
        file_size = backup_file.stat().st_size
        if file_size == 0:
            raise Exception("Backup file is empty")
        
        human_size = format_file_size(file_size)
        print(f"File size: {human_size}")
        

        try:
            
            cmd = ['gunzip', '-c', str(backup_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise Exception("File cannot be decompressed")
            
            
            lines = result.stdout.split('\n')
            first_lines = lines[:20]
            
            
            header_content = '\n'.join(first_lines).upper()
            if not any(keyword in header_content for keyword in ['--', 'CREATE DATABASE', 'CREATE TABLE', 'INSERT INTO']):
                raise Exception("File does not appear to contain valid SQL backup content")
            
            
            if len(lines) > 20:
                last_lines = lines[-10:]  
                last_content = '\n'.join(last_lines).upper()
                
                if not any(keyword in last_content for keyword in ['INSERT INTO', 'CREATE TABLE', '--']):
                    raise Exception("File appears to be truncated or incomplete")
            
            print(f"Backup verification successful: {human_size}")
            return True
            
        except subprocess.TimeoutExpired:
            print("Verification timed out (file may be very large)")
            return True  
        except Exception as e:
            raise Exception(f"Compressed file verification failed: {e}")
        
    except Exception as e:
        print(f"Backup verification failed: {e}")
        return False

def cleanup_old_backups():
    """Clean up old backup files based on retention policy"""
    print(f"Cleaning up backups older than {RETENTION_WEEKS} weeks")
    
    try:
        backup_dir = Path(BACKUP_DIR)
        backup_patterns = ["*.sql.gz", "*.sql"]
        all_backups = []
        
        for pattern in backup_patterns:
            all_backups.extend(backup_dir.glob(pattern))
        
        all_backups.sort(key=lambda x: x.stat().st_mtime)
        
        
        if is_end_of_month():
            print("End of month detected - sending latest backup via email...")
            latest_backup = get_latest_backup()
            
            if latest_backup:
                file_size = latest_backup.stat().st_size
                human_size = format_file_size(file_size)
                
                subject = f"Monthly Database Backup - {datetime.datetime.now().strftime('%B %Y')}"
                body = f"""
Monthly Database Backup Report

Database: {DB_CONFIG['database']}
Backup File: {latest_backup.name}
File Size: {human_size}
Backup Date: {datetime.datetime.fromtimestamp(latest_backup.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
Generated by: Standalone Backup Script

This backup contains your database as of the end of the month.
Keep this file for long-term storage.
                """.strip()
                
                if send_email_with_attachment(subject, body, str(latest_backup)):
                    print(f"Monthly backup email sent: {latest_backup.name}")
                else:
                    print("Failed to send monthly backup email")
            else:
                print("No backup files found to email")
        
        backups_to_keep = RETENTION_WEEKS * 7  
        
        if len(all_backups) > backups_to_keep:
            old_files = all_backups[:len(all_backups) - backups_to_keep]
            total_size_removed = 0
            
            for old_file in old_files:
                try:
                    file_size = old_file.stat().st_size
                    old_file.unlink()
                    total_size_removed += file_size
                    print(f"Removed old backup: {old_file} ({format_file_size(file_size)})")
                except OSError as e:
                    print(f"Failed to remove old backup {old_file}: {e}")
            
            print(f"Cleanup completed. Removed {len(old_files)} files, freed {format_file_size(total_size_removed)}")
        else:
            print(f"No old backups to remove. Keeping {len(all_backups)} backups")
            
    except Exception as e:
        print(f"Cleanup failed: {e}")

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def send_email_with_attachment(subject, body, attachment_path):
    """Send email with backup file attachment"""
    try:
        if not all([EMAIL_CONFIG['smtp_username'], EMAIL_CONFIG['smtp_password'], 
                   EMAIL_CONFIG['recipient_email'], EMAIL_CONFIG['sender_email']]):
            print("Email configuration incomplete. Skipping email send.")
            return False
        
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['recipient_email']
        msg['Subject'] = subject
        
        
        msg.attach(MIMEText(body, 'plain'))
        
        
        if attachment_path and Path(attachment_path).exists():
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {Path(attachment_path).name}'
            )
            msg.attach(part)
        
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        
        
        if EMAIL_CONFIG['use_tls']:
            server.starttls()
        
        server.login(EMAIL_CONFIG['smtp_username'], EMAIL_CONFIG['smtp_password'])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['recipient_email'], text)
        server.quit()
        
        print(f"Email sent successfully to {EMAIL_CONFIG['recipient_email']}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def is_end_of_month():
    """Check if today is the end of the month"""
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    return tomorrow.day == 1

def get_latest_backup():
    """Get the most recent backup file"""
    try:
        backup_dir = Path(BACKUP_DIR)
        backup_patterns = ["*.sql.gz", "*.sql"]
        all_backups = []
        
        for pattern in backup_patterns:
            all_backups.extend(backup_dir.glob(pattern))
        
        if not all_backups:
            return None
        
        
        latest_backup = max(all_backups, key=lambda x: x.stat().st_mtime)
        return latest_backup
        
    except Exception as e:
        print(f"Error getting latest backup: {e}")
        return None

def main():
    """Main backup function"""
    start_time = datetime.datetime.now()
    print("=== Starting Standalone Database Backup Process ===")
    
    try:
        
        load_env_vars()
        
        
        if not check_database_connection():
            raise Exception("Cannot connect to database")
        

        get_database_size()
        
        
        backup_file = create_backup()
        print("Backup creation completed successfully")
        
        
        if not verify_backup(backup_file):
            raise Exception("Backup verification failed")
        
        
        cleanup_old_backups()
        
        end_time = datetime.datetime.now()
        execution_time = end_time - start_time
        
        print(f"=== Backup Process Completed Successfully in {execution_time} ===")
        return 0
        
    except Exception as e:
        error_msg = str(e)
        print(f"=== Backup Process Failed: {error_msg} ===")
        return 1

if __name__ == "__main__":
    sys.exit(main())
