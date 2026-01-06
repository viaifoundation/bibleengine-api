# API Reference

Complete API endpoint documentation for BibleEngine API v1.

## Base URL

```
http://localhost:8000/v1/api
```

## Authentication

Currently, the API does not require authentication. This may change in future versions.

## Response Format

All endpoints return JSON by default, unless otherwise specified via the `api` parameter.

### Success Response Format
```json
{
  "success": true,
  "data": [...],
  "count": 10,
  "query": "John 3:16"
}
```

### Error Response Format
```json
{
  "success": false,
  "error": "Error message here"
}
```

---

## Endpoints

### 1. Search Verses

**Endpoint:** `GET /v1/api/search`

Search for Bible verses by reference or keywords.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | No* | - | Search query (verse reference or keywords) |
| `i` | string | No* | - | Verse index (book:chapter:verse, comma-separated) |
| `translation` | string | No | - | Translation codes (comma-separated): cuvs, cuvt, kjv, nasb, esv |
| `b` | integer | No | - | Book filter (book ID, 1-66) |
| `m` | integer | No | 0 | Multi-verse flag (0 or 1) |
| `e` | integer | No | 0 | Context extension (number of verses before/after) |
| `strongs` | boolean | No | false | Include Strong's codes |
| `api` | string | No | "json" | Response format: json, text, plain, html |

*Either `q` or `i` must be provided.

#### Examples

**Verse Reference Search:**
```bash
GET /v1/api/search?q=John+3:16
GET /v1/api/search?q=Gen+1:1-3
GET /v1/api/search?q=约3:16&translation=cuvs
```

**Keyword Search:**
```bash
GET /v1/api/search?q=love&translation=kjv
GET /v1/api/search?q=faith+hope&b=43
```

**Verse Index Search:**
```bash
GET /v1/api/search?i=43:3:16,43:3:17
```

**With Context:**
```bash
GET /v1/api/search?q=John+3:16&e=2
```

**With Strong's Codes:**
```bash
GET /v1/api/search?q=John+3:16&strongs=true
```

#### Response

```json
{
  "success": true,
  "data": [
    {
      "reference": "John 3:16",
      "text": "For God so loved the world...",
      "book": 43,
      "chapter": 3,
      "verse": 16,
      "translation": "kjv",
      "likes": 42
    }
  ],
  "count": 1,
  "query": "John 3:16"
}
```

---

### 2. Search Wiki

**Endpoint:** `GET /v1/api/wiki`

Search bible.world MediaWiki for content.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | - | Wiki search query |
| `p` | integer | No | 1 | Page number (for paginated content) |

#### Examples

```bash
GET /v1/api/wiki?q=Jesus
GET /v1/api/wiki?q=Gospel&p=1
GET /v1/api/wiki?q=十字架
```

#### Response

```json
{
  "success": true,
  "data": "Wiki content here...",
  "query": "Jesus"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error fetching wiki content: ...",
  "query": "Jesus"
}
```

---

### 3. Like Verse

**Endpoint:** `POST /v1/api/like`

Increment the like count for a verse.

#### Request Body

```json
{
  "book": 43,
  "chapter": 3,
  "verse": 16
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `book` | integer | Yes | Book ID (1-66) |
| `chapter` | integer | Yes | Chapter number (≥1) |
| `verse` | integer | Yes | Verse number (≥1) |

#### Examples

```bash
POST /v1/api/like
Content-Type: application/json

{
  "book": 43,
  "chapter": 3,
  "verse": 16
}
```

#### Response

```json
{
  "success": true,
  "likes": 43
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message here"
}
```

---

## Response Formats

### JSON (Default)

Standard JSON response with structured data.

### Text/Plain

Returns plain text, one verse per line:
```
John 3:16: For God so loved the world...
John 3:17: For God did not send his Son...
```

### HTML

Returns HTML formatted verses:
```html
<p><strong>John 3:16</strong>: For God so loved the world...</p>
<p><strong>John 3:17</strong>: For God did not send his Son...</p>
```

---

## Translation Codes

| Code | Translation | Language |
|------|-------------|----------|
| `cuvs` | Chinese Union Version Simplified | Chinese (Simplified) |
| `cuvt` | Chinese Union Version Traditional | Chinese (Traditional) |
| `kjv` | King James Version | English |
| `nasb` | New American Standard Bible | English |
| `esv` | English Standard Version | English |

---

## Book IDs

Books are numbered 1-66:

- **1-39:** Old Testament (Genesis through Malachi)
- **40-66:** New Testament (Matthew through Revelation)

Common book IDs:
- 1 = Genesis
- 43 = John
- 66 = Revelation

See `app/utils/book_utils.py` for complete book name mappings.

---

## Error Codes

| HTTP Status | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Rate Limiting

Currently, there is no rate limiting. This may be implemented in future versions.

---

## Interactive Documentation

When running the API locally, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

These provide interactive API documentation with the ability to test endpoints directly.

