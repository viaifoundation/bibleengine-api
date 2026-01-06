# Bible Database Schema Documentation

This document describes the complete database schema for the BibleEngine database. The database uses MariaDB/MySQL and contains multiple tables for different Bible translations and search functionality.

## Database Overview

**Database Name:** `bible`

**Total Tables:** 26 tables (excluding system tables)

## Core Tables

### 1. Book Information Tables

#### `bible_book`

Book name reference table containing book names in multiple languages and formats.

**Purpose:** Provides book name lookups and metadata for all 66 books of the Bible. This table serves as a mapping table for book names across different languages and formats.

**Schema:**
```sql
CREATE TABLE bible_book (
    id       INT(11)      NOT NULL PRIMARY KEY DEFAULT 0,
    en       VARCHAR(8)    NOT NULL,
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
    count    INT(11)      DEFAULT 0,
    offset   INT(11)      NOT NULL DEFAULT 0
);
```

**Columns:**

| Field    | Type        | Description |
|----------|-------------|-------------|
| `id`      | INT(11) PK  | Book ID (1-66) |
| `en`      | VARCHAR(8)  | English abbreviation (e.g., "Gen", "Exod") |
| `english` | VARCHAR(20) | Full English name (e.g., "Genesis", "Exodus") |
| `english2` | VARCHAR(20) | Alternative English name |
| `en1`     | VARCHAR(8)  | Additional English abbreviation variant 1 |
| `en2`     | VARCHAR(8)  | Additional English abbreviation variant 2 |
| `en3`     | VARCHAR(8)  | Additional English abbreviation variant 3 |
| `short`   | VARCHAR(8)  | General short abbreviation |
| `chinese` | VARCHAR(32) | Chinese full name (Simplified) |
| `cn`      | VARCHAR(10) | Chinese abbreviation (Simplified) |
| `taiwan`  | VARCHAR(32) | Chinese full name (Traditional) |
| `tw`      | VARCHAR(10) | Chinese abbreviation (Traditional) |
| `abbr`    | VARCHAR(32) | General abbreviation |
| `count`   | INT(11)     | Number of chapters in the book |
| `offset`  | INT(11)     | Chapter offset (for verse numbering calculations) |

**Indexes:**
- Primary Key: `id`

**Example Data:**
```
id=1, en="Gen", english="Genesis", chinese="创世记" (Genesis), count=50, offset=0
id=43, en="John", english="John", chinese="约翰福音" (Gospel of John), count=21, offset=997
```

**Note:** Chinese characters in the example are shown with their English translations in parentheses for reference.

---

#### `bible_books`

Main Bible text table storing verses with multiple translations in a single row.

**Purpose:** Central table containing verses with Traditional Chinese (CUVT), Simplified Chinese (CUVS), English (KJV), and Pinyin translations. This table also manages the like functionality for verses.

**Schema:**
```sql
CREATE TABLE bible_books (
    id       INT(11),
    book     INT(11)      NOT NULL,
    chapter  INT(11)      NOT NULL,
    verse    INT(11)      NOT NULL,
    txt_tw   TEXT,
    txt_cn   TEXT,
    txt_en   TEXT,
    txt_py   TEXT,
    short    VARCHAR(8)   NOT NULL,
    updated  DATE,
    reported DATE,
    likes    INT(11)      NOT NULL DEFAULT 0,
    PRIMARY KEY (book, chapter, verse)
);
```

**Columns:**

| Field     | Type        | Description |
|-----------|-------------|-------------|
| `id`       | INT(11)     | Auto-increment ID (optional) |
| `book`     | INT(11)     | Book ID (1-66) |
| `chapter`  | INT(11)     | Chapter number |
| `verse`    | INT(11)     | Verse number |
| `txt_tw`   | TEXT        | Traditional Chinese text (CUVT) - indexed for search |
| `txt_cn`   | TEXT        | Simplified Chinese text (CUVS) |
| `txt_en`   | TEXT        | English text (KJV) |
| `txt_py`   | TEXT        | Pinyin text |
| `short`    | VARCHAR(8)  | Book abbreviation |
| `updated`  | DATE        | Last update date |
| `reported` | DATE        | Report date (for error reporting) |
| `likes`    | INT(11)     | Like count for this verse (default: 0) |

**Indexes:**
- Primary Key: `(book, chapter, verse)`
- Full-text Index: `txt_tw` (for search)

**Notes:**
- This table combines multiple translations in one row
- The `likes` column is used for the like functionality
- `txt_tw` has a full-text index for search operations

---

### 2. Translation-Specific Tables

Each translation has its own dedicated table following the pattern `bible_book_{translation_code}`.

**Design Rationale:** Separating each translation into its own table prevents single tables from becoming too large and allows for better performance and maintenance. This design also enables independent updates and versioning of different translations.

#### Common Schema for Translation Tables

All translation tables follow this identical structure:

```sql
CREATE TABLE bible_book_{translation} (
    Book      INT(11)  NOT NULL,
    Chapter   INT(11)  NOT NULL,
    Verse     INT(11)  NOT NULL,
    Scripture TEXT,
    PRIMARY KEY (Book, Chapter, Verse)
);
```

**Available Translation Tables (20+ tables):**

| Table Name | Translation | Language |
|------------|-------------|----------|
| `bible_book_cuvs` | Chinese Union Version Simplified | Chinese (Simplified) |
| `bible_book_cuvt` | Chinese Union Version Traditional | Chinese (Traditional) |
| `bible_book_cuvc` | Chinese Union Version (variant) | Chinese |
| `bible_book_kjv` | King James Version | English |
| `bible_book_kjv1611` | King James Version 1611 | English |
| `bible_book_nasb` | New American Standard Bible | English |
| `bible_book_esv` | English Standard Version | English |
| `bible_book_pinyin` | Pinyin | Chinese (Romanized) |
| `bible_book_ncvs` | New Chinese Version Simplified | Chinese (Simplified) |
| `bible_book_lcvs` | Literal Chinese Version Simplified | Chinese (Simplified) |
| `bible_book_ccsb` | Chinese Contemporary Study Bible | Chinese |
| `bible_book_clbs` | Chinese Living Bible Simplified | Chinese (Simplified) |
| `bible_book_ckjvs` | Chinese King James Version Simplified | Chinese (Simplified) |
| `bible_book_ckjvt` | Chinese King James Version Traditional | Chinese (Traditional) |
| `bible_book_ukjv` | Updated King James Version | English |
| `bible_book_tcvs` | Traditional Chinese Version Simplified | Chinese |
| `bible_book_tr` | Turkish Translation | Turkish |
| `bible_book_wlc` | Westminster Leningrad Codex | Hebrew |
| `bible_book_bbe` | Bible in Basic English | English |
| `bible_book_nstrunv` | New Simplified Traditional Revised Union New Version | Chinese |

**Column Details:**

| Field      | Type   | Key | Description |
|------------|--------|-----|-------------|
| `Book`     | INT(11)| PRI | Book ID (1-66) |
| `Chapter`  | INT(11)| PRI | Chapter number |
| `Verse`    | INT(11)| PRI | Verse number |
| `Scripture`| TEXT   |     | Verse text content |

**Notes:**
- All translation tables use the same structure
- Primary key is composite: `(Book, Chapter, Verse)`
- Some tables may have NULL values for certain verses (e.g., `bible_book_wlc`)

---

### 3. Search Index Tables

#### `bible_search`

Single-language full-text search table for keyword searches.

**Purpose:** Optimized table for full-text keyword searches across Bible verses. This table is specifically designed for efficient text searching operations.

**Schema:**
```sql
CREATE TABLE bible_search (
    book    TINYINT(2) UNSIGNED  NOT NULL,
    chapter TINYINT(3) UNSIGNED  NOT NULL,
    verse   TINYINT(3) UNSIGNED  NOT NULL,
    txt     TEXT                 NOT NULL,
    PRIMARY KEY (book, chapter, verse)
);
```

**Columns:**

| Field   | Type                  | Key | Description |
|---------|-----------------------|-----|-------------|
| `book`  | TINYINT(2) UNSIGNED  | PRI | Book ID (1-66) |
| `chapter` | TINYINT(3) UNSIGNED | PRI | Chapter number |
| `verse` | TINYINT(3) UNSIGNED  | PRI | Verse number |
| `txt`   | TEXT                 | MUL | Verse text for full-text search (indexed) |

**Indexes:**
- Primary Key: `(book, chapter, verse)`
- Full-text Index: `txt` (for keyword search)

**Usage:**
- Used for keyword-based verse searches
- Contains searchable text (typically in one language, often Chinese or English)
- Optimized for `LIKE` queries and full-text search

---

#### `bible_multi_search`

Multi-language full-text search table.

**Purpose:** Similar to `bible_search` but optimized for multi-language searches. This table may contain content in multiple languages or be used for cross-language search operations.

**Schema:**
```sql
CREATE TABLE bible_multi_search (
    book    TINYINT(2) UNSIGNED  NOT NULL,
    chapter TINYINT(3) UNSIGNED  NOT NULL,
    verse   TINYINT(3) UNSIGNED  NOT NULL,
    txt     TEXT                 NOT NULL,
    PRIMARY KEY (book, chapter, verse)
);
```

**Columns:**

| Field   | Type                  | Key | Description |
|---------|-----------------------|-----|-------------|
| `book`  | TINYINT(2) UNSIGNED  | PRI | Book ID (1-66) |
| `chapter` | TINYINT(3) UNSIGNED | PRI | Chapter number |
| `verse` | TINYINT(3) UNSIGNED  | PRI | Verse number |
| `txt`   | TEXT                 | MUL | Verse text for multi-language full-text search (indexed) |

**Indexes:**
- Primary Key: `(book, chapter, verse)`
- Full-text Index: `txt`

**Notes:**
- Structure identical to `bible_search`
- May contain different language content or be used for cross-language searches

---

### 4. System Tables

#### `mytest`
- Purpose: Testing table (may be used for development/testing purposes)

#### `sae_selfchk_tb`
- Purpose: Self-check table (likely used for system health checks or monitoring)

---

## Table Relationships

```
bible_book (metadata)
    ↓ (id)
bible_books (main table with multiple translations)
    ↓ (book, chapter, verse)
bible_book_{translation} (individual translation tables)
    ↓ (Book, Chapter, Verse)
bible_search / bible_multi_search (search tables)
```

## Data Access Patterns

### 1. Verse Lookup by Reference
```sql
-- Get verse from main table
SELECT * FROM bible_books 
WHERE book = 43 AND chapter = 3 AND verse = 16;

-- Get verse from specific translation
SELECT * FROM bible_book_kjv 
WHERE Book = 43 AND Chapter = 3 AND Verse = 16;
```

### 2. Keyword Search
```sql
-- Search in bible_search table
SELECT * FROM bible_search 
WHERE txt LIKE '%love%' 
LIMIT 100;
```

### 3. Book Metadata Lookup
```sql
-- Get book information
SELECT * FROM bible_book WHERE id = 43;
```

### 4. Like Functionality
```sql
-- Increment likes
UPDATE bible_books 
SET likes = likes + 1 
WHERE book = 43 AND chapter = 3 AND verse = 16;

-- Get verse with likes
SELECT book, chapter, verse, txt_cn, likes 
FROM bible_books 
WHERE book = 43 AND chapter = 3 AND verse = 16;
```

## Database System

This database is designed for **MariaDB/MySQL**. The schema uses MySQL-specific features:

1. **Data Types:**
   - `TINYINT` - Used for book, chapter, verse (space-efficient)
   - `TEXT` - For verse content
   - `VARCHAR(n)` - For book names and abbreviations
   - `INT(11)` - For IDs and counts

2. **Full-Text Search:**
   - Uses MySQL `FULLTEXT` indexes on `txt` columns
   - `LIKE '%keyword%'` for pattern matching
   - Case-insensitive by default

3. **Character Encoding:**
   - Uses `utf8mb4` character set for full Unicode support
   - Collation: `utf8mb4_unicode_ci` for case-insensitive comparisons

4. **Primary Keys:**
   - Composite primary keys on `(book, chapter, verse)` or `(Book, Chapter, Verse)`
   - Efficient for verse lookups

## Indexing Recommendations

For optimal performance:

1. **Primary Keys:** Already defined on all tables
2. **Full-Text Indexes:** 
   - `bible_books.txt_tw` - Full-text index
   - `bible_search.txt` - Full-text index
   - `bible_multi_search.txt` - Full-text index
3. **Lookup Indexes:**
   - Consider adding indexes on `(book, chapter)` for range queries
   - Consider adding indexes on `book` alone for book-wide searches

## Database Design Characteristics Summary

The database design follows these key principles:

1. **Translation Separation**: Each translation is stored in its own dedicated table (`bible_book_{translation_code}`), preventing single tables from becoming too large and enabling better performance and maintenance.

2. **Main Table (`bible_books`)**: Centralizes management of core translations (CUVS/CUVT/KJV/Pinyin) and the like functionality in a single table, providing quick access to the most commonly used translations.

3. **Search Optimization**: Dedicated search tables (`bible_search` and `bible_multi_search`) are optimized for full-text search operations, separate from the main verse storage tables.

4. **Book Name Mapping**: The `bible_book` table provides comprehensive multi-language book name mappings, supporting lookups in English, Simplified Chinese, Traditional Chinese, and various abbreviations.

5. **Scalability**: The design allows for easy addition of new translations by creating new tables following the standard schema pattern.

This structure is well-suited for a Bible engine application, providing efficient access patterns for both verse lookups and keyword searches across multiple translations.

## Database Notes

This database is designed for **MariaDB/MySQL**. The current implementation uses:
- **MariaDB 10.5+** or **MySQL 8.0+**
- **UTF-8 encoding** (`utf8mb4`) for full Unicode support
- **InnoDB storage engine** (default) for ACID compliance
- **Full-text indexes** on search columns for efficient keyword searches

The database structure is optimized for:
- Fast verse lookups by book/chapter/verse
- Efficient full-text keyword searches
- Multi-translation support with separate tables
- Like functionality with atomic updates

## Additional Notes

- The database contains 66 books (Genesis through Revelation)
- Verse numbering follows standard Bible verse numbering
- Some translations may not have all verses (especially in `bible_book_wlc` which is Hebrew)
- The `likes` column in `bible_books` starts at 0 and increments with each like
- Translation tables use capitalized column names (`Book`, `Chapter`, `Verse`, `Scripture`) while main tables use lowercase
- The `bible_books` table combines multiple core translations in one row for efficient access
- Search tables use `TINYINT` for space efficiency (sufficient for book/chapter/verse ranges)

