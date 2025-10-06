# Development Environment Setup

This guide explains how to set up the JGW Pandas application for local development using Docker.

## Prerequisites

- Docker and Docker Compose installed
- `google_cred.json` file from Google Cloud Console
- Git repository cloned

## Quick Start

1. **Run the setup script:**
   ```bash
   chmod +x setup-dev.sh
   ./setup-dev.sh
   ```

2. **Or manually:**
   ```bash
   # Create .env file (if it doesn't exist)
   cp .env.example .env
   # Edit .env with your values
   
   # Start development environment
   docker compose -f docker-compose.dev.yml up --build
   ```

## Development Files

- `docker-compose.dev.yml` - Development Docker Compose configuration
- `Dockerfile.dev` - Development Dockerfile (uses local google_cred.json)
- `setup-dev.sh` - Automated setup script
- `.env` - Environment variables (create from .env.example)

## Key Differences from Production

### Development Environment:
- ✅ Uses local `google_cred.json` file (mounted as volume)
- ✅ Hot reload enabled (code changes reflect immediately)
- ✅ Debug mode enabled
- ✅ Local database and Redis
- ✅ Portainer for container management

### Production Environment:
- ✅ Uses GitHub secrets for Google credentials
- ✅ Pre-built images from Docker Hub
- ✅ Optimized for performance
- ✅ Production database and Redis

## Services

| Service | Port | Description |
|---------|------|-------------|
| web | 8000 | Django application |
| db | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache |
| portainer | 9000 | Container management UI |

## Environment Variables

Create a `.env` file with these variables:

```bash
# Database
DB_ENGINE=django.db.backends.postgresql_psycopg2
DB_NAME=jgw_pandas_dev
DB_USERNAME=postgres
DB_PASSWORD=devpassword
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379

# Django
SECRET_KEY=dev-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# JGW API
JGW_API=your_api_url
JGW_API_SECRET=your_api_secret
```

## Google Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to IAM & Admin → Service Accounts
3. Create or select a service account
4. Generate a JSON key
5. Save as `google_cred.json` in the project root

## Common Commands

```bash
# Start development environment
docker compose -f docker-compose.dev.yml up

# Start in background
docker compose -f docker-compose.dev.yml up -d

# Stop services
docker compose -f docker-compose.dev.yml down

# View logs
docker compose -f docker-compose.dev.yml logs -f

# Rebuild containers
docker compose -f docker-compose.dev.yml up --build

# Access Django shell
docker compose -f docker-compose.dev.yml exec web python manage.py shell

# Run migrations
docker compose -f docker-compose.dev.yml exec web python manage.py migrate

# Create superuser
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

## Troubleshooting

### Google Credentials Error
- Ensure `google_cred.json` exists in project root
- Check file permissions
- Verify the service account has necessary permissions

### Database Connection Error
- Check if PostgreSQL container is running
- Verify database credentials in `.env`
- Check if port 5432 is available

### Port Already in Use
- Stop other services using the same ports
- Change ports in `docker-compose.dev.yml` if needed

## File Structure

```
jgw-pandas/
├── docker-compose.dev.yml      # Development compose file
├── Dockerfile.dev              # Development Dockerfile
├── setup-dev.sh               # Setup script
├── .env                       # Environment variables
├── google_cred.json           # Google credentials (local)
└── DEV_SETUP.md              # This file
```
