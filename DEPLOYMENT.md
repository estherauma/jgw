# Deployment Guide

This project supports automated deployments to staging and manual deployments to production with Slack notifications.

## 🚀 Deployment Workflows

### 1. Staging Deployment (Automatic)
- **Trigger**: Push to `develop` branch
- **File**: `.github/workflows/deploy.yml`
- **Environment**: Staging server
- **Branch**: `develop`

### 2. Production Deployment (Manual)
- **Trigger**: Manual workflow dispatch
- **File**: `.github/workflows/deploy-production.yml`
- **Environment**: Production server
- **Branch**: `main`
- **Requires**: Admin approval

## 🔧 Required GitHub Secrets

### For Staging (Current setup)
- `SSH_PRIVATE_KEY` - SSH private key for staging server
- `SSH_HOST` - Staging server hostname/IP
- `USERNAME` - SSH username for staging
- `HOST` - Staging server hostname/IP (same as SSH_HOST)
- `SLACK_WEBHOOK_URL` - Slack webhook URL for notifications

### For Production (New setup)
- `PRODUCTION_SSH_PRIVATE_KEY` - SSH private key for production server
- `PRODUCTION_HOST` - Production server hostname/IP
- `PRODUCTION_USERNAME` - SSH username for production
- `SLACK_WEBHOOK_URL` - Slack webhook URL for notifications

## 📋 Deployment Process

### Staging (Automatic)
1. Push code to `develop` branch
2. GitHub Actions automatically:
   - Sets up SSH connection
   - Pulls latest code
   - Rebuilds Docker containers
   - Verifies deployment
   - Sends Slack notification

### Production (Manual)
1. Merge tested code to `main` branch
2. Go to GitHub Actions → "Deploy to Production"
3. Click "Run workflow"
4. Confirm deployment
5. GitHub Actions:
   - Creates backup
   - Deploys to production
   - Verifies deployment
   - Sends Slack notification

## 🔒 Security Features

- **Environment Protection**: Production requires admin approval
- **Manual Confirmation**: Production deployment requires explicit confirmation
- **Backup Creation**: Automatic backups before production deployment
- **Health Checks**: Verification that applications are responding

## 📱 Slack Notifications

Both workflows send detailed Slack notifications including:
- Deployment status (success/failure)
- Environment information
- Commit details
- Author information
- Change descriptions
- Direct links to commits

## 🛠️ Server Requirements

### Staging Server
- SSH access configured
- Docker and Docker Compose installed
- Git repository cloned
- Proper permissions for Docker commands

### Production Server
- SSH access configured
- Docker and Docker Compose installed
- Git repository cloned
- Proper permissions for Docker commands
- Backup directory with write permissions

## 🔍 Troubleshooting

### Common Issues
1. **SSH Connection Failed**: Check SSH keys and host configuration
2. **Docker Permission Denied**: Ensure user has sudo access
3. **Health Check Failed**: Check if Django app is running properly
4. **Slack Notifications Not Working**: Verify webhook URL

### Manual Rollback
If deployment fails, you can manually rollback:
```bash
cd ~/jgw-pandas
git reset --hard HEAD~1
sudo docker compose down
sudo docker compose up -d --build
```



