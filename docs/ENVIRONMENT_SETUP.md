# Environment Setup Guide

Complete guide for configuring the Music Analysis Platform.

## Quick Start

### 1. Clone Repository

```bash
git clone <repo-url>
cd music-analysis-platform-prd
```

### 2. Create Environment File

Copy the template and fill in your values:

```bash
cp .env.example .env
```

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Initialize Database

```bash
docker-compose exec api alembic upgrade head
```

### 5. Access Services

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000/docs
- **Flower**: http://localhost:5555
- **pgAdmin**: http://localhost:5050

## Environment Variables

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_USER` | `music_user` | PostgreSQL username |
| `DB_PASSWORD` | `music_password` | PostgreSQL password |
| `DB_NAME` | `music_analysis` | Database name |

### Redis Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL |

### FastAPI Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | `your-secret-key-...` | JWT signing secret (change in production) |
| `ENVIRONMENT` | `development` | Environment (development, staging, production) |

### Audio Processing

| Variable | Default | Description |
|----------|---------|-------------|
| `ESSENTIA_CACHE_DIR` | `/tmp/essentia_cache` | Cache directory for Essentia |
| `DEMUCS_MODEL` | `htdemucs` | Demucs model (htdemucs, mdx, etc.) |
| `DEMUCS_DEVICE` | `cpu` | Device for Demucs (cpu, cuda) |
| `WHISPER_MODEL` | `base` | Whisper model size (tiny, base, small, medium, large) |
| `WHISPER_DEVICE` | `cpu` | Device for Whisper (cpu, cuda) |

### LLM Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (empty) | OpenAI API key for LLM features |
| `LLM_MODEL` | `gpt-3.5-turbo` | LLM model to use |
| `LLM_TEMPERATURE` | `0.7` | LLM temperature (0-1) |

### pgAdmin Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PGADMIN_EMAIL` | `admin@example.com` | pgAdmin login email |
| `PGADMIN_PASSWORD` | `admin` | pgAdmin login password |

### Frontend Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api` | Backend API URL |

### Storage Configuration (S3)

| Variable | Default | Description |
|----------|---------|-------------|
| `AWS_ACCESS_KEY_ID` | (empty) | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | (empty) | AWS secret key |
| `AWS_REGION` | `us-east-1` | AWS region |
| `S3_BUCKET` | `music-analysis-bucket` | S3 bucket name |

### Email Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server host |
| `SMTP_PORT` | `587` | SMTP server port |
| `SMTP_USER` | (empty) | SMTP username |
| `SMTP_PASSWORD` | (empty) | SMTP password |

### Monitoring

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_DSN` | (empty) | Sentry error tracking DSN |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

## Development Setup

### 1. Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- Git

### 2. Local Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### 3. Database Migrations

```bash
# Create new migration
docker-compose exec api alembic revision --autogenerate -m "Add new table"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback migration
docker-compose exec api alembic downgrade -1
```

### 4. Running Tests

```bash
# Backend tests
docker-compose exec api pytest tests/ -v

# Frontend tests
docker-compose exec web npm run test

# All tests
docker-compose exec api pytest && docker-compose exec web npm run test
```

## Production Setup

### 1. Environment Variables

Change these in production:

```bash
# Use strong JWT secret
JWT_SECRET=generate-strong-random-string-here

# Use production database
DB_PASSWORD=strong-password-here

# Use GPU for faster processing
DEMUCS_DEVICE=cuda
WHISPER_DEVICE=cuda

# Use production LLM
LLM_MODEL=gpt-4

# Set environment
ENVIRONMENT=production
```

### 2. Database

```bash
# Use managed database (AWS RDS, Google Cloud SQL, etc.)
DATABASE_URL=postgresql://user:pass@prod-db.example.com/music_analysis

# Enable SSL
DATABASE_SSL_MODE=require
```

### 3. Redis

```bash
# Use managed Redis (AWS ElastiCache, etc.)
REDIS_URL=redis://prod-redis.example.com:6379/0
```

### 4. Storage

```bash
# Use S3 for file storage
AWS_ACCESS_KEY_ID=prod-access-key
AWS_SECRET_ACCESS_KEY=prod-secret-key
S3_BUCKET=production-bucket
```

### 5. Monitoring

```bash
# Enable error tracking
SENTRY_DSN=https://key@sentry.io/project-id

# Set log level
LOG_LEVEL=WARNING
```

## Docker Compose Services

### Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| postgres | 5432 | Database |
| redis | 6379 | Cache & message broker |
| api | 8000 | FastAPI backend |
| worker-audio | - | Audio analysis worker |
| worker-semantic | - | Semantic analysis worker |
| beat | - | Celery scheduler |
| flower | 5555 | Celery monitoring |
| web | 3000 | Next.js frontend |
| pgadmin | 5050 | Database management |

### Starting Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d postgres redis

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v
```

## Troubleshooting

### Database Connection Error

```bash
# Check if postgres is running
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### Redis Connection Error

```bash
# Check if redis is running
docker-compose ps redis

# Test redis connection
docker-compose exec redis redis-cli ping

# Restart redis
docker-compose restart redis
```

### Worker Not Processing Tasks

```bash
# Check worker status
docker-compose logs worker-audio

# Check Celery tasks
docker-compose exec redis redis-cli

# Restart worker
docker-compose restart worker-audio
```

### API Not Responding

```bash
# Check API logs
docker-compose logs api

# Check if API is running
docker-compose ps api

# Restart API
docker-compose restart api
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Generate strong JWT secret
- [ ] Enable HTTPS in production
- [ ] Set up SSL certificates
- [ ] Configure CORS properly
- [ ] Enable database SSL
- [ ] Use environment variables for secrets
- [ ] Set up firewall rules
- [ ] Enable monitoring and alerting
- [ ] Regular database backups
- [ ] Regular security updates

## Performance Tuning

### Database

```sql
-- Create indexes
CREATE INDEX idx_songs_org_id ON songs(organization_id);
CREATE INDEX idx_analyses_status ON song_analyses(status);
```

### Redis

```bash
# Increase max memory
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Workers

```bash
# Increase worker concurrency
docker-compose exec worker-audio celery -A celery_pipeline worker --concurrency=4
```

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Celery Documentation](https://docs.celeryproject.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
