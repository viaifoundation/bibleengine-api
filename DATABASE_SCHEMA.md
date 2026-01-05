# Database Schema

This document describes the expected database schema for the BibleEngine API.

## Tables

### `bible_books`

Main table storing Bible verses with text and metadata.

**Columns:**
- `book` (INTEGER): Book ID (1-66)
- `chapter` (INTEGER): Chapter number
- `verse` (INTEGER): Verse number
- `txt` (TEXT): Verse text content
- `likes` (INTEGER, default 0): Number of likes for this verse
- `translation` (VARCHAR, optional): Translation code (cuvs, cuvt, kjv, nasb, esv)

**Indexes:**
- Primary key: `(book, chapter, verse)`
- Index on `book`, `chapter`, `verse` for fast lookups

**Example:**
```sql
CREATE TABLE bible_books (
    book INTEGER NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    txt TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    translation VARCHAR(10),
    PRIMARY KEY (book, chapter, verse)
);

CREATE INDEX idx_bible_books_lookup ON bible_books(book, chapter, verse);
```

### `bible_search`

Search table for full-text search functionality.

**Columns:**
- `book` (INTEGER): Book ID (1-66)
- `chapter` (INTEGER): Chapter number
- `verse` (INTEGER): Verse number
- `txt` (TEXT): Verse text content for searching

**Indexes:**
- Full-text index on `txt` for keyword searches
- Index on `book`, `chapter`, `verse`

**Example:**
```sql
CREATE TABLE bible_search (
    book INTEGER NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    txt TEXT NOT NULL
);

CREATE INDEX idx_bible_search_text ON bible_search USING gin(to_tsvector('english', txt));
CREATE INDEX idx_bible_search_lookup ON bible_search(book, chapter, verse);
```

## Notes

1. The schema assumes PostgreSQL as the database backend.
2. For full-text search, PostgreSQL's `tsvector` and `gin` indexes are recommended.
3. The `bible_books` table may need a `translation` column if storing multiple translations in the same table, or separate tables per translation (e.g., `bible_books_cuvs`, `bible_books_kjv`).
4. The `likes` column should be initialized to 0 for all verses.

## Migration from MySQL/MariaDB

If migrating from the PHP version (which uses MySQL), you may need to:

1. Convert table names to lowercase (PostgreSQL is case-sensitive)
2. Adjust data types (e.g., `TEXT` vs `LONGTEXT`)
3. Update full-text search indexes (PostgreSQL uses `tsvector` instead of MySQL's `FULLTEXT`)
4. Ensure UTF-8 encoding is properly set

