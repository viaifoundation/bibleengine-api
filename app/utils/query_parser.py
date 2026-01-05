"""Query parser for verse references and keywords."""
import re
from typing import Dict, Optional, Tuple
from app.utils.book_utils import get_book_id, BOOK_SHORT


def parse_verse_reference(query: str) -> Optional[Dict[str, any]]:
    """Parse a verse reference query (e.g., "John 3:16", "Gen 1:1-3").
    
    Args:
        query: Query string
        
    Returns:
        Dictionary with book_id, chapter, verse, verse_end, or None if not a reference
    """
    query = query.strip()
    
    # Pattern: book name (with optional spaces) + chapter:verse or chapter:verse-verse2
    # Examples: "John 3:16", "Gen1:1", "约3:16", "1Cor 15:1-5"
    patterns = [
        # Standard format: "Book Chapter:Verse" or "Book Chapter:Verse-Verse2"
        r'^([^\d\s:]+)\s*(\d+):(\d+)(?:-(\d+))?$',
        # Format without space: "BookChapter:Verse"
        r'^([^\d:]+)(\d+):(\d+)(?:-(\d+))?$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, query, re.IGNORECASE)
        if match:
            book_name = match.group(1).strip()
            chapter = int(match.group(2))
            verse = int(match.group(3))
            verse_end = int(match.group(4)) if match.group(4) else verse
            
            # Try to find book ID
            book_id = get_book_id(book_name)
            if not book_id:
                # Try lowercase
                book_id = get_book_id(book_name.lower())
            if not book_id:
                # Try removing common suffixes
                book_id = get_book_id(book_name.rstrip('.,;'))
            
            if book_id:
                return {
                    'book_id': book_id,
                    'chapter': chapter,
                    'verse': verse,
                    'verse_end': verse_end,
                    'type': 'reference'
                }
    
    return None


def parse_keyword_query(query: str) -> Dict[str, any]:
    """Parse a keyword search query.
    
    Args:
        query: Query string
        
    Returns:
        Dictionary with keywords
    """
    # Split by spaces and filter empty strings
    keywords = [q.strip() for q in query.split() if q.strip()]
    
    return {
        'keywords': keywords,
        'type': 'keyword'
    }


def parse_query(query: str) -> Dict[str, any]:
    """Parse a query (verse reference or keyword).
    
    Args:
        query: Query string
        
    Returns:
        Parsed query dictionary
    """
    # First try to parse as verse reference
    result = parse_verse_reference(query)
    if result:
        return result
    
    # Otherwise, treat as keyword search
    return parse_keyword_query(query)

