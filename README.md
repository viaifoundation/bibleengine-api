# BibleEngine API

BibleEngine API is the next-generation backend powering the Goshen Bible Engine at `https://engine.bible` and `https://bible.world`.

Built with **Python**, **FastAPI**, and **PostgreSQL**, it provides a high-performance, scalable RESTful API for Bible verse search, multi-translation access, wiki integration, and user interaction features (e.g., verse likes).

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
- **Scalable & Modern**: Async FastAPI backend with PostgreSQL for reliability and performance.

## API Endpoints (v1)

- `GET /v1/api/search` – Search verses
- `GET /v1/api/wiki` – Search bible.world MediaWiki
- `POST /v1/api/like` – Like a verse

See interactive Swagger docs at `/docs` when running locally.

## Setup (Ubuntu 24.04 LTS)

This guide covers the complete setup for the BibleEngine API backend on a fresh Ubuntu 24.04 LTS server.

#### 1. System Update and Basic Tools
`sudo apt update && sudo apt upgrade -y`
`sudo apt install -y python3 python3-venv python3-pip git curl postgresql postgresql-contrib ufw`

#### 2. Create Project Directory and Clone Repository
`mkdir -p /home/mhuo/bibleengine-api`
`cd /home/mhuo/bibleengine-api`
`git clone https://github.com/viaifoundation/bibleengine-api.git .`

#### 3. Set Up Python Virtual Environment
`python3 -m venv venv`
`source venv/bin/activate`
`pip install --upgrade pip`
`pip install fastapi uvicorn psycopg2-binary python-dotenv`

#### 4. Configure PostgreSQL
`sudo -u postgres psql`

In psql:
`CREATE DATABASE bible;`
`CREATE USER bible WITH PASSWORD 'your_strong_password';`
`ALTER ROLE bible SET client_encoding TO 'utf8';`
`ALTER ROLE bible SET default_transaction_isolation TO 'read committed';`
`ALTER ROLE bible SET timezone TO 'UTC';`
`GRANT ALL PRIVILEGES ON DATABASE bible TO bible;`
`\q`

#### 5. Create Environment File
Create a `.env` file in the project root:
`nano .env`

Example `.env` content:
```
ENVIRONMENT=production
DATABASE_URL=postgresql://bible:your_strong_password@localhost/bible
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
- FastAPI, PostgreSQL, and Python communities