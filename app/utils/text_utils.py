"""Text processing utilities for Bible text."""
import re
from typing import List, Optional


def fix_text_encoding(text: str) -> str:
    """Fix character encoding issues in text.
    
    Args:
        text: Text to fix
        
    Returns:
        Fixed text
    """
    if not text:
        return text
    
    # Remove common replacement characters
    replacement_chars = ['\xEF\xBF\xBD', 'ï¿½']
    for char in replacement_chars:
        text = text.replace(char, '')
    
    return text


def process_formatting_tags(text: str) -> str:
    """Process formatting tags (FI, FR, FO, RF, font color).
    
    Args:
        text: Text to process
        
    Returns:
        Processed text
    """
    # Red letter (words of Christ) - <FR>...</Fr>
    text = text.replace('<FR>', '<span style="color:red;">')
    text = text.replace('<Fr>', '</span>')
    
    # Orange letter (words of angels/divine speech) - <FO>...</Fo>
    text = text.replace('<FO>', '<span style="color:orange;">')
    text = text.replace('<Fo>', '</span>')
    
    # Italics (supplied words) - <FI>...</Fi>
    text = text.replace('<FI>', '<i>')
    text = text.replace('<Fi>', '</i>')
    
    # Footnotes/References - <RF>...</Rf>
    text = text.replace('<RF>', '<span class="footnote">')
    text = text.replace('<Rf>', '</span>')
    
    # Fix font color attributes
    text = re.sub(
        r'<font color=([^>\s"`]+)>',
        r'<font color="\1">',
        text,
        flags=re.IGNORECASE
    )
    
    return text


def process_strongs_codes(text: str) -> str:
    """Process Strong's codes - add as links in parentheses.
    
    Args:
        text: Text to process
        
    Returns:
        Processed text
    """
    # Process <WG...> format (Greek, long form) - supports optional suffix like "a"
    text = re.sub(
        r'([^\s<>]+)<WG(\d{1,4})([a-z]?)>',
        r'\1 (<a href="http://bible.fhl.net/new/s.php?N=0&k=\2" target="_blank">G\2\3</a>)',
        text,
        flags=re.IGNORECASE
    )
    
    # Process <WH...> format (Hebrew, long form) - supports optional suffix like "a"
    text = re.sub(
        r'([^\s<>]+)<WH(\d{1,4})([a-z]?)>',
        r'\1 (<a href="http://bible.fhl.net/new/s.php?N=1&k=\2" target="_blank">H\2\3</a>)',
        text,
        flags=re.IGNORECASE
    )
    
    # Process <G...> format (Greek, short form) - supports optional suffix like "a"
    text = re.sub(
        r'(?<!>)([^\s<>]+)<G(\d{1,4})([a-z]?)>',
        r'\1 (<a href="http://bible.fhl.net/new/s.php?N=0&k=\2" target="_blank">G\2\3</a>)',
        text,
        flags=re.IGNORECASE
    )
    
    # Process <H...> format (Hebrew, short form) - supports optional suffix like "a"
    text = re.sub(
        r'(?<!>)([^\s<>]+)<H(\d{1,4})([a-z]?)>',
        r'\1 (<a href="http://bible.fhl.net/new/s.php?N=1&k=\2" target="_blank">H\2\3</a>)',
        text,
        flags=re.IGNORECASE
    )
    
    return text


def remove_strongs_codes(text: str) -> str:
    """Remove Strong's codes from text.
    
    Args:
        text: Text to process
        
    Returns:
        Processed text
    """
    # Remove Strong's codes from within <sup> tags, then remove empty <sup> tags
    text = re.sub(
        r'<sup>([^<]*)<[WH]?[GH]\d{1,4}[a-z]?>(.*?)</sup>',
        r'<sup>\1\2</sup>',
        text,
        flags=re.IGNORECASE
    )
    
    # Remove <sup> tags that only contain Strong's codes (with optional whitespace)
    text = re.sub(
        r'<sup>\s*<[WH]?[GH]\d{1,4}[a-z]?>\s*</sup>',
        '',
        text,
        flags=re.IGNORECASE
    )
    
    # Remove standalone Strong's code tags (not in sup tags)
    text = re.sub(
        r'<[WH]?[GH]\d{1,4}[a-z]?>',
        '',
        text,
        flags=re.IGNORECASE
    )
    
    return text


def highlight_search_terms(text: str, queries: List[str]) -> str:
    """Highlight search terms in text.
    
    Args:
        text: Text to highlight
        queries: Array of search terms
        
    Returns:
        Text with highlighted terms
    """
    for query_word in queries:
        if query_word:
            text = text.replace(query_word, f"<strong>{query_word}</strong>")
    return text


def process_bible_text(
    text: str,
    queries: Optional[List[str]] = None,
    strongs: bool = False
) -> str:
    """Process Bible text: encoding, formatting, Strong's codes, highlighting.
    
    Args:
        text: Original text
        queries: Search terms for highlighting
        strongs: Enable Strong's codes
        
    Returns:
        Processed text
    """
    # Fix encoding
    text = fix_text_encoding(text)
    
    # Process formatting tags (always)
    text = process_formatting_tags(text)
    
    # Process or remove Strong's codes
    if strongs:
        text = process_strongs_codes(text)
    else:
        text = remove_strongs_codes(text)
    
    # Highlight search terms
    if queries:
        text = highlight_search_terms(text, queries)
    
    return text

