# Deployment Guide

Complete guide for deploying the Music Analysis Platform to production.

## Deployment Options

### Option 1: Docker Compose (Recommended for Small-Medium Scale)

#### Prerequisites
- Server with Docker & Docker Compose
- Minimum 4GB RAM, 2 CPU cores
- 20GB disk space

#### Steps

1. **Clone Repository**
```bash
git clone <repo-url>
cd music-analysis-platform-prd
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with production values
nano .env
```

3. **Start Services**
```bash
docker-compose up -d
```

4. **Initialize Database**
```bash
docker-compose exec api alembic upgrade head
```

5. **Verify Services**
```bash
docker-compose ps
curl http://localhost:8000/health
```

### Option 2: Kubernetes (Recommended for Large Scale)

#### Prerequisites
- Kubernetes cluster (EKS, GKE, AKS)
- kubectl configured
- Helm (optional)

#### Steps

1. **Create Namespace**
```bash
kubectl create namespace music-analysis
```

2. **Create Secrets**
```bash
kubectl create secret generic music-analysis-secrets \
  --from-literal=db-password=<password> \
  --from-literal=jwt-secret=<secret> \
  --from-literal=openai-key=<key> \
  -n music-analysis
```

3. **Deploy Services**
```bash
kubectl apply -f k8s/ -n music-analysis
```

4. **Verify Deployment**
```bash
kubectl get pods -n music-analysis
kubectl get svc -n music-analysis
```

### Option 3: Cloud Platforms

#### AWS (Recommended)

**Services:**
- RDS for PostgreSQL
- ElastiCache for Redis
- ECS for containers
- ALB for load balancing
- S3 for storage

**Deployment:**
```bash
# Using CloudFormation or Terraform
terraform apply -var-file=production.tfvars
```

#### Google Cloud

**Services:**
- Cloud SQL for PostgreSQL
- Memorystore for Redis
- Cloud Run for containers
- Cloud Load Balancing
- Cloud Storage

**Deployment:**
```bash
gcloud run deploy music-analysis-api \
  --image gcr.io/project/music-analysis-api:latest \
  --platform managed \
  --region us-central1
```

#### Azure

**Services:**
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Container Instances
- Application Gateway
- Blob Storage

**Deployment:**
```bash
az container create \
  --resource-group music-analysis \
  --name music-analysis-api \
  --image myregistry.azurecr.io/music-analysis-api:latest
```

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database backups configured
- [ ] SSL certificates ready
- [ ] Domain configured
- [ ] Monitoring set up
- [ ] Logging configured
- [ ] Backup strategy defined
- [ ] Security audit completed
- [ ] Performance testing done

## Production Configuration

### 1. Environment Variables

```bash
# Security
JWT_SECRET=<generate-strong-random-string>
ENVIRONMENT=production

# Database
DB_PASSWORD=<strong-password>
DATABASE_URL=postgresql://user:pass@prod-db:5432/music_analysis
DATABASE_SSL_MODE=require

# Redis
REDIS_URL=redis://prod-redis:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Workers
WORKER_CONCURRENCY=4
DEMUCS_DEVICE=cuda
WHISPER_DEVICE=cuda

# LLM
OPENAI_API_KEY=<your-key>
LLM_MODEL=gpt-4

# Storage
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
S3_BUCKET=production-bucket

# Monitoring
SENTRY_DSN=<your-dsn>
LOG_LEVEL=WARNING
```

### 2. Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_songs_org_id ON songs(organization_id);
CREATE INDEX idx_songs_created_at ON songs(created_at DESC);
CREATE INDEX idx_analyses_status ON song_analyses(status);
CREATE INDEX idx_analyses_created_at ON song_analyses(created_at DESC);
CREATE INDEX idx_arrangements_song_id ON arrangements(song_id);
CREATE INDEX idx_setlist_items_setlist_id ON setlist_items(setlist_id);

-- Enable RLS
ALTER TABLE songs ENABLE ROW LEVEL SECURITY;
ALTER TABLE arrangements ENABLE ROW LEVEL SECURITY;
ALTER TABLE setlist_items ENABLE ROW LEVEL SECURITY;

-- Vacuum
VACUUM ANALYZE;
```

### 3. Redis Configuration

```bash
# Increase max memory
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Enable persistence
redis-cli CONFIG SET save "900 1 300 10 60 10000"
redis-cli CONFIG REWRITE
```

### 4. API Configuration

```python
# apps/api/main.py
app = FastAPI(
    title="Music Analysis Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com

# Configure Nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://api:8000;
    }
}
```

## Monitoring & Logging

### 1. Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'api'
    static_configs:
      - targets: ['localhost:8000']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']
```

### 2. ELK Stack

```yaml
# docker-compose.yml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  environment:
    - discovery.type=single-node

logstash:
  image: docker.elastic.co/logstash/logstash:8.0.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
```

### 3. Sentry Error Tracking

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

## Backup Strategy

### Database Backups

```bash
# Daily backup
0 2 * * * pg_dump -h localhost -U postgres music_analysis | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz

# Upload to S3
0 3 * * * aws s3 cp /backups/db_*.sql.gz s3://backup-bucket/
```

### Redis Backups

```bash
# Enable RDB persistence
redis-cli CONFIG SET save "900 1 300 10 60 10000"

# Backup RDB file
0 4 * * * cp /var/lib/redis/dump.rdb /backups/redis_$(date +\%Y\%m\%d).rdb
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      replicas: 3
    
  worker-audio:
    deploy:
      replicas: 4
    
  worker-semantic:
    deploy:
      replicas: 2
```

### Load Balancing

```bash
# Nginx upstream
upstream api {
    server api-1:8000;
    server api-2:8000;
    server api-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://api;
    }
}
```

## Health Checks

### API Health Check

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": await check_database(),
        "redis": await check_redis(),
    }
```

### Kubernetes Health Checks

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  template:
    spec:
      containers:
      - name: api
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Rollback Procedure

### Docker Compose

```bash
# Get previous image tag
docker images | grep music-analysis-api

# Rollback to previous version
docker-compose down
docker-compose up -d
```

### Kubernetes

```bash
# Get rollout history
kubectl rollout history deployment/api -n music-analysis

# Rollback to previous version
kubectl rollout undo deployment/api -n music-analysis

# Rollback to specific revision
kubectl rollout undo deployment/api --to-revision=2 -n music-analysis
```

## Troubleshooting

### High Memory Usage

```bash
# Check memory
docker stats

# Reduce worker concurrency
docker-compose exec worker-audio celery -A celery_pipeline worker --concurrency=2
```

### Database Connection Issues

```bash
# Check database
docker-compose exec postgres psql -U postgres -c "SELECT 1"

# Check connection pool
docker-compose logs api | grep "connection"
```

### Worker Not Processing Tasks

```bash
# Check Celery status
docker-compose exec redis redis-cli

# Check worker logs
docker-compose logs worker-audio

# Restart worker
docker-compose restart worker-audio
```

## References

- [Docker Deployment](https://docs.docker.com/engine/install/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS Deployment](https://aws.amazon.com/getting-started/)
- [Google Cloud Deployment](https://cloud.google.com/docs)
- [Azure Deployment](https://docs.microsoft.com/en-us/azure/)
