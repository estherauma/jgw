#!/bin/bash

# Development Setup Script for JGW Pandas
# This script sets up the development environment using Docker Compose

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if file exists
file_exists() {
    [ -f "$1" ]
}

# Function to check if directory exists
dir_exists() {
    [ -d "$1" ]
}

print_status "🚀 Setting up JGW Pandas Development Environment"
echo ""

# Check prerequisites
print_status "Checking prerequisites..."

# Check if Docker is installed
if ! command_exists docker; then
    print_error "Docker is not installed. Please install Docker first."
    print_status "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    print_status "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

print_success "Docker and Docker Compose are installed"

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    
    # Create .env file with development settings
    cat > .env << EOF
# Database Configuration
DB_ENGINE=django.db.backends.postgresql_psycopg2
DB_NAME=jgw_pandas_dev
DB_USERNAME=postgres
DB_PASSWORD=devpassword
DB_HOST=db
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379

# Django Settings
SECRET_KEY=dev-secret-key-change-in-production-$(date +%s)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# JGW API Configuration
JGW_API=your_jgw_api_url
JGW_API_SECRET=your_jgw_api_secret

# Email Configuration (optional for development)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Sentry (optional for development)
SENTRY_DSN=your_sentry_dsn_here
EOF
    
    print_success ".env file created with default values"
    print_warning "Please update .env with your actual values before running the application"
else
    print_success ".env file already exists"
fi

# Check if google_cred.json exists
if [ ! -f google_cred.json ]; then
    print_error "google_cred.json not found!"
    print_status "Please add your Google credentials file to the project root."
    print_status "You can get it from: https://console.cloud.google.com/iam-admin/serviceaccounts"
    print_status ""
    print_status "Steps to get Google credentials:"
    print_status "1. Go to Google Cloud Console"
    print_status "2. Navigate to IAM & Admin → Service Accounts"
    print_status "3. Create or select a service account"
    print_status "4. Generate a JSON key"
    print_status "5. Save as 'google_cred.json' in the project root"
    print_status ""
    read -p "Do you want to continue without Google credentials? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Exiting. Please add google_cred.json and run the script again."
        exit 1
    fi
    print_warning "Continuing without Google credentials. Some features may not work."
else
    print_success "google_cred.json found"
fi

# Check if docker-compose.dev.yml exists
if [ ! -f docker-compose.dev.yml ]; then
    print_error "docker-compose.dev.yml not found!"
    print_status "Please ensure the development Docker Compose file exists."
    exit 1
fi

print_success "All required files are present"

# Check if ports are available
print_status "Checking if required ports are available..."

check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $port is already in use by another service"
        print_status "You may need to stop the service using port $port or change the port in docker-compose.dev.yml"
        return 1
    else
        print_success "Port $port is available for $service"
        return 0
    fi
}

# Check all required ports
ports_available=true
check_port 8000 "Web application" || ports_available=false
check_port 5432 "PostgreSQL database" || ports_available=false
check_port 6379 "Redis cache" || ports_available=false
check_port 9000 "Portainer" || ports_available=false

if [ "$ports_available" = false ]; then
    print_warning "Some ports are not available. You may encounter issues."
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Exiting. Please free up the required ports and run the script again."
        exit 1
    fi
fi

# Clean up any existing containers
print_status "Cleaning up any existing development containers..."
docker compose -f docker-compose.dev.yml down --remove-orphans 2>/dev/null || true

# Build and start the development environment
print_status "Building and starting development environment..."
echo ""

# Ask user if they want to build or just start
read -p "Do you want to rebuild all containers? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Building containers from scratch..."
    docker compose -f docker-compose.dev.yml up --build -d
else
    print_status "Starting existing containers..."
    docker compose -f docker-compose.dev.yml up -d
fi

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check if services are running
print_status "Checking service status..."

services=("web" "db" "redis" "celery_worker" "celery_beat" "portainer")
all_services_running=true

for service in "${services[@]}"; do
    if docker compose -f docker-compose.dev.yml ps --services --filter "status=running" | grep -q "^$service$"; then
        print_success "$service is running"
    else
        print_error "$service is not running"
        all_services_running=false
    fi
done

if [ "$all_services_running" = false ]; then
    print_error "Some services failed to start. Checking logs..."
    docker compose -f docker-compose.dev.yml logs --tail=20
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
docker compose -f docker-compose.dev.yml exec web python manage.py migrate

# Create superuser (optional)
print_status "Checking if superuser exists..."
if ! docker compose -f docker-compose.dev.yml exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists:', User.objects.filter(is_superuser=True).exists())" 2>/dev/null | grep -q "True"; then
    print_status "No superuser found. You can create one later with:"
    print_status "docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser"
fi

# Collect static files
print_status "Collecting static files..."
docker compose -f docker-compose.dev.yml exec web python manage.py collectstatic --noinput

print_success "Development environment is ready!"
echo ""
echo "🎉 Access Points:"
echo "   - Web App: http://localhost:8000"
echo "   - Portainer: http://localhost:9000"
echo "   - Database: localhost:5432"
echo "   - Redis: localhost:6379"
echo ""
echo "📋 Useful Commands:"
echo "   - View logs: docker compose -f docker-compose.dev.yml logs -f"
echo "   - Stop services: docker compose -f docker-compose.dev.yml down"
echo "   - Restart services: docker compose -f docker-compose.dev.yml restart"
echo "   - Access Django shell: docker compose -f docker-compose.dev.yml exec web python manage.py shell"
echo "   - Run migrations: docker compose -f docker-compose.dev.yml exec web python manage.py migrate"
echo "   - Create superuser: docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser"
echo ""
print_success "Happy coding! 🚀"