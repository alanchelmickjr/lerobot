# BOM Calculator Deployment Guide

Complete guide for deploying the BOM Calculator application to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Deployment](#quick-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Cloud Deployments](#cloud-deployments)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Database Configuration](#database-configuration)
8. [Performance Tuning](#performance-tuning)
9. [Monitoring Setup](#monitoring-setup)
10. [Security Hardening](#security-hardening)
11. [Backup & Recovery](#backup--recovery)
12. [Scaling Strategies](#scaling-strategies)
13. [Maintenance](#maintenance)

---

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB
- OS: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+

**Recommended Requirements:**
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 50+ GB SSD
- OS: Ubuntu 22.04 LTS

### Software Dependencies

```bash
# Required
- Python 3.9+
- Node.js 16+
- PostgreSQL 15+ (production) or SQLite 3.40+ (development)
- Redis 7.0+ (optional, for caching)
- Nginx 1.20+ (for reverse proxy)

# Optional
- Docker 24+
- Docker Compose 2+
- Kubernetes 1.28+ (for K8s deployment)
- Certbot (for SSL certificates)
```

---

## Quick Deployment

### One-Command Production Deployment

```bash
# Clone and deploy
git clone https://github.com/yourusername/lerobot.git
cd lerobot/src/lerobot/robots/bom_calculator

# Run automated deployment
./deploy.sh production

# Or using Python
python bom_calculator.py --mode production --deploy
```

This will:
- ✅ Check system requirements
- ✅ Install dependencies
- ✅ Configure environment
- ✅ Build frontend
- ✅ Setup database
- ✅ Configure Nginx
- ✅ Start services
- ✅ Setup monitoring

---

## Docker Deployment

### Docker Compose (Recommended)

#### 1. Basic Docker Deployment

```bash
# Clone repository
git clone https://github.com/yourusername/lerobot.git
cd lerobot/src/lerobot/robots/bom_calculator

# Configure environment
cp .env.example .env.production
nano .env.production  # Edit configuration

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

#### 2. Production Docker Compose

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - frontend_build:/usr/share/nginx/html:ro
    depends_on:
      - api
      - frontend
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - NODE_ENV=production
        - VITE_API_URL=${API_URL}
    volumes:
      - frontend_build:/app/dist
    command: npm run build
    environment:
      - NODE_ENV=production

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS}
      - DEBUG=false
    depends_on:
      - db
      - redis
    restart: unless-stopped
    command: gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=bom_calculator
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning:ro
    ports:
      - "3001:3000"
    restart: unless-stopped

volumes:
  frontend_build:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

#### 3. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose -f docker-compose.production.yml up -d --build

# View logs
docker-compose logs -f

# Scale API workers
docker-compose -f docker-compose.production.yml up -d --scale api=3
```

### Docker Swarm Deployment

```bash
# Initialize swarm
docker swarm init

# Create secrets
echo "your-secret-key" | docker secret create bom_secret_key -
echo "your-db-password" | docker secret create bom_db_password -

# Deploy stack
docker stack deploy -c docker-stack.yml bom_calculator

# Check services
docker service ls
docker service logs bom_calculator_api
```

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace bom-calculator

# Create secrets
kubectl create secret generic bom-secrets \
  --from-literal=secret-key='your-secret-key' \
  --from-literal=db-password='your-db-password' \
  -n bom-calculator

# Apply configurations
kubectl apply -f k8s/ -n bom-calculator

# Check deployment
kubectl get pods -n bom-calculator
kubectl get services -n bom-calculator
```

---

## Manual Deployment

### Step-by-Step Production Setup

#### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.9 python3-pip python3-venv \
  nodejs npm postgresql postgresql-contrib redis-server \
  nginx certbot python3-certbot-nginx git build-essential

# Create application user
sudo useradd -m -s /bin/bash bomcalc
sudo usermod -aG sudo bomcalc
```

#### 2. Clone and Setup Application

```bash
# Switch to app user
sudo su - bomcalc

# Clone repository
git clone https://github.com/yourusername/lerobot.git
cd lerobot/src/lerobot/robots/bom_calculator

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install gunicorn uvloop httptools
```

#### 3. Configure PostgreSQL

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE bom_calculator;
CREATE USER bomcalc WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE bom_calculator TO bomcalc;
\q

# Update database URL in .env
DATABASE_URL=postgresql://bomcalc:secure_password@localhost/bom_calculator
```

#### 4. Build Frontend

```bash
cd frontend
npm ci --production
npm run build
cd ..
```

#### 5. Configure Systemd Services

```bash
# Backend service
sudo nano /etc/systemd/system/bom-calculator-api.service
```

```ini
[Unit]
Description=BOM Calculator API
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=bomcalc
Group=bomcalc
WorkingDirectory=/home/bomcalc/lerobot/src/lerobot/robots/bom_calculator/backend
Environment="PATH=/home/bomcalc/lerobot/src/lerobot/robots/bom_calculator/venv/bin"
ExecStart=/home/bomcalc/lerobot/src/lerobot/robots/bom_calculator/venv/bin/gunicorn \
    main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/bom-calculator/access.log \
    --error-logfile /var/log/bom-calculator/error.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 6. Configure Nginx

```nginx
# /etc/nginx/sites-available/bom-calculator
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Frontend
    location / {
        root /home/bomcalc/lerobot/src/lerobot/robots/bom_calculator/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # Monitoring
    location /metrics {
        proxy_pass http://localhost:8000/metrics;
        allow 127.0.0.1;
        deny all;
    }
}
```

#### 7. Start Services

```bash
# Enable and start services
sudo systemctl enable bom-calculator-api
sudo systemctl start bom-calculator-api

# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/bom-calculator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Check status
sudo systemctl status bom-calculator-api
sudo systemctl status nginx
```

---

## Cloud Deployments

### AWS EC2 Deployment

#### 1. Launch EC2 Instance

```bash
# Using AWS CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key \
  --security-group-ids sg-xxxxxx \
  --subnet-id subnet-xxxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=bom-calculator}]'
```

#### 2. Configure Security Groups

```bash
# Allow HTTP, HTTPS, and SSH
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

#### 3. Deploy Application

```bash
# SSH to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Run deployment script
curl -sSL https://raw.githubusercontent.com/yourusername/lerobot/main/deploy/aws-deploy.sh | bash
```

### Heroku Deployment

#### 1. Prepare for Heroku

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login

# Create app
heroku create bom-calculator-app
```

#### 2. Configure Buildpacks

```bash
# Add multiple buildpacks
heroku buildpacks:add heroku/python
heroku buildpacks:add heroku/nodejs
```

#### 3. Create Procfile

```procfile
web: cd backend && gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker
release: cd backend && python -m init_db
```

#### 4. Deploy

```bash
# Add Heroku remote
heroku git:remote -a bom-calculator-app

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=your-database-url

# Deploy
git push heroku main

# Scale dynos
heroku ps:scale web=1
```

### DigitalOcean App Platform

#### 1. Create app.yaml

```yaml
name: bom-calculator
region: nyc
services:
  - name: api
    environment_slug: python
    github:
      repo: yourusername/lerobot
      branch: main
      deploy_on_push: true
    source_dir: src/lerobot/robots/bom_calculator/backend
    build_command: pip install -r requirements.txt
    run_command: gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${db.DATABASE_URL}
    http_port: 8000
    instance_count: 1
    instance_size_slug: basic-xxs
    
  - name: frontend
    environment_slug: node-js
    github:
      repo: yourusername/lerobot
      branch: main
      deploy_on_push: true
    source_dir: src/lerobot/robots/bom_calculator/frontend
    build_command: npm ci && npm run build
    envs:
      - key: VITE_API_URL
        scope: BUILD_TIME
        value: ${api.PUBLIC_URL}
    routes:
      - path: /

databases:
  - name: db
    engine: PG
    version: "15"
```

#### 2. Deploy

```bash
# Using DigitalOcean CLI
doctl apps create --spec app.yaml

# Or using UI
# Upload app.yaml in DigitalOcean App Platform
```

### Google Cloud Platform

```bash
# Create app.yaml for App Engine
cat > app.yaml << EOF
runtime: python39
entrypoint: gunicorn -b :$PORT main:app

env_variables:
  DATABASE_URL: "postgresql://..."
  SECRET_KEY: "your-secret-key"

handlers:
- url: /static
  static_dir: frontend/dist
- url: /.*
  script: auto
EOF

# Deploy
gcloud app deploy

# View application
gcloud app browse
```

---

## SSL/TLS Configuration

### Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Setup auto-renewal cron
sudo crontab -e
# Add: 0 0,12 * * * /usr/bin/certbot renew --quiet
```

### Manual SSL Configuration

```nginx
# Strong SSL Configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

---

## Database Configuration

### PostgreSQL Optimization

```sql
-- Performance tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;

-- Reload configuration
SELECT pg_reload_conf();
```

### Database Migrations

```bash
# Using Alembic
cd backend
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Connection Pooling

```python
# Using SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool, QueuePool

# Production configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
)
```

---

## Performance Tuning

### Backend Optimization

```python
# Gunicorn configuration (gunicorn.conf.py)
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
accesslog = "/var/log/bom-calculator/access.log"
errorlog = "/var/log/bom-calculator/error.log"
loglevel = "info"
```

### Frontend Optimization

```javascript
// vite.config.ts - Production build optimization
export default defineConfig({
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          mui: ['@mui/material'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
});
```

### Redis Caching

```python
# Cache configuration
from redis import Redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = Redis(host='localhost', port=6379, decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="bom-cache:")
```

### CDN Configuration

```nginx
# Nginx CDN cache
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=bom_cache:10m max_size=1g inactive=60m use_temp_path=off;

location /static {
    proxy_cache bom_cache;
    proxy_cache_valid 200 1y;
    proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
    proxy_cache_background_update on;
    proxy_cache_lock on;
    add_header X-Cache-Status $upstream_cache_status;
}
```

---

## Monitoring Setup

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'bom-calculator-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
      
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['localhost:9187']
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "BOM Calculator Monitoring",
    "panels": [
      {
        "title": "API Response Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### Application Logging

```python
# Structured logging
import structlog

logger = structlog.get_logger()

logger.info(
    "inventory_updated",
    part_id=part_id,
    old_quantity=old_qty,
    new_quantity=new_qty,
    user_id=user_id
)
```

### Health Checks

```python
# Health check endpoints
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/health/ready")
async def readiness():
    # Check database connection
    try:
        db.execute("SELECT 1")
        return {"status": "ready"}
    except:
        raise HTTPException(status_code=503)
```

---

## Security Hardening

### Application Security

```python
# Security headers middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["your-domain.com", "*.your-domain.com"]
)

app.add_middleware(HTTPSRedirectMiddleware)

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"]
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### Server Hardening

```bash
# Firewall configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# Fail2ban configuration
sudo apt install fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Environment Variables

```bash
# Secure environment variables
# Never commit .env files
echo ".env*" >> .gitignore

# Use secrets management
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name bom-calculator-secrets \
  --secret-string file://secrets.json

# HashiCorp Vault
vault kv put secret/bom-calculator \
  database_url="..." \
  secret_key="..."
```

---

## Backup & Recovery

### Database Backup

```bash
#!/bin/bash
# backup.sh - Daily backup script

BACKUP_DIR="/backups/bom-calculator"
DB_NAME="bom_calculator"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup application files
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz \
  /home/bomcalc/lerobot/src/lerobot/robots/bom_calculator

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/db_backup_$DATE.sql.gz \
  s3://your-backup-bucket/bom-calculator/
```

### Restore Procedure

```bash
# Restore database
gunzip < backup.sql.gz | psql bom_calculator

# Restore application files
tar -xzf app_backup.tar.gz -C /

# Restart services
sudo systemctl restart bom-calculator-api
sudo systemctl restart nginx
```

### Disaster Recovery Plan

1. **Regular Backups**
   - Database: Every 6 hours
   - Files: Daily
   - Off-site: Daily to S3/GCS

2. **Recovery Time Objectives**
   - RTO: 4 hours
   - RPO: 6 hours

3. **Testing**
   - Monthly restore tests
   - Quarterly full DR drill

---

## Scaling Strategies

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  api:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Load Balancing

```nginx
# Nginx load balancing
upstream bom_api {
    least_conn;
    server api1:8000 weight=1;
    server api2:8000 weight=1;
    server api3:8000 weight=1;
    keepalive 32;
}

server {
    location /api {
        proxy_pass http://bom_api;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

### Database Scaling

```sql
-- Read replica configuration
-- Primary database
CREATE PUBLICATION bom_publication FOR ALL TABLES;

-- Replica database
CREATE SUBSCRIPTION bom_subscription
CONNECTION 'host=primary dbname=bom_calculator'
PUBLICATION bom_publication;
```

### Caching Strategy

```python
# Multi-layer caching
from functools import lru_cache

# Application-level cache
@lru_cache(maxsize=128)
def calculate_buildable(model_id: str):
    # Expensive calculation
    pass

# Redis cache for API responses
@cache(expire=300)
async def get_inventory():
    # Database query
    pass
```

---

## Maintenance

### Update Procedures

```bash
#!/bin/bash
# update.sh - Zero-downtime update

# Pull latest code
git pull origin main

# Install dependencies
pip install -r backend/requirements.txt
npm --prefix frontend ci

# Build frontend
npm --prefix frontend run build

# Run migrations
alembic upgrade head

# Reload services (zero-downtime)
sudo systemctl reload bom-calculator-api
sudo systemctl reload nginx
```

### Monitoring Checklist

Daily:
- [ ] Check application logs
- [ ] Review error rates
- [ ] Monitor disk space
- [ ] Check backup completion

Weekly:
- [ ] Review performance metrics
- [ ] Check security logs
- [ ] Update dependencies
- [ ] Test backup restoration

Monthly:
- [ ] Security patches
- [ ] Performance analysis
- [ ] Capacity planning
- [ ] DR testing

### Troubleshooting Commands

```bash
# Check service status
systemctl status bom-calculator-api

# View logs
journalctl -u bom-calculator-api -f
tail -f /var/log/bom-calculator/error.log

# Database connections
psql -c "SELECT count(*) FROM pg_stat_activity;"

# Memory usage
free -m
ps aux | grep gunicorn

# Disk usage
df -h
du -sh /var/log/*

# Network connections
netstat -tulpn | grep :8000
ss -tulwn | grep :8000
```

---

## Appendix

### Environment Variables Reference

```bash
# Backend
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-min-32-chars
CORS_ORIGINS=["https://your-domain.com"]
DEBUG=false
LOG_LEVEL=info

# Frontend
VITE_API_URL=https://api.your-domain.com
VITE_WS_URL=wss://api.your-domain.com
VITE_ENVIRONMENT=production

# Monitoring
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
PROMETHEUS_PORT=9090
GRAFANA_ADMIN_PASSWORD=secure-password
```

### Useful Scripts

```bash
# Health check script
#!/bin/bash
curl -f http://localhost:8000/health || exit 1

# Log rotation
/var/log/bom-calculator/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 640 bomcalc bomcalc
    sharedscripts
    postrotate
        systemctl reload bom-calculator-api
    endscript
}
```

### Support Contacts

- Documentation: https://github.com/yourusername/lerobot/wiki
- Issues: https://github.com/yourusername/lerobot/issues
- Discord: https://discord.gg/lerobot
- Email: support@bomcalculator.com

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Next Review**: April 2024

For development setup, see the [Developer Guide](DEVELOPER_GUIDE.md).  
For troubleshooting, see the [Troubleshooting Guide](TROUBLESHOOTING.md).