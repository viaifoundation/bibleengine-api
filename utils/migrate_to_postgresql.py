#!/usr/bin/env python3
"""
MySQL to PostgreSQL Migration Script for BibleEngine Database

This script migrates all tables and data from MySQL to PostgreSQL.
Designed for Ubuntu 24.04 VPS.

Requirements:
    pip install pymysql psycopg2-binary

Usage:
    python3 migrate_to_postgresql.py --help
    python3 migrate_to_postgresql.py --mysql-host localhost --mysql-user root --mysql-password secret
    python3 migrate_to_postgresql.py --pg-host localhost --pg-user postgres --pg-password secret
"""

import argparse
import os
import sys
from typing import List, Tuple

# ============================================================================
# TRANSLATION TABLES - All bible_book_{translation} tables
# ============================================================================

TRANSLATION_TABLES = [
    'bible_book_cuvs',
    'bible_book_cuvt',
    'bible_book_cuvc',
    'bible_book_kjv',
    'bible_book_kjv1611',
    'bible_book_nasb',
    'bible_book_esv',
    'bible_book_pinyin',
    'bible_book_ncvs',
    'bible_book_lcvs',
    'bible_book_ccsb',
    'bible_book_clbs',
    'bible_book_ckjvs',
    'bible_book_ckjvt',
    'bible_book_ukjv',
    'bible_book_tcvs',
    'bible_book_tr',
    'bible_book_wlc',
    'bible_book_bbe',
    'bible_book_nstrunv',
]

# ============================================================================
# SCHEMA DEFINITIONS
# ============================================================================

SCHEMA_BIBLE_BOOK = """
CREATE TABLE IF NOT EXISTS bible_book (
    id       INTEGER      NOT NULL PRIMARY KEY DEFAULT 0,
    en       VARCHAR(8)   NOT NULL,
    english  VARCHAR(20),
    english2 VARCHAR(20),
    en1      VARCHAR(8),
    en2      VARCHAR(8),
    en3      VARCHAR(8),
    short    VARCHAR(8),
    chinese  VARCHAR(32),
    cn       VARCHAR(10),
    taiwan   VARCHAR(32),
    tw       VARCHAR(10),
    abbr     VARCHAR(32),
    count    INTEGER      DEFAULT 0,
    "offset" INTEGER      NOT NULL DEFAULT 0
);
"""

SCHEMA_BIBLE_BOOKS = """
CREATE TABLE IF NOT EXISTS bible_books (
    id       INTEGER,
    book     INTEGER      NOT NULL,
    chapter  INTEGER      NOT NULL,
    verse    INTEGER      NOT NULL,
    txt_tw   TEXT,
    txt_cn   TEXT,
    txt_en   TEXT,
    txt_py   TEXT,
    short    VARCHAR(8)   NOT NULL,
    updated  DATE,
    reported DATE,
    likes    INTEGER      NOT NULL DEFAULT 0,
    PRIMARY KEY (book, chapter, verse)
);

-- Create full-text search index using tsvector
CREATE INDEX IF NOT EXISTS idx_bible_books_txt_tw_fts
ON bible_books USING gin(to_tsvector('simple', COALESCE(txt_tw, '')));
"""

SCHEMA_BIBLE_SEARCH = """
CREATE TABLE IF NOT EXISTS bible_search (
    book    SMALLINT     NOT NULL,
    chapter SMALLINT     NOT NULL,
    verse   SMALLINT     NOT NULL,
    txt     TEXT         NOT NULL,
    PRIMARY KEY (book, chapter, verse)
);

-- Create full-text search index
CREATE INDEX IF NOT EXISTS idx_bible_search_txt_fts
ON bible_search USING gin(to_tsvector('simple', txt));
"""

SCHEMA_BIBLE_MULTI_SEARCH = """
CREATE TABLE IF NOT EXISTS bible_multi_search (
    book    SMALLINT     NOT NULL,
    chapter SMALLINT     NOT NULL,
    verse   SMALLINT     NOT NULL,
    txt     TEXT         NOT NULL,
    PRIMARY KEY (book, chapter, verse)
);

-- Create full-text search index
CREATE INDEX IF NOT EXISTS idx_bible_multi_search_txt_fts
ON bible_multi_search USING gin(to_tsvector('simple', txt));
"""

# Template for translation tables (Book, Chapter, Verse capitalized as in MySQL)
SCHEMA_TRANSLATION_TABLE = """
CREATE TABLE IF NOT EXISTS {table_name} (
    "Book"      INTEGER  NOT NULL,
    "Chapter"   INTEGER  NOT NULL,
    "Verse"     INTEGER  NOT NULL,
    "Scripture" TEXT,
    PRIMARY KEY ("Book", "Chapter", "Verse")
);
"""

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Migrate BibleEngine database from MySQL to PostgreSQL.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Use default settings (localhost, default ports)
  python3 %(prog)s

  # Specify MySQL credentials
  python3 %(prog)s --mysql-user bible --mysql-password secret123

  # Specify PostgreSQL credentials
  python3 %(prog)s --pg-user postgres --pg-password secret123

  # Full custom configuration
  python3 %(prog)s \\
      --mysql-host 10.0.0.1 --mysql-port 3306 \\
      --mysql-user bible --mysql-password mysqlpass \\
      --mysql-database bible \\
      --pg-host 10.0.0.2 --pg-port 5432 \\
      --pg-user postgres --pg-password pgpass \\
      --pg-database bible

  # Use environment variables
  export MYSQL_PASSWORD=secret
  export PG_PASSWORD=secret
  python3 %(prog)s

  # Dry run (show what would be migrated)
  python3 %(prog)s --dry-run

  # Custom batch size for large datasets
  python3 %(prog)s --batch-size 5000

Tables Migrated:
  - bible_book        : Book metadata (66 books)
  - bible_books       : Main verses table with likes
  - bible_search      : Full-text search index
  - bible_multi_search: Multi-language search index
  - bible_book_*      : 20+ translation tables (KJV, CUVS, etc.)
'''
    )

    # MySQL connection options
    mysql_group = parser.add_argument_group('MySQL Connection Options')
    mysql_group.add_argument(
        '--mysql-host',
        default=os.environ.get('MYSQL_HOST', 'localhost'),
        help='MySQL host (default: localhost, env: MYSQL_HOST)'
    )
    mysql_group.add_argument(
        '--mysql-port',
        type=int,
        default=int(os.environ.get('MYSQL_PORT', 3306)),
        help='MySQL port (default: 3306, env: MYSQL_PORT)'
    )
    mysql_group.add_argument(
        '--mysql-user',
        default=os.environ.get('MYSQL_USER', 'root'),
        help='MySQL username (default: root, env: MYSQL_USER)'
    )
    mysql_group.add_argument(
        '--mysql-password',
        default=os.environ.get('MYSQL_PASSWORD', ''),
        help='MySQL password (env: MYSQL_PASSWORD)'
    )
    mysql_group.add_argument(
        '--mysql-database',
        default=os.environ.get('MYSQL_DATABASE', 'bible'),
        help='MySQL database name (default: bible, env: MYSQL_DATABASE)'
    )

    # PostgreSQL connection options
    pg_group = parser.add_argument_group('PostgreSQL Connection Options')
    pg_group.add_argument(
        '--pg-host',
        default=os.environ.get('PG_HOST', 'localhost'),
        help='PostgreSQL host (default: localhost, env: PG_HOST)'
    )
    pg_group.add_argument(
        '--pg-port',
        type=int,
        default=int(os.environ.get('PG_PORT', 5432)),
        help='PostgreSQL port (default: 5432, env: PG_PORT)'
    )
    pg_group.add_argument(
        '--pg-user',
        default=os.environ.get('PG_USER', 'postgres'),
        help='PostgreSQL username (default: postgres, env: PG_USER)'
    )
    pg_group.add_argument(
        '--pg-password',
        default=os.environ.get('PG_PASSWORD', ''),
        help='PostgreSQL password (env: PG_PASSWORD)'
    )
    pg_group.add_argument(
        '--pg-database',
        default=os.environ.get('PG_DATABASE', 'bible'),
        help='PostgreSQL database name (default: bible, env: PG_DATABASE)'
    )

    # Migration options
    migration_group = parser.add_argument_group('Migration Options')
    migration_group.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Batch size for bulk inserts (default: 1000)'
    )
    migration_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be migrated without making changes'
    )
    migration_group.add_argument(
        '--skip-translations',
        action='store_true',
        help='Skip translation tables (bible_book_*)'
    )
    migration_group.add_argument(
        '--tables',
        nargs='+',
        help='Migrate only specific tables (space-separated list)'
    )

    return parser.parse_args()


def print_help():
    """Print detailed help information."""
    help_text = """
================================================================================
             BibleEngine MySQL to PostgreSQL Migration Tool
================================================================================

DESCRIPTION:
    This tool migrates the BibleEngine database from MySQL/MariaDB to PostgreSQL.
    It creates the schema, transfers all data, and sets up full-text search indexes.

REQUIREMENTS:
    pip install pymysql psycopg2-binary

QUICK START:
    1. Ensure MySQL source database is accessible
    2. Ensure PostgreSQL is installed and running
    3. Run: python3 migrate_to_postgresql.py --mysql-password <pwd> --pg-password <pwd>

FEATURES:
    - Automatic database creation in PostgreSQL
    - Full-text search using GIN indexes with tsvector
    - Batch inserts for performance
    - Upsert support (ON CONFLICT)
    - Environment variable support for credentials

DATABASE SCHEMA:
    Core Tables:
        bible_book         - Book metadata (id, names in EN/CN/TW)
        bible_books        - Main verses with likes count
        bible_search       - Full-text search index
        bible_multi_search - Multi-language search

    Translation Tables (20+):
        bible_book_kjv, bible_book_cuvs, bible_book_cuvt, etc.

ENVIRONMENT VARIABLES:
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
    PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DATABASE

For full options, run: python3 migrate_to_postgresql.py --help
================================================================================
"""
    print(help_text)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_mysql_connection(config: dict):
    """Create MySQL connection."""
    import pymysql
    return pymysql.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database'],
        charset='utf8mb4'
    )


def get_postgres_connection(config: dict):
    """Create PostgreSQL connection."""
    import psycopg2
    return psycopg2.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )


def create_database_if_not_exists(config: dict):
    """Create PostgreSQL database if it doesn't exist."""
    import psycopg2
    from psycopg2 import sql

    conn_config = config.copy()
    db_name = conn_config.pop('database')
    conn_config['database'] = 'postgres'

    conn = psycopg2.connect(**conn_config)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    if not cur.fetchone():
        print(f"Creating database '{db_name}'...")
        cur.execute(sql.SQL("CREATE DATABASE {} ENCODING 'UTF8'").format(
            sql.Identifier(db_name)
        ))
        print(f"Database '{db_name}' created.")
    else:
        print(f"Database '{db_name}' already exists.")

    cur.close()
    conn.close()


def table_exists_mysql(cur, database: str, table_name: str) -> bool:
    """Check if a table exists in MySQL."""
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = %s AND table_name = %s
    """, (database, table_name))
    return cur.fetchone()[0] > 0


def get_row_count(cur, table_name: str) -> int:
    """Get row count from a table."""
    cur.execute(f"SELECT COUNT(*) FROM `{table_name}`")
    return cur.fetchone()[0]


def fetch_all_data(cur, table_name: str, columns: List[str]) -> List[Tuple]:
    """Fetch all data from a MySQL table."""
    cols = ', '.join(f'`{c}`' for c in columns)
    cur.execute(f"SELECT {cols} FROM `{table_name}`")
    return cur.fetchall()


def migrate_table(
    mysql_cur,
    pg_conn,
    table_name: str,
    columns: List[str],
    insert_sql: str,
    batch_size: int,
    database: str,
    dry_run: bool = False
):
    """Migrate data from MySQL table to PostgreSQL."""
    from psycopg2.extras import execute_batch

    if not table_exists_mysql(mysql_cur, database, table_name):
        print(f"  Table '{table_name}' does not exist in MySQL, skipping...")
        return

    row_count = get_row_count(mysql_cur, table_name)
    print(f"  Migrating {row_count} rows from '{table_name}'...")

    if dry_run:
        print(f"  [DRY RUN] Would migrate {row_count} rows")
        return

    if row_count == 0:
        print(f"  No data in '{table_name}', skipping...")
        return

    data = fetch_all_data(mysql_cur, table_name, columns)
    pg_cur = pg_conn.cursor()

    try:
        pg_cur.execute(f'TRUNCATE TABLE "{table_name}" CASCADE')
        execute_batch(pg_cur, insert_sql, data, page_size=batch_size)
        pg_conn.commit()
        print(f"  Successfully migrated {len(data)} rows to '{table_name}'")
    except Exception as e:
        pg_conn.rollback()
        print(f"  Error migrating '{table_name}': {e}")
        raise
    finally:
        pg_cur.close()


# ============================================================================
# MAIN MIGRATION FUNCTIONS
# ============================================================================

def create_schemas(pg_conn, dry_run: bool = False):
    """Create all table schemas in PostgreSQL."""
    print("\n=== Creating Table Schemas ===\n")

    if dry_run:
        print("[DRY RUN] Would create all schemas")
        return

    cur = pg_conn.cursor()

    print("Creating bible_book...")
    cur.execute(SCHEMA_BIBLE_BOOK)

    print("Creating bible_books...")
    cur.execute(SCHEMA_BIBLE_BOOKS)

    print("Creating bible_search...")
    cur.execute(SCHEMA_BIBLE_SEARCH)

    print("Creating bible_multi_search...")
    cur.execute(SCHEMA_BIBLE_MULTI_SEARCH)

    for table_name in TRANSLATION_TABLES:
        print(f"Creating {table_name}...")
        cur.execute(SCHEMA_TRANSLATION_TABLE.format(table_name=table_name))

    pg_conn.commit()
    cur.close()
    print("\nAll schemas created successfully.")


def migrate_bible_book(mysql_cur, pg_conn, batch_size: int, database: str, dry_run: bool):
    """Migrate bible_book table."""
    columns = ['id', 'en', 'english', 'english2', 'en1', 'en2', 'en3',
               'short', 'chinese', 'cn', 'taiwan', 'tw', 'abbr', 'count', 'offset']

    insert_sql = """
        INSERT INTO bible_book (id, en, english, english2, en1, en2, en3,
                                short, chinese, cn, taiwan, tw, abbr, count, "offset")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            en = EXCLUDED.en, english = EXCLUDED.english, english2 = EXCLUDED.english2,
            en1 = EXCLUDED.en1, en2 = EXCLUDED.en2, en3 = EXCLUDED.en3,
            short = EXCLUDED.short, chinese = EXCLUDED.chinese, cn = EXCLUDED.cn,
            taiwan = EXCLUDED.taiwan, tw = EXCLUDED.tw, abbr = EXCLUDED.abbr,
            count = EXCLUDED.count, "offset" = EXCLUDED."offset"
    """
    migrate_table(mysql_cur, pg_conn, 'bible_book', columns, insert_sql,
                  batch_size, database, dry_run)


def migrate_bible_books(mysql_cur, pg_conn, batch_size: int, database: str, dry_run: bool):
    """Migrate bible_books table."""
    columns = ['id', 'book', 'chapter', 'verse', 'txt_tw', 'txt_cn',
               'txt_en', 'txt_py', 'short', 'updated', 'reported', 'likes']

    insert_sql = """
        INSERT INTO bible_books (id, book, chapter, verse, txt_tw, txt_cn,
                                 txt_en, txt_py, short, updated, reported, likes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (book, chapter, verse) DO UPDATE SET
            id = EXCLUDED.id, txt_tw = EXCLUDED.txt_tw, txt_cn = EXCLUDED.txt_cn,
            txt_en = EXCLUDED.txt_en, txt_py = EXCLUDED.txt_py, short = EXCLUDED.short,
            updated = EXCLUDED.updated, reported = EXCLUDED.reported, likes = EXCLUDED.likes
    """
    migrate_table(mysql_cur, pg_conn, 'bible_books', columns, insert_sql,
                  batch_size, database, dry_run)


def migrate_bible_search(mysql_cur, pg_conn, batch_size: int, database: str, dry_run: bool):
    """Migrate bible_search table."""
    columns = ['book', 'chapter', 'verse', 'txt']
    insert_sql = """
        INSERT INTO bible_search (book, chapter, verse, txt)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (book, chapter, verse) DO UPDATE SET txt = EXCLUDED.txt
    """
    migrate_table(mysql_cur, pg_conn, 'bible_search', columns, insert_sql,
                  batch_size, database, dry_run)


def migrate_bible_multi_search(mysql_cur, pg_conn, batch_size: int, database: str, dry_run: bool):
    """Migrate bible_multi_search table."""
    columns = ['book', 'chapter', 'verse', 'txt']
    insert_sql = """
        INSERT INTO bible_multi_search (book, chapter, verse, txt)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (book, chapter, verse) DO UPDATE SET txt = EXCLUDED.txt
    """
    migrate_table(mysql_cur, pg_conn, 'bible_multi_search', columns, insert_sql,
                  batch_size, database, dry_run)


def migrate_translation_table(mysql_cur, pg_conn, table_name: str, batch_size: int,
                               database: str, dry_run: bool):
    """Migrate a translation table."""
    columns = ['Book', 'Chapter', 'Verse', 'Scripture']
    insert_sql = f"""
        INSERT INTO "{table_name}" ("Book", "Chapter", "Verse", "Scripture")
        VALUES (%s, %s, %s, %s)
        ON CONFLICT ("Book", "Chapter", "Verse") DO UPDATE SET
            "Scripture" = EXCLUDED."Scripture"
    """
    migrate_table(mysql_cur, pg_conn, table_name, columns, insert_sql,
                  batch_size, database, dry_run)


def main():
    """Main migration function."""
    args = parse_args()

    print("=" * 60)
    print("MySQL to PostgreSQL Migration for BibleEngine")
    print("=" * 60)

    if args.dry_run:
        print("\n*** DRY RUN MODE - No changes will be made ***\n")

    mysql_config = {
        'host': args.mysql_host,
        'port': args.mysql_port,
        'user': args.mysql_user,
        'password': args.mysql_password,
        'database': args.mysql_database,
    }

    pg_config = {
        'host': args.pg_host,
        'port': args.pg_port,
        'user': args.pg_user,
        'password': args.pg_password,
        'database': args.pg_database,
    }

    # Step 1: Create database
    print("\n=== Step 1: Database Setup ===\n")
    if not args.dry_run:
        try:
            create_database_if_not_exists(pg_config)
        except Exception as e:
            print(f"Error creating database: {e}")
            sys.exit(1)
    else:
        print(f"[DRY RUN] Would create database '{pg_config['database']}' if not exists")

    # Step 2: Connect to databases
    print("\n=== Step 2: Connecting to Databases ===\n")
    try:
        mysql_conn = get_mysql_connection(mysql_config)
        mysql_cur = mysql_conn.cursor()
        print(f"Connected to MySQL at {mysql_config['host']}:{mysql_config['port']}")
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        sys.exit(1)

    pg_conn = None
    if not args.dry_run:
        try:
            pg_conn = get_postgres_connection(pg_config)
            print(f"Connected to PostgreSQL at {pg_config['host']}:{pg_config['port']}")
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            mysql_conn.close()
            sys.exit(1)

    try:
        # Step 3: Create schemas
        if pg_conn:
            create_schemas(pg_conn, args.dry_run)

        # Step 4: Migrate core tables
        print("\n=== Step 3: Migrating Core Tables ===\n")

        tables_to_migrate = args.tables if args.tables else None

        if not tables_to_migrate or 'bible_book' in tables_to_migrate:
            print("Migrating bible_book...")
            migrate_bible_book(mysql_cur, pg_conn, args.batch_size,
                               mysql_config['database'], args.dry_run)

        if not tables_to_migrate or 'bible_books' in tables_to_migrate:
            print("Migrating bible_books...")
            migrate_bible_books(mysql_cur, pg_conn, args.batch_size,
                                mysql_config['database'], args.dry_run)

        if not tables_to_migrate or 'bible_search' in tables_to_migrate:
            print("Migrating bible_search...")
            migrate_bible_search(mysql_cur, pg_conn, args.batch_size,
                                 mysql_config['database'], args.dry_run)

        if not tables_to_migrate or 'bible_multi_search' in tables_to_migrate:
            print("Migrating bible_multi_search...")
            migrate_bible_multi_search(mysql_cur, pg_conn, args.batch_size,
                                       mysql_config['database'], args.dry_run)

        # Step 5: Migrate translation tables
        if not args.skip_translations:
            print("\n=== Step 4: Migrating Translation Tables ===\n")
            for table_name in TRANSLATION_TABLES:
                if not tables_to_migrate or table_name in tables_to_migrate:
                    print(f"Migrating {table_name}...")
                    migrate_translation_table(mysql_cur, pg_conn, table_name,
                                              args.batch_size, mysql_config['database'],
                                              args.dry_run)

        print("\n" + "=" * 60)
        if args.dry_run:
            print("Dry run completed - no changes were made")
        else:
            print("Migration completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nMigration failed with error: {e}")
        sys.exit(1)
    finally:
        mysql_cur.close()
        mysql_conn.close()
        if pg_conn:
            pg_conn.close()
        print("\nDatabase connections closed.")


if __name__ == '__main__':
    main()
