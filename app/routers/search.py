"""Search API router for verse search."""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.models import SearchResponse, VerseResult
from app.database import db
from app.utils.query_parser import parse_query
from app.utils.book_utils import get_book_short, get_book_english, get_book_chapter_count
from app.utils.text_utils import process_bible_text

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search_verses(
    q: Optional[str] = Query(None, description="Search query (verse reference or keywords)"),
    i: Optional[str] = Query(None, description="Verse index (book:chapter:verse, comma-separated)"),
    translation: Optional[str] = Query(None, description="Translation code (cuvs, cuvt, kjv, nasb, esv)"),
    b: Optional[int] = Query(None, description="Book filter (book ID, 1-66)"),
    m: Optional[int] = Query(0, description="Multi-verse flag (0 or 1)"),
    e: Optional[int] = Query(0, description="Context extension (number of verses before/after)"),
    strongs: Optional[bool] = Query(False, description="Include Strong's codes"),
    api: Optional[str] = Query("json", description="Response format (json, text, plain, html)")
):
    """Search for Bible verses by reference or keywords.
    
    Examples:
    - /v1/api/search?q=John+3:16
    - /v1/api/search?q=love&translation=kjv
    - /v1/api/search?i=43:3:16,43:3:17
    """
    try:
        results = []
        
        # Determine which translations to search
        translations = []
        if translation:
            translations = [t.strip() for t in translation.split(',')]
        else:
            # Default: search all available translations
            translations = ['cuvs', 'cuvt', 'kjv', 'nasb']
        
        if i:
            # Process index (verse references)
            verse_refs = [ref.strip() for ref in i.split(',')]
            for verse_ref in verse_refs:
                parts = verse_ref.split(':')
                if len(parts) >= 3:
                    book_id = int(parts[0])
                    chapter = int(parts[1])
                    verse = int(parts[2])
                    
                    # Fetch verses
                    verse_results = await fetch_verses(
                        book_id=book_id,
                        chapter=chapter,
                        verse_start=verse,
                        verse_end=verse,
                        translations=translations,
                        context=e or 0,
                        strongs=strongs
                    )
                    results.extend(verse_results)
        elif q:
            # Parse query
            parsed = parse_query(q)
            
            if parsed['type'] == 'reference':
                # Verse reference search
                book_id = parsed['book_id']
                chapter = parsed['chapter']
                verse_start = parsed['verse']
                verse_end = parsed['verse_end']
                
                # Apply book filter if specified
                if b and b != book_id:
                    return SearchResponse(
                        success=True,
                        data=[],
                        count=0,
                        query=q
                    )
                
                # Fetch verses
                verse_results = await fetch_verses(
                    book_id=book_id,
                    chapter=chapter,
                    verse_start=verse_start,
                    verse_end=verse_end,
                    translations=translations,
                    context=e or 0,
                    strongs=strongs
                )
                results.extend(verse_results)
            else:
                # Keyword search
                keywords = parsed['keywords']
                
                # Build search query
                verse_results = await search_by_keywords(
                    keywords=keywords,
                    book_filter=b,
                    translations=translations,
                    strongs=strongs
                )
                results.extend(verse_results)
        else:
            return SearchResponse(
                success=False,
                data=[],
                count=0,
                query=None
            )
        
        # Format response based on API format
        if api in ['text', 'plain']:
            # Return plain text (for compatibility)
            from fastapi.responses import PlainTextResponse
            text_output = "\n".join([f"{r.reference}: {r.text}" for r in results])
            return PlainTextResponse(content=text_output)
        elif api == 'html':
            # Return HTML (for compatibility)
            from fastapi.responses import HTMLResponse
            html_output = "".join([
                f"<p><strong>{r.reference}</strong>: {r.text}</p>\n"
                for r in results
            ])
            return HTMLResponse(content=html_output)
        else:
            # Default: JSON
            return SearchResponse(
                success=True,
                data=results,
                count=len(results),
                query=q or i
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def fetch_verses(
    book_id: int,
    chapter: int,
    verse_start: int,
    verse_end: int,
    translations: List[str],
    context: int = 0,
    strongs: bool = False
) -> List[VerseResult]:
    """Fetch verses from database.
    
    Args:
        book_id: Book ID (1-66)
        chapter: Chapter number
        verse_start: Starting verse number
        verse_end: Ending verse number
        translations: List of translation codes
        context: Number of verses before/after to include
        strongs: Include Strong's codes
        
    Returns:
        List of verse results
    """
    results = []
    
    # Calculate verse range with context
    verse_min = max(1, verse_start - context)
    verse_max = verse_end + context
    
    for trans in translations:
        # Map translation codes to table names
        table_map = {
            'cuvs': 'bible_books',
            'cuvt': 'bible_books',
            'kjv': 'bible_books',
            'nasb': 'bible_books',
            'esv': 'bible_books'
        }
        
        table = table_map.get(trans.lower(), 'bible_books')
        
        # Build query (table name is from whitelist, so safe)
        # Note: asyncpg doesn't support parameterized table names, so we validate against whitelist
        query = f"""
            SELECT book, chapter, verse, txt, likes
            FROM {table}
            WHERE book = $1
            AND chapter = $2
            AND verse >= $3
            AND verse <= $4
            ORDER BY verse
        """
        
        rows = await db.fetch_all(query, book_id, chapter, verse_min, verse_max)
        
        for row in rows:
            book_short = get_book_short(row['book'])
            reference = f"{book_short} {row['chapter']}:{row['verse']}"
            
            # Process text
            text = process_bible_text(
                text=row['txt'],
                queries=None,  # No highlighting for reference searches
                strongs=strongs
            )
            
            results.append(VerseResult(
                reference=reference,
                text=text,
                book=row['book'],
                chapter=row['chapter'],
                verse=row['verse'],
                translation=trans,
                likes=row.get('likes', 0)
            ))
    
    return results


async def search_by_keywords(
    keywords: List[str],
    book_filter: Optional[int],
    translations: List[str],
    strongs: bool = False
) -> List[VerseResult]:
    """Search verses by keywords.
    
    Args:
        keywords: List of search keywords
        book_filter: Optional book ID filter
        translations: List of translation codes
        strongs: Include Strong's codes
        
    Returns:
        List of verse results
    """
    results = []
    
    if not keywords:
        return results
    
    # Use bible_search table for keyword search
    # Build WHERE clause for keyword matching
    conditions = []
    params = []
    param_idx = 1
    
    for keyword in keywords:
        conditions.append(f"txt ILIKE ${param_idx}")
        params.append(f"%{keyword}%")
        param_idx += 1
    
    where_clause = " AND ".join(conditions)
    
    # Add book filter if specified
    if book_filter:
        where_clause = f"book = ${param_idx} AND {where_clause}"
        params.append(book_filter)
        param_idx += 1
    
    # Build query with parameterized conditions
    query = f"""
        SELECT DISTINCT book, chapter, verse, txt, likes
        FROM bible_search
        WHERE {where_clause}
        ORDER BY book, chapter, verse
        LIMIT 100
    """
    
    rows = await db.fetch_all(query, *params)
    
    for row in rows:
        book_short = get_book_short(row['book'])
        reference = f"{book_short} {row['chapter']}:{row['verse']}"
        
        # Process text with keyword highlighting
        text = process_bible_text(
            text=row['txt'],
            queries=keywords,
            strongs=strongs
        )
        
        results.append(VerseResult(
            reference=reference,
            text=text,
            book=row['book'],
            chapter=row['chapter'],
            verse=row['verse'],
            translation=None,  # Search table doesn't specify translation
            likes=row.get('likes', 0)
        ))
    
    return results

