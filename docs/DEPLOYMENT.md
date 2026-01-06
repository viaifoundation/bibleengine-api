# Deployment Guide

This guide covers deploying the BibleEngine API to production.

## Prerequisites

- Ubuntu 24.04 LTS (or similar Linux distribution)
- Python 3.10+
- MariaDB 10.5+ or MySQL 8.0+
- Systemd (for service management)
- Nginx or Apache (for reverse proxy)

## Step 1: Server Setup

### Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Install Dependencies
```bash
sudo apt install -y python3 python3-venv python3-pip git curl mariadb-server mariadb-client ufw
```

## Step 2: Database Setup

### MariaDB Installation

```bash
# Start and enable MariaDB
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Run secure installation (optional but recommended)
sudo mysql_secure_installation
```

### Create Database and User

```bash
sudo mysql -u root -p
```

In MariaDB/MySQL:
```sql
CREATE DATABASE bible CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bible'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON bible.* TO 'bible'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Import Existing Database (if migrating)

If you have an existing MariaDB/MySQL dump:

```bash
# Import database dump
mysql -u bible -p bible < bible_backup.sql
```

Or if you need to import from another server:
```bash
mysqldump -u username -p -h source-host bible | mysql -u bible -p bible
```

## Step 3: Application Setup

### Clone Repository
```bash
cd /home/mhuo
git clone https://github.com/viaifoundation/bibleengine-api.git
cd bibleengine-api
```

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Configure Environment
```bash
cp .env.example .env
nano .env
```

Set the following:
```
ENVIRONMENT=production
DATABASE_URL=mysql://bible:your_strong_password@localhost:3306/bible
SECRET_KEY=your_random_secret_key_here
WIKI_BASE_URL=https://bible.world
```

### Test Application
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Visit `http://your-server-ip:8000/docs` to verify.

## Step 4: Systemd Service

### Create Service File
```bash
sudo nano /etc/systemd/system/bibleengine-api.service
```

Content:
```ini
[Unit]
Description=BibleEngine API
After=network.target mariadb.service

[Service]
User=mhuo
Group=mhuo
WorkingDirectory=/home/mhuo/bibleengine-api
Environment="PATH=/home/mhuo/bibleengine-api/venv/bin"
ExecStart=/home/mhuo/bibleengine-api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable bibleengine-api
sudo systemctl start bibleengine-api
sudo systemctl status bibleengine-api
```

## Step 5: Reverse Proxy (Nginx)

### Install Nginx
```bash
sudo apt install -y nginx
```

### Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/bibleengine-api
```

Content:
```nginx
server {
    listen 80;
    server_name api.bible.world;  # Change to your domain

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/bibleengine-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 6: SSL Certificate (Let's Encrypt)

### Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtain Certificate
```bash
sudo certbot --nginx -d api.bible.world
```

Follow the prompts to complete SSL setup.

## Step 7: Firewall Configuration

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo ufw status
```

## Step 8: Monitoring and Logs

### View Application Logs
```bash
sudo journalctl -u bibleengine-api -f
```

### View Nginx Logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Set Up Log Rotation
Create log rotation config:
```bash
sudo nano /etc/logrotate.d/bibleengine-api
```

Content:
```
/home/mhuo/bibleengine-api/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 mhuo mhuo
    sharedscripts
}
```

## Step 9: Performance Tuning

### MariaDB Tuning
Edit `/etc/mysql/mariadb.conf.d/50-server.cnf`:
```ini
[mysqld]
max_connections = 100
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
query_cache_type = 1
query_cache_size = 64M
tmp_table_size = 64M
max_heap_table_size = 64M
```

Restart MariaDB:
```bash
sudo systemctl restart mariadb
```

### Application Tuning
Adjust worker processes in systemd service:
```ini
ExecStart=/home/mhuo/bibleengine-api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Step 10: Backup Strategy

### Database Backup
Create backup script:
```bash
sudo nano /usr/local/bin/backup-bible-db.sh
```

Content:
```bash
#!/bin/bash
BACKUP_DIR="/backups/bible"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
mysqldump -u bible -p'your_password' bible > $BACKUP_DIR/bible_$DATE.sql
# Keep only last 30 days
find $BACKUP_DIR -name "bible_*.sql" -mtime +30 -delete
```

Make executable:
```bash
sudo chmod +x /usr/local/bin/backup-bible-db.sh
```

Add to crontab:
```bash
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-bible-db.sh
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
sudo journalctl -u bibleengine-api -n 50

# Check database connection
psql -U bible -d bible -c "SELECT 1;"

# Verify environment variables
sudo -u mhuo cat /home/mhuo/bibleengine-api/.env
```

### Database Connection Issues
```bash
# Test connection
mysql -u bible -p bible

# Check MariaDB status
sudo systemctl status mariadb

# Check MariaDB error log
sudo tail -f /var/log/mysql/error.log

# Check firewall
sudo ufw status
```

### High Memory Usage
- Reduce number of workers
- Optimize database queries
- Add caching (Redis)

## Security Considerations

1. **Environment Variables:** Never commit `.env` file
2. **Database Passwords:** Use strong, unique passwords
3. **Firewall:** Only open necessary ports
4. **SSL/TLS:** Always use HTTPS in production
5. **Updates:** Regularly update system and dependencies
6. **Monitoring:** Set up monitoring and alerting

## Maintenance

### Update Application
```bash
cd /home/mhuo/bibleengine-api
source venv/bin/activate
git pull
pip install -r requirements.txt
sudo systemctl restart bibleengine-api
```

### Database Maintenance
```bash
# Optimize tables
mysql -u bible -p bible -e "OPTIMIZE TABLE bible_books, bible_search, bible_multi_search;"

# Check database size
mysql -u bible -p bible -e "SELECT table_schema AS 'Database', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' FROM information_schema.tables WHERE table_schema = 'bible' GROUP BY table_schema;"

# Analyze tables for query optimization
mysql -u bible -p bible -e "ANALYZE TABLE bible_books, bible_search;"
```

## Support

For issues or questions:
- GitHub Issues: `https://github.com/viaifoundation/bibleengine-api/issues`
- Documentation: See `docs/` folder

