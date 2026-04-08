---
name: devops
description: Use when setting up deployment, CI/CD, Docker, or infrastructure -- covers solo-dev deployment patterns, GitHub Actions, Docker best practices, SSL, environment management, and rollback procedures
allowed-tools: Read Write Edit Bash(docker *) Bash(git *) Bash(npm *) Glob Grep
---

# DevOps

When helping with deployment, CI/CD, Docker, or infrastructure, follow these solo-dev ops patterns. This is practical ops for small teams and individual developers -- not enterprise Kubernetes clusters. The goal is to make deployments boring and reliable.

## Core Principles

1. **Automate what you do twice.** First time, do it manually and take notes. Second time, write the script. Third time should be `./deploy.sh` and walk away.

2. **Reproducible environments.** If it works on your machine, it must work on the server. Docker for isolation. `.env` files for config. Never install packages globally on the server when a container will do.

3. **Fail loudly, recover quietly.** Every deployment should scream if something goes wrong (alerts, logs, non-zero exit codes). Recovery should be automatic where possible (health checks, restart policies, rollback triggers).

4. **Secrets never touch git.** API keys in `.env`, loaded at runtime. Docker secrets or environment variables in CI. If you see a secret in a committed file, rotate it immediately -- it's already compromised.

5. **Logs are your debugger.** You can't SSH into production and attach a debugger. Structured logging (JSON), log levels, and centralized collection are how you diagnose issues at 2 AM.

6. **Small, frequent deploys.** One feature per deploy. If something breaks, you know exactly what caused it. "We deployed 47 changes and something broke" is a nightmare.

7. **Backups are only real if tested.** A backup you haven't restored is a hope, not a backup. Test restoration quarterly at minimum.

## Step-by-Step Processes

### Setting Up a New Service

```
1. Write the application code (separate concern)
2. Create Dockerfile (or docker-compose.yml for multi-service)
3. Create .env.example with all required variables
4. Build and test locally: docker compose up --build
5. Set up GitHub repo + Actions workflow
6. Configure hosting (VPS, Render, Fly.io, etc.)
7. Set environment variables on the host
8. Deploy and verify health endpoint returns 200
9. Set up domain + SSL (if applicable)
10. Configure monitoring / uptime checks
```

### Deploying an Update

```
1. Push to main (or merge PR)
2. CI runs: lint -> test -> build -> deploy
3. Health check confirms new version is up
4. If health check fails: auto-rollback to previous version
5. Monitor logs for 15 minutes after deploy
```

## Common Patterns

### Dockerfile (Python/FastAPI)

```dockerfile
FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose (Multi-Service Local Dev)

```yaml
version: "3.8"

services:
  server:
    build: ./apps/server
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./apps/server:/app    # Hot reload in dev
    restart: unless-stopped
    depends_on:
      - redis

  web:
    build: ./apps/web
    ports:
      - "3000:3000"
    env_file: .env
    depends_on:
      - server

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### GitHub Actions (CI/CD)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install deps
        run: pip install -r requirements.txt

      - name: Lint
        run: |
          pip install ruff
          ruff check .

      - name: Test
        run: python -m pytest tests/ -v
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Option A: SSH to VPS
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/myapp
            git pull origin main
            docker compose up -d --build
            docker compose exec server python -c "print('OK')"

      - name: Health check
        run: |
          sleep 30
          curl -f https://myapp.example.com/health || exit 1
```

### Deployment Script (VPS / Self-Hosted)

```bash
#!/bin/bash
# deploy.sh -- Run on the server, not locally
set -euo pipefail

APP_DIR="/opt/myapp"
BACKUP_DIR="/opt/myapp-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=== Deploying at $TIMESTAMP ==="

# Backup current version
echo "Backing up..."
mkdir -p "$BACKUP_DIR"
cp -r "$APP_DIR" "$BACKUP_DIR/app_$TIMESTAMP"

# Pull latest code
echo "Pulling latest..."
cd "$APP_DIR"
git fetch origin main
git reset --hard origin/main

# Rebuild and restart
echo "Rebuilding..."
docker compose build --no-cache
docker compose down
docker compose up -d

# Wait for health check
echo "Checking health..."
for i in {1..10}; do
    if curl -sf http://localhost:8000/health > /dev/null; then
        echo "Health check passed!"
        exit 0
    fi
    echo "Attempt $i/10 -- waiting 5s..."
    sleep 5
done

# Rollback on failure
echo "HEALTH CHECK FAILED -- Rolling back!"
docker compose down
cp -r "$BACKUP_DIR/app_$TIMESTAMP"/* "$APP_DIR/"
docker compose up -d
echo "Rolled back to previous version"
exit 1
```

### SSL + Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name app.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/app.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # API server
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Web frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# SSL setup with Let's Encrypt (one-time)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d app.yourdomain.com
# Auto-renewal is configured automatically by certbot
# Verify: sudo certbot renew --dry-run
```

### Environment Management

```bash
# .env.example -- committed to git, documents all variables
# .env -- NEVER committed, contains actual secrets

# Pattern for loading env vars in Python:
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Required -- crash at startup if missing
    DATABASE_URL = os.environ["DATABASE_URL"]
    API_SECRET = os.environ["API_SECRET"]

    # Optional -- defaults provided
    PORT = int(os.getenv("PORT", "8000"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Feature flags
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
```

### Structured Logging

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        })
```

### Health Endpoint

```python
from datetime import datetime

START_TIME = datetime.utcnow()

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": os.getenv("GIT_SHA", "dev"),
        "uptime_seconds": (datetime.utcnow() - START_TIME).total_seconds(),
        "checks": {
            "database": await check_db(),
            "redis": await check_redis(),
        }
    }
```

### Quick Log Analysis Commands

```bash
# Find errors in last hour
docker logs myapp-server --since 1h 2>&1 | grep -i error

# Count requests by endpoint
docker logs myapp-server --since 24h 2>&1 | grep "POST\|GET" | awk '{print $7}' | sort | uniq -c | sort -rn

# Monitor in real-time
docker logs -f myapp-server 2>&1 | grep --line-buffered -E "ERROR|WARN"
```

## Edge Cases and Pitfalls

**Docker build cache invalidation**
- Changing ANY file before `pip install` invalidates the pip cache layer
- Always `COPY requirements.txt .` and `RUN pip install` BEFORE `COPY . .`
- Saves minutes on every build

**Port conflicts**
- `EADDRINUSE` means something else is on that port
- Check: `lsof -i :8000` (Linux/Mac) or `netstat -ano | findstr :8000` (Windows)
- Docker: map to a different host port: `"8001:8000"`

**Disk space on servers**
- Docker images accumulate fast: `docker system prune -a` reclaims space
- Old log files: configure rotation (`--log-opt max-size=10m --log-opt max-file=3`)
- Old backups: keep last 5, delete older ones in deploy script

**DNS propagation**
- DNS changes take 5 minutes to 48 hours to propagate globally
- TTL (Time To Live) controls cache duration -- set to 300 (5 min) before migration
- Check propagation: `dig yourdomain.com @8.8.8.8` or dnschecker.org

**SSL certificate renewal failures**
- Let's Encrypt certs expire every 90 days
- Certbot auto-renewal can fail if Nginx config changes or port 80 is blocked
- Check: `sudo certbot renew --dry-run` monthly
- Alert if cert expires in <14 days: check with `openssl s_client -connect domain:443`

**Environment variable gotchas**
- Docker Compose `.env` is loaded from the directory where you run `docker compose`
- `env_file` in compose uses the file path relative to the compose file
- Shell variables override `.env` file values -- can cause "works on my machine" issues
- Boolean env vars are strings: `"true"` not `True` -- always parse explicitly

**Container timezone issues**
- Alpine/slim containers default to UTC
- If your app expects local time: set `TZ` env var or `ENV TZ=America/New_York` in Dockerfile
- Better practice: use UTC everywhere, convert to local only in the UI

## Quality Checklist

Before marking a deployment task as done:

- [ ] Service starts without errors (`docker compose up` shows no crash loops)
- [ ] Health endpoint returns 200 with all checks passing
- [ ] All environment variables set (compare `.env.example` against actual `.env`)
- [ ] No secrets in committed files (grep for `sk-`, `key=`, passwords in repo)
- [ ] SSL certificate valid and auto-renewal configured
- [ ] Logs are accessible (`docker logs` works, or centralized logging is set up)
- [ ] Restart policy configured (`restart: unless-stopped` or equivalent)
- [ ] Rollback procedure tested (you've actually done it, not just written the script)
- [ ] Firewall rules correct (only needed ports exposed: 80, 443, maybe SSH)
- [ ] Backups configured and tested (database, .env, any persistent data)
- [ ] Monitoring/uptime check active (alerts go somewhere a human will see them)
- [ ] Documentation updated (how to deploy, how to rollback, where logs are)
