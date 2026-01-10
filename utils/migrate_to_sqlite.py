#!/usr/bin/env python3
"""
MySQL to SQLite Migration Script for BibleEngine Database

This script migrates all tables and data from MySQL to SQLite.
Designed for Ubuntu 24.04 VPS.

Requirements:
    pip install pymysql

Usage:
    python3 migrate_to_sqlite.py --help
    python3 migrate_to_sqlite.py --mysql-host localhost --mysql-user root --mysql-password secret
    python3 migrate_to_sqlite.py --sqlite-path /path/to/bible.db
"""

import argparse
import os
import sqlite3
import sys
from datetime import date
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
    en       TEXT         NOT NULL,
    english  TEXT,
    english2 TEXT,
    en1      TEXT,
    en2      TEXT,
    en3      TEXT,
    short    TEXT,
    chinese  TEXT,
    cn       TEXT,
    taiwan   TEXT,
    tw       TEXT,
    abbr     TEXT,
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
    short    TEXT         NOT NULL,
    updated  TEXT,
    reported TEXT,
    likes    INTEGER      NOT NULL DEFAULT 0,
    PRIMARY KEY (book, chapter, verse)
);

CREATE INDEX IF NOT EXISTS idx_bible_books_short ON bible_books(short);
"""

SCHEMA_BIBLE_SEARCH = """
CREATE TABLE IF NOT EXISTS bible_search (
    book    INTEGER      NOT NULL,
    chapter INTEGER      NOT NULL,
    verse   INTEGER      NOT NULL,
    txt     TEXT         NOT NULL,
    PRIMARY KEY (book, chapter, verse)
);
"""

SCHEMA_BIBLE_MULTI_SEARCH = """
CREATE TABLE IF NOT EXISTS bible_multi_search (
    book    INTEGER      NOT NULL,
    chapter INTEGER      NOT NULL,
    verse   INTEGER      NOT NULL,
    txt     TEXT         NOT NULL,
    PRIMARY KEY (book, chapter, verse)
);
"""

# FTS5 Virtual Tables for Full-Text Search
SCHEMA_FTS_BIBLE_BOOKS = """
CREATE VIRTUAL TABLE IF NOT EXISTS bible_books_fts USING fts5(
    txt_tw,
    txt_cn,
    txt_en,
    txt_py,
    content='bible_books',
    content_rowid='rowid'
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER IF NOT EXISTS bible_books_ai AFTER INSERT ON bible_books BEGIN
    INSERT INTO bible_books_fts(rowid, txt_tw, txt_cn, txt_en, txt_py)
    VALUES (new.rowid, new.txt_tw, new.txt_cn, new.txt_en, new.txt_py);
END;

CREATE TRIGGER IF NOT EXISTS bible_books_ad AFTER DELETE ON bible_books BEGIN
    INSERT INTO bible_books_fts(bible_books_fts, rowid, txt_tw, txt_cn, txt_en, txt_py)
    VALUES ('delete', old.rowid, old.txt_tw, old.txt_cn, old.txt_en, old.txt_py);
END;

CREATE TRIGGER IF NOT EXISTS bible_books_au AFTER UPDATE ON bible_books BEGIN
    INSERT INTO bible_books_fts(bible_books_fts, rowid, txt_tw, txt_cn, txt_en, txt_py)
    VALUES ('delete', old.rowid, old.txt_tw, old.txt_cn, old.txt_en, old.txt_py);
    INSERT INTO bible_books_fts(rowid, txt_tw, txt_cn, txt_en, txt_py)
    VALUES (new.rowid, new.txt_tw, new.txt_cn, new.txt_en, new.txt_py);
END;
"""

SCHEMA_FTS_BIBLE_SEARCH = """
CREATE VIRTUAL TABLE IF NOT EXISTS bible_search_fts USING fts5(
    txt,
    content='bible_search',
    content_rowid='rowid'
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER IF NOT EXISTS bible_search_ai AFTER INSERT ON bible_search BEGIN
    INSERT INTO bible_search_fts(rowid, txt) VALUES (new.rowid, new.txt);
END;

CREATE TRIGGER IF NOT EXISTS bible_search_ad AFTER DELETE ON bible_search BEGIN
    INSERT INTO bible_search_fts(bible_search_fts, rowid, txt)
    VALUES ('delete', old.rowid, old.txt);
END;

CREATE TRIGGER IF NOT EXISTS bible_search_au AFTER UPDATE ON bible_search BEGIN
    INSERT INTO bible_search_fts(bible_search_fts, rowid, txt)
    VALUES ('delete', old.rowid, old.txt);
    INSERT INTO bible_search_fts(rowid, txt) VALUES (new.rowid, new.txt);
END;
"""

SCHEMA_FTS_MULTI_SEARCH = """
CREATE VIRTUAL TABLE IF NOT EXISTS bible_multi_search_fts USING fts5(
    txt,
    content='bible_multi_search',
    content_rowid='rowid'
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER IF NOT EXISTS bible_multi_search_ai AFTER INSERT ON bible_multi_search BEGIN
    INSERT INTO bible_multi_search_fts(rowid, txt) VALUES (new.rowid, new.txt);
END;

CREATE TRIGGER IF NOT EXISTS bible_multi_search_ad AFTER DELETE ON bible_multi_search BEGIN
    INSERT INTO bible_multi_search_fts(bible_multi_search_fts, rowid, txt)
    VALUES ('delete', old.rowid, old.txt);
END;

CREATE TRIGGER IF NOT EXISTS bible_multi_search_au AFTER UPDATE ON bible_multi_search BEGIN
    INSERT INTO bible_multi_search_fts(bible_multi_search_fts, rowid, txt)
    VALUES ('delete', old.rowid, old.txt);
    INSERT INTO bible_multi_search_fts(rowid, txt) VALUES (new.rowid, new.txt);
END;
"""

# Template for translation tables
SCHEMA_TRANSLATION_TABLE = """
CREATE TABLE IF NOT EXISTS {table_name} (
    Book      INTEGER  NOT NULL,
    Chapter   INTEGER  NOT NULL,
    Verse     INTEGER  NOT NULL,
    Scripture TEXT,
    PRIMARY KEY (Book, Chapter, Verse)
);
"""

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Migrate BibleEngine database from MySQL to SQLite.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Use default settings (localhost, default ports)
  python3 %(prog)s

  # Specify MySQL credentials
  python3 %(prog)s --mysql-user bible --mysql-password secret123

  # Specify SQLite database path
  python3 %(prog)s --sqlite-path /var/lib/bibleengine/bible.db

  # Full custom configuration
  python3 %(prog)s \\
      --mysql-host 10.0.0.1 --mysql-port 3306 \\
      --mysql-user bible --mysql-password mysqlpass \\
      --mysql-database bible \\
      --sqlite-path ./bible.db

  # Use environment variables
  export MYSQL_PASSWORD=secret
  python3 %(prog)s

  # Dry run (show what would be migrated)
  python3 %(prog)s --dry-run

  # Skip FTS index creation (faster migration)
  python3 %(prog)s --skip-fts

  # Custom batch size for large datasets
  python3 %(prog)s --batch-size 5000

Tables Migrated:
  - bible_book        : Book metadata (66 books)
  - bible_books       : Main verses table with likes
  - bible_search      : Full-text search index
  - bible_multi_search: Multi-language search index
  - bible_book_*      : 20+ translation tables (KJV, CUVS, etc.)

FTS5 Virtual Tables (for full-text search):
  - bible_books_fts
  - bible_search_fts
  - bible_multi_search_fts
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

    # SQLite options
    sqlite_group = parser.add_argument_group('SQLite Options')
    sqlite_group.add_argument(
        '--sqlite-path',
        default=os.environ.get('SQLITE_PATH', './bible.db'),
        help='SQLite database file path (default: ./bible.db, env: SQLITE_PATH)'
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
        '--skip-fts',
        action='store_true',
        help='Skip FTS5 full-text search index creation'
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
               BibleEngine MySQL to SQLite Migration Tool
================================================================================

DESCRIPTION:
    This tool migrates the BibleEngine database from MySQL/MariaDB to SQLite.
    It creates the schema, transfers all data, and sets up FTS5 full-text search.

REQUIREMENTS:
    pip install pymysql
    (sqlite3 is included in Python standard library)

QUICK START:
    1. Ensure MySQL source database is accessible
    2. Run: python3 migrate_to_sqlite.py --mysql-password <pwd>

FEATURES:
    - Single-file SQLite database (portable)
    - FTS5 full-text search with auto-sync triggers
    - WAL mode for better concurrent access
    - Batch inserts for performance
    - VACUUM and ANALYZE optimization

DATABASE SCHEMA:
    Core Tables:
        bible_book         - Book metadata (id, names in EN/CN/TW)
        bible_books        - Main verses with likes count
        bible_search       - Full-text search index
        bible_multi_search - Multi-language search

    Translation Tables (20+):
        bible_book_kjv, bible_book_cuvs, bible_book_cuvt, etc.

    FTS5 Virtual Tables:
        bible_books_fts, bible_search_fts, bible_multi_search_fts

ENVIRONMENT VARIABLES:
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
    SQLITE_PATH

SQLITE USAGE:
    After migration, use the database with:
        import sqlite3
        conn = sqlite3.connect('/path/to/bible.db')

    Full-text search example:
        SELECT * FROM bible_books_fts WHERE bible_books_fts MATCH 'love';

For full options, run: python3 migrate_to_sqlite.py --help
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


def get_sqlite_connection(db_path: str):
    """Create SQLite connection."""
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"Created directory: {db_dir}")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
    return conn


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


def convert_date(value):
    """Convert date objects to string for SQLite."""
    if value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def migrate_table(
    mysql_cur,
    sqlite_conn,
    table_name: str,
    columns: List[str],
    insert_sql: str,
    batch_size: int,
    database: str,
    has_date_columns: bool = False,
    dry_run: bool = False
):
    """Migrate data from MySQL table to SQLite."""
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

    # Convert dates if needed
    if has_date_columns:
        converted_data = []
        for row in data:
            converted_row = tuple(convert_date(v) if isinstance(v, date) else v for v in row)
            converted_data.append(converted_row)
        data = converted_data

    sqlite_cur = sqlite_conn.cursor()

    try:
        sqlite_cur.execute(f'DELETE FROM "{table_name}"')

        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            sqlite_cur.executemany(insert_sql, batch)

        sqlite_conn.commit()
        print(f"  Successfully migrated {len(data)} rows to '{table_name}'")
    except Exception as e:
        sqlite_conn.rollback()
        print(f"  Error migrating '{table_name}': {e}")
        raise


def rebuild_fts_index(sqlite_conn, fts_table: str, source_table: str, columns: List[str]):
    """Rebuild FTS index from source table."""
    print(f"  Rebuilding FTS index for {fts_table}...")
    cur = sqlite_conn.cursor()

    try:
        cur.execute(f"DELETE FROM {fts_table}")
        col_list = ', '.join(columns)
        cur.execute(f"""
            INSERT INTO {fts_table}(rowid, {col_list})
            SELECT rowid, {col_list} FROM {source_table}
        """)
        sqlite_conn.commit()
        print(f"  FTS index rebuilt for {fts_table}")
    except Exception as e:
        print(f"  Error rebuilding FTS index: {e}")
        raise


# ============================================================================
# MAIN MIGRATION FUNCTIONS
# ============================================================================

def create_schemas(sqlite_conn, dry_run: bool = False):
    """Create all table schemas in SQLite."""
    print("\n=== Creating Table Schemas ===\n")

    if dry_run:
        print("[DRY RUN] Would create all schemas")
        return

    cur = sqlite_conn.cursor()

    print("Creating bible_book...")
    cur.executescript(SCHEMA_BIBLE_BOOK)

    print("Creating bible_books...")
    cur.executescript(SCHEMA_BIBLE_BOOKS)

    print("Creating bible_search...")
    cur.executescript(SCHEMA_BIBLE_SEARCH)

    print("Creating bible_multi_search...")
    cur.executescript(SCHEMA_BIBLE_MULTI_SEARCH)

    for table_name in TRANSLATION_TABLES:
        print(f"Creating {table_name}...")
        cur.execute(SCHEMA_TRANSLATION_TABLE.format(table_name=table_name))

    sqlite_conn.commit()
    print("\nAll schemas created successfully.")


def create_fts_tables(sqlite_conn, dry_run: bool = False):
    """Create FTS5 virtual tables for full-text search."""
    print("\n=== Creating FTS5 Virtual Tables ===\n")

    if dry_run:
        print("[DRY RUN] Would create FTS5 tables")
        return

    cur = sqlite_conn.cursor()

    print("Creating bible_books_fts...")
    cur.executescript(SCHEMA_FTS_BIBLE_BOOKS)

    print("Creating bible_search_fts...")
    cur.executescript(SCHEMA_FTS_BIBLE_SEARCH)

    print("Creating bible_multi_search_fts...")
    cur.executescript(SCHEMA_FTS_MULTI_SEARCH)

    sqlite_conn.commit()
    print("\nFTS tables created successfully.")


def migrate_bible_book(mysql_cur, sqlite_conn, batch_size: int, database: str, dry_run: bool):
    """Migrate bible_book table."""
    columns = ['id', 'en', 'english', 'english2', 'en1', 'en2', 'en3',
               'short', 'chinese', 'cn', 'taiwan', 'tw', 'abbr', 'count', 'offset']

    insert_sql = """
        INSERT OR REPLACE INTO bible_book
        (id, en, english, english2, en1, en2, en3, short, chinese, cn,
         taiwan, tw, abbr, count, "offset")
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    migrate_table(mysql_cur, sqlite_conn, 'bible_book', columns, insert_sql,
                  batch_size, database, dry_run=dry_run)


def migrate_bible_books(mysql_cur, sqlite_conn, batch_size: int, database: str, dry_run: bool):
    """Migrate bible_books table."""
    columns = ['id', 'book', 'chapter', 'verse', 'txt_tw', 'txt_cn',
               'txt_en', 'txt_py', 'short', 'updated', 'reported', 'likes']

    insert_sql = """
        INSERT OR REPLACE INTO bible_books
        (id, book, chapter, verse, txt_tw, txt_cn, txt_en, txt_py,
         short, updated, reported, likes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    migrate_table(mysql_cur, sqlite_conn, 'bible_books', columns, insert_sql,
                  batch_size, database, has_date_columns=True, dry_run=dry_run)


def migrate_bible_search(mysql_cur, sqlite_conn, batch_size: int, database: str, dry_run: bool):
    """Migrate bible_search table."""
    columns = ['book', 'chapter', 'verse', 'txt']
    insert_sql = """
        INSERT OR REPLACE INTO bible_search (book, chapter, verse, txt)
        VALUES (?, ?, ?, ?)
    """
    migrate_table(mysql_cur, sqlite_conn, 'bible_search', columns, insert_sql,
                  batch_size, database, dry_run=dry_run)


def migrate_bible_multi_search(mysql_cur, sqlite_conn, batch_size: int, database: str, dry_run: bool):
    """Migrate bible_multi_search table."""
    columns = ['book', 'chapter', 'verse', 'txt']
    insert_sql = """
        INSERT OR REPLACE INTO bible_multi_search (book, chapter, verse, txt)
        VALUES (?, ?, ?, ?)
    """
    migrate_table(mysql_cur, sqlite_conn, 'bible_multi_search', columns, insert_sql,
                  batch_size, database, dry_run=dry_run)


def migrate_translation_table(mysql_cur, sqlite_conn, table_name: str, batch_size: int,
                               database: str, dry_run: bool):
    """Migrate a translation table."""
    columns = ['Book', 'Chapter', 'Verse', 'Scripture']
    insert_sql = f"""
        INSERT OR REPLACE INTO "{table_name}" (Book, Chapter, Verse, Scripture)
        VALUES (?, ?, ?, ?)
    """
    migrate_table(mysql_cur, sqlite_conn, table_name, columns, insert_sql,
                  batch_size, database, dry_run=dry_run)


def rebuild_all_fts_indexes(sqlite_conn, dry_run: bool = False):
    """Rebuild all FTS indexes after data migration."""
    print("\n=== Rebuilding FTS Indexes ===\n")

    if dry_run:
        print("[DRY RUN] Would rebuild FTS indexes")
        return

    rebuild_fts_index(sqlite_conn, 'bible_books_fts', 'bible_books',
                      ['txt_tw', 'txt_cn', 'txt_en', 'txt_py'])
    rebuild_fts_index(sqlite_conn, 'bible_search_fts', 'bible_search', ['txt'])
    rebuild_fts_index(sqlite_conn, 'bible_multi_search_fts', 'bible_multi_search', ['txt'])

    print("\nAll FTS indexes rebuilt successfully.")


def main():
    """Main migration function."""
    args = parse_args()

    print("=" * 60)
    print("MySQL to SQLite Migration for BibleEngine")
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

    # Step 1: Connect to MySQL
    print("\n=== Step 1: Connecting to Databases ===\n")
    try:
        mysql_conn = get_mysql_connection(mysql_config)
        mysql_cur = mysql_conn.cursor()
        print(f"Connected to MySQL at {mysql_config['host']}:{mysql_config['port']}")
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        sys.exit(1)

    # Step 2: Create/Connect to SQLite
    sqlite_conn = None
    if not args.dry_run:
        try:
            sqlite_conn = get_sqlite_connection(args.sqlite_path)
            print(f"SQLite database opened at: {args.sqlite_path}")
        except Exception as e:
            print(f"Error creating SQLite database: {e}")
            mysql_conn.close()
            sys.exit(1)
    else:
        print(f"[DRY RUN] Would create SQLite database at: {args.sqlite_path}")

    try:
        # Step 3: Create schemas (without FTS first)
        if sqlite_conn:
            create_schemas(sqlite_conn, args.dry_run)

        # Step 4: Migrate core tables
        print("\n=== Step 2: Migrating Core Tables ===\n")

        tables_to_migrate = args.tables if args.tables else None

        if not tables_to_migrate or 'bible_book' in tables_to_migrate:
            print("Migrating bible_book...")
            migrate_bible_book(mysql_cur, sqlite_conn, args.batch_size,
                               mysql_config['database'], args.dry_run)

        if not tables_to_migrate or 'bible_books' in tables_to_migrate:
            print("Migrating bible_books...")
            migrate_bible_books(mysql_cur, sqlite_conn, args.batch_size,
                                mysql_config['database'], args.dry_run)

        if not tables_to_migrate or 'bible_search' in tables_to_migrate:
            print("Migrating bible_search...")
            migrate_bible_search(mysql_cur, sqlite_conn, args.batch_size,
                                 mysql_config['database'], args.dry_run)

        if not tables_to_migrate or 'bible_multi_search' in tables_to_migrate:
            print("Migrating bible_multi_search...")
            migrate_bible_multi_search(mysql_cur, sqlite_conn, args.batch_size,
                                       mysql_config['database'], args.dry_run)

        # Step 5: Migrate translation tables
        if not args.skip_translations:
            print("\n=== Step 3: Migrating Translation Tables ===\n")
            for table_name in TRANSLATION_TABLES:
                if not tables_to_migrate or table_name in tables_to_migrate:
                    print(f"Migrating {table_name}...")
                    migrate_translation_table(mysql_cur, sqlite_conn, table_name,
                                              args.batch_size, mysql_config['database'],
                                              args.dry_run)

        # Step 6: Create FTS tables and rebuild indexes
        if not args.skip_fts and sqlite_conn:
            create_fts_tables(sqlite_conn, args.dry_run)
            rebuild_all_fts_indexes(sqlite_conn, args.dry_run)

        # Step 7: Optimize database
        if sqlite_conn and not args.dry_run:
            print("\n=== Step 4: Optimizing Database ===\n")
            print("Running VACUUM...")
            sqlite_conn.execute("VACUUM")
            print("Running ANALYZE...")
            sqlite_conn.execute("ANALYZE")

        print("\n" + "=" * 60)
        if args.dry_run:
            print("Dry run completed - no changes were made")
        else:
            print("Migration completed successfully!")
            print(f"SQLite database created at: {args.sqlite_path}")

            if os.path.exists(args.sqlite_path):
                size_mb = os.path.getsize(args.sqlite_path) / (1024 * 1024)
                print(f"Database size: {size_mb:.2f} MB")
        print("=" * 60)

    except Exception as e:
        print(f"\nMigration failed with error: {e}")
        sys.exit(1)
    finally:
        mysql_cur.close()
        mysql_conn.close()
        if sqlite_conn:
            sqlite_conn.close()
        print("\nDatabase connections closed.")


if __name__ == '__main__':
    main()
