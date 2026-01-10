# BibleEngine API

BibleEngine API is the next-generation backend powering the Goshen Bible Engine at `https://engine.bible` and `https://bible.world`.

Built with **Python**, **FastAPI**, and **MariaDB/MySQL**, it provides a high-performance, scalable RESTful API for Bible verse search, multi-translation access, wiki integration, and user interaction features (e.g., verse likes).

This project is fully decoupled from the legacy PHP implementation and the bible.world MediaWiki frontend, enabling independent development and deployment.

## Features

- **Verse Search**: Query by reference (e.g., `John 3:16`) or keywords, with support for single/multi-verse and context extension (±n verses).
- **Multi-Language & Translation Support**:
  - Hosted (public domain): CUVS, CUVT, KJV, Pinyin
  - Authorized: NASB (with permission from The Lockman Foundation)
  - External links: ESV, NCVS, LCVS, CCSB, CLBS, CKJVS, CKJVT, UKJV, KJV1611, BBE
- **Wiki Integration**: Fetch rich contextual content (commentaries, encyclopedia entries) from bible.world MediaWiki.
- **Like Functionality**: Increment and retrieve "likes" for verses.
- **Versioned Endpoints**: `/v1/api/...` for future-proofing and backward compatibility.
- **Scalable & Modern**: Async FastAPI backend with MariaDB/MySQL for reliability and performance.

## API Endpoints (v1)

- `GET /v1/api/search` – Search verses
- `GET /v1/api/wiki` – Search bible.world MediaWiki
- `POST /v1/api/like` – Like a verse

See interactive Swagger docs at `/docs` when running locally.

## Setup (Ubuntu 24.04 LTS)

This guide covers the complete setup for the BibleEngine API backend on a fresh Ubuntu 24.04 LTS server.

#### 1. System Update and Basic Tools
`sudo apt update && sudo apt upgrade -y`
`sudo apt install -y python3 python3-venv python3-pip git curl mariadb-server mariadb-client ufw`

#### 2. Create Project Directory and Clone Repository
`mkdir -p /home/mhuo/bibleengine-api`
`cd /home/mhuo/bibleengine-api`
`git clone https://github.com/viaifoundation/bibleengine-api.git .`

#### 3. Set Up Python Virtual Environment
`python3 -m venv venv`
`source venv/bin/activate`
`pip install --upgrade pip`
`pip install -r requirements.txt`

#### 4. Configure MariaDB
`sudo systemctl start mariadb`
`sudo systemctl enable mariadb`
`sudo mysql_secure_installation`

Then create database and user:
`sudo mysql -u root -p`

In MySQL:
```sql
CREATE DATABASE bible CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bible'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON bible.* TO 'bible'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 5. Create Environment File
Create a `.env` file in the project root:
`nano .env`

Example `.env` content:
```
ENVIRONMENT=production
DATABASE_URL=mysql://bible:your_strong_password@localhost:3306/bible
SECRET_KEY=your_random_secret_key_here
WIKI_BASE_URL=https://bible.world
```

**Note:** Make sure to replace `your_strong_password` and `your_random_secret_key_here` with actual values.

#### 6. Test Local Run
`uvicorn main:app --reload --host 0.0.0.0 --port 8000`

Visit `http://your_server_ip:8000/docs` to see the interactive API documentation.

#### 7. Set Up Systemd Service (Production)
`sudo nano /etc/systemd/system/bibleengine-api.service`

Content:
```
[Unit]
Description=BibleEngine API
After=network.target

[Service]
User=mhuo
WorkingDirectory=/home/mhuo/bibleengine-api
Environment="PATH=/home/mhuo/bibleengine-api/venv/bin"
ExecStart=/home/mhuo/bibleengine-api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start:
`sudo systemctl daemon-reload`
`sudo systemctl enable bibleengine-api`
`sudo systemctl start bibleengine-api`
`sudo systemctl status bibleengine-api`

#### 8. Basic Security (UFW Firewall)
`sudo ufw allow OpenSSH`
`sudo ufw allow 80/tcp`
`sudo ufw allow 443/tcp`
`sudo ufw --force enable`

#### 9. Apache Reverse Proxy (Optional but Recommended)
Configure Apache to proxy to FastAPI and handle SSL termination (see separate Apache config guide).

Your BibleEngine API backend is now ready on Ubuntu 24.04 LTS!

## Database Migration Tools

The `utils/` folder contains migration tools to replicate the MySQL database to PostgreSQL or SQLite.

### Prerequisites

```bash
# For PostgreSQL migration
pip install pymysql psycopg2-binary

# For SQLite migration
pip install pymysql
```

### Migrate to PostgreSQL

```bash
# Show help
python3 utils/migrate_to_postgresql.py --help

# Basic usage with credentials
python3 utils/migrate_to_postgresql.py \
    --mysql-password <mysql_pwd> \
    --pg-password <pg_pwd>

# Full configuration
python3 utils/migrate_to_postgresql.py \
    --mysql-host localhost --mysql-user root --mysql-password secret \
    --pg-host localhost --pg-user postgres --pg-password secret \
    --pg-database bible

# Dry run (preview without changes)
python3 utils/migrate_to_postgresql.py --dry-run

# Using environment variables
export MYSQL_PASSWORD=secret
export PG_PASSWORD=secret
python3 utils/migrate_to_postgresql.py
```

**Features:**
- Automatic PostgreSQL database creation
- GIN indexes with tsvector for full-text search
- Batch inserts for performance
- Upsert support (ON CONFLICT)

### Migrate to SQLite

```bash
# Show help
python3 utils/migrate_to_sqlite.py --help

# Basic usage
python3 utils/migrate_to_sqlite.py \
    --mysql-password <mysql_pwd> \
    --sqlite-path /var/lib/bibleengine/bible.db

# Skip FTS for faster migration
python3 utils/migrate_to_sqlite.py --skip-fts

# Dry run
python3 utils/migrate_to_sqlite.py --dry-run
```

**Features:**
- Single portable SQLite file
- FTS5 full-text search with auto-sync triggers
- WAL mode for concurrent access
- VACUUM and ANALYZE optimization

### Common Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview migration without changes |
| `--batch-size N` | Batch size for inserts (default: 1000) |
| `--skip-translations` | Skip translation tables |
| `--tables TABLE...` | Migrate specific tables only |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `MYSQL_HOST` | MySQL hostname |
| `MYSQL_PORT` | MySQL port (default: 3306) |
| `MYSQL_USER` | MySQL username |
| `MYSQL_PASSWORD` | MySQL password |
| `MYSQL_DATABASE` | MySQL database (default: bible) |
| `PG_HOST` | PostgreSQL hostname |
| `PG_PORT` | PostgreSQL port (default: 5432) |
| `PG_USER` | PostgreSQL username |
| `PG_PASSWORD` | PostgreSQL password |
| `PG_DATABASE` | PostgreSQL database (default: bible) |
| `SQLITE_PATH` | SQLite database file path |

## Documentation

Comprehensive documentation is available in the [`docs/`](docs/) folder:

- **[Database Schema](docs/DATABASE_SCHEMA.md)** - Complete database schema documentation
- **[API Reference](docs/API_REFERENCE.md)** - API endpoint documentation
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Environment Configuration](docs/ENVIRONMENTS.md)** - Dev and production environment setup

## License

See [LICENSE](LICENSE) for details.

This project is licensed under a proprietary license with doctrinal and usage restrictions. See the full license text for authorized use conditions.

Bible text data includes public domain translations (CUVS, CUVT, KJV, Pinyin) and NASB used with permission from The Lockman Foundation.

## Contributing
  
Contributions require explicit authorization from VI AI Foundation. Please open an issue at `https://github.com/viaifoundation/bibleengine-api/issues` to request permission.

The foundation reserves the right to deny contributions from entities whose beliefs conflict with orthodox Christian doctrine.

## Contact

For authorization or support: `https://github.com/viaifoundation/bibleengine-api/issues`

## Acknowledgements

- The Lockman Foundation for NASB permission
- bible.world MediaWiki community for content integration
- FastAPI, MariaDB, and Python communities