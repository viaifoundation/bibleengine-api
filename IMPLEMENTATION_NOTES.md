# Implementation Notes

This document provides implementation details and notes about the BibleEngine API FastAPI backend.

## Project Structure

```
bibleengine-api/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection and pool management
│   ├── models.py              # Pydantic models for API requests/responses
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── search.py          # Verse search endpoint
│   │   ├── wiki.py            # Wiki search endpoint
│   │   └── like.py            # Like verse endpoint
│   └── utils/
│       ├── book_utils.py      # Book name arrays and lookup functions
│       ├── query_parser.py    # Query parsing (verse references vs keywords)
│       ├── text_utils.py      # Text processing (encoding, formatting, Strong's)
│       └── wiki_utils.py      # MediaWiki integration
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── DATABASE_SCHEMA.md         # Database schema documentation
└── LICENSE                    # License file
```

## Key Features Implemented

### 1. Verse Search (`/v1/api/search`)

- **Verse Reference Search**: Supports formats like "John 3:16", "Gen 1:1-3", "约3:16"
- **Keyword Search**: Full-text search across verse content
- **Multi-Translation Support**: Search across CUVS, CUVT, KJV, NASB, ESV
- **Context Extension**: Include surrounding verses with `e` parameter
- **Multi-Verse Support**: Fetch verse ranges
- **Strong's Codes**: Optional inclusion of Strong's number links
- **Response Formats**: JSON (default), text, plain, HTML

### 2. Wiki Integration (`/v1/api/wiki`)

- **MediaWiki API Integration**: Fetches content from bible.world MediaWiki
- **Page Pagination**: Supports paginated content for long articles
- **Search Fallback**: If direct page not found, returns search results
- **Error Handling**: Graceful error handling with informative messages

### 3. Like Functionality (`/v1/api/like`)

- **POST Endpoint**: Increment like count for a verse
- **Verse Identification**: Uses book, chapter, verse parameters
- **Atomic Updates**: Database-level increment for thread safety

## Database Considerations

### Table Structure

The implementation assumes:
- `bible_books` table with columns: `book`, `chapter`, `verse`, `txt`, `likes`
- `bible_search` table for full-text search with columns: `book`, `chapter`, `verse`, `txt`

### Translation Storage

The current implementation assumes all translations are in the same `bible_books` table with a `translation` column, or separate tables per translation. You may need to adjust the `fetch_verses` function in `app/routers/search.py` based on your actual database schema.

### Full-Text Search

For optimal keyword search performance, consider:
- PostgreSQL full-text search indexes (`tsvector`, `gin` indexes)
- Or use a dedicated search engine like Elasticsearch for large-scale deployments

## Differences from PHP Implementation

1. **Async/Await**: Uses Python async/await for better concurrency
2. **Type Safety**: Pydantic models provide request/response validation
3. **Database**: PostgreSQL instead of MySQL (asyncpg instead of mysqli)
4. **API Structure**: RESTful endpoints with versioning (`/v1/api/...`)
5. **Error Handling**: Structured error responses with HTTP status codes

## Configuration

All configuration is done via environment variables (see `.env` file):
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Application secret key
- `WIKI_BASE_URL`: Base URL for MediaWiki API
- `ENVIRONMENT`: Environment name (development/production)

## Testing

To test the API locally:

1. Start the server: `uvicorn main:app --reload`
2. Visit `http://localhost:8000/docs` for interactive API documentation
3. Test endpoints:
   - `GET /v1/api/search?q=John+3:16`
   - `GET /v1/api/wiki?q=Jesus`
   - `POST /v1/api/like` with JSON body: `{"book": 43, "chapter": 3, "verse": 16}`

## Next Steps

1. **Database Migration**: Set up PostgreSQL database and migrate data from MySQL
2. **Testing**: Add unit tests and integration tests
3. **Caching**: Consider adding Redis for caching frequent queries
4. **Rate Limiting**: Add rate limiting to prevent abuse
5. **Authentication**: Add authentication if needed for protected endpoints
6. **Monitoring**: Add logging and monitoring (e.g., Sentry, Prometheus)

## Notes

- The book name lookup supports English, Chinese (Simplified/Traditional), and various abbreviations
- Text processing handles Strong's codes, formatting tags, and encoding issues
- The wiki integration uses MediaWiki's XML API format

