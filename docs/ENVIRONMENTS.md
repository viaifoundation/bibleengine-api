# Environment Configuration

This document describes the environment setup for dev and production deployments.

## Environments

### Development Environment
- **Branch**: `dev`
- **Domain**: `dev.engine.bible`
- **Purpose**: Testing and development
- **Database**: Can use separate dev database or shared database with test data

### Production Environment
- **Branch**: `main`
- **Domain**: `api.engine.bible`
- **Purpose**: Live production API
- **Database**: Production database

## Environment Variables

### Development (`.env` for dev branch)

```bash
ENVIRONMENT=development
DATABASE_URL=mysql://bible:dev_password@localhost:3306/bible_dev
SECRET_KEY=dev_secret_key_change_in_production
WIKI_BASE_URL=https://bible.world
CORS_ORIGINS=*
LOG_LEVEL=DEBUG
```

### Production (`.env` for main branch)

```bash
ENVIRONMENT=production
DATABASE_URL=mysql://bible:production_password@localhost:3306/bible
SECRET_KEY=strong_production_secret_key_use_secure_random
WIKI_BASE_URL=https://bible.world
CORS_ORIGINS=https://engine.bible,https://bible.world,https://api.engine.bible
LOG_LEVEL=INFO
```

## Configuration Differences

| Setting | Development | Production |
|---------|-------------|------------|
| **API Docs** | Enabled (`/docs`, `/redoc`) | Disabled |
| **CORS** | Allow all origins (`*`) | Specific origins only |
| **Logging** | DEBUG level | INFO level |
| **Error Details** | Full stack traces | Minimal error messages |
| **Database** | Can use dev/test database | Production database only |

## Deployment Setup

### Development Server (dev.engine.bible)

1. **Checkout dev branch:**
```bash
git checkout dev
git pull origin dev
```

2. **Create development `.env` file:**
```bash
cp .env.example .env
# Edit .env with development settings
nano .env
```

3. **Set up systemd service:**
```bash
sudo nano /etc/systemd/system/bibleengine-api-dev.service
```

Content:
```ini
[Unit]
Description=BibleEngine API (Development)
After=network.target mariadb.service

[Service]
User=mhuo
WorkingDirectory=/home/mhuo/bibleengine-api
Environment="PATH=/home/mhuo/bibleengine-api/venv/bin"
EnvironmentFile=/home/mhuo/bibleengine-api/.env
ExecStart=/home/mhuo/bibleengine-api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

4. **Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable bibleengine-api-dev
sudo systemctl start bibleengine-api-dev
```

### Production Server (api.engine.bible)

1. **Checkout main branch:**
```bash
git checkout main
git pull origin main
```

2. **Create production `.env` file:**
```bash
cp .env.example .env
# Edit .env with production settings
nano .env
```

3. **Set up systemd service:**
```bash
sudo nano /etc/systemd/system/bibleengine-api.service
```

Content:
```ini
[Unit]
Description=BibleEngine API (Production)
After=network.target mariadb.service

[Service]
User=mhuo
WorkingDirectory=/home/mhuo/bibleengine-api
Environment="PATH=/home/mhuo/bibleengine-api/venv/bin"
EnvironmentFile=/home/mhuo/bibleengine-api/.env
ExecStart=/home/mhuo/bibleengine-api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

4. **Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable bibleengine-api
sudo systemctl start bibleengine-api
```

## Nginx Configuration

### Development (dev.engine.bible)

```nginx
server {
    listen 80;
    server_name dev.engine.bible;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Production (api.engine.bible)

```nginx
server {
    listen 80;
    server_name api.engine.bible;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Database Setup

### Development Database

You can use a separate database for development:

```sql
CREATE DATABASE bible_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bible_dev'@'localhost' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON bible_dev.* TO 'bible_dev'@'localhost';
FLUSH PRIVILEGES;
```

### Production Database

Use the main production database:

```sql
CREATE DATABASE bible CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bible'@'localhost' IDENTIFIED BY 'production_password';
GRANT ALL PRIVILEGES ON bible.* TO 'bible'@'localhost';
FLUSH PRIVILEGES;
```

## Deployment Workflow

### Development Deployment

1. Make changes on `dev` branch
2. Test locally
3. Push to `dev` branch
4. Deploy to dev.engine.bible:
```bash
cd /home/mhuo/bibleengine-api
git checkout dev
git pull origin dev
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart bibleengine-api-dev
```

### Production Deployment

1. Merge `dev` into `main` branch
2. Tag release (optional)
3. Deploy to api.engine.bible:
```bash
cd /home/mhuo/bibleengine-api
git checkout main
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart bibleengine-api
```

## Security Considerations

### Development
- API documentation enabled for easier testing
- More verbose logging
- Can use weaker secrets (but still use different ones)
- CORS allows all origins

### Production
- API documentation disabled
- Minimal logging
- Strong, unique secrets
- CORS restricted to specific domains
- SSL/TLS required
- Rate limiting recommended

## Monitoring

### Development
- Check logs: `sudo journalctl -u bibleengine-api-dev -f`
- Monitor on port 8001

### Production
- Check logs: `sudo journalctl -u bibleengine-api -f`
- Monitor on port 8000
- Set up monitoring/alerting (e.g., Prometheus, Grafana)

## Troubleshooting

### Check Environment
```bash
# Check which environment is active
grep ENVIRONMENT /home/mhuo/bibleengine-api/.env

# Check service status
sudo systemctl status bibleengine-api-dev  # Development
sudo systemctl status bibleengine-api      # Production
```

### Switch Between Environments
```bash
# Switch to dev
git checkout dev
# Update .env file
sudo systemctl restart bibleengine-api-dev

# Switch to production
git checkout main
# Update .env file
sudo systemctl restart bibleengine-api
```

