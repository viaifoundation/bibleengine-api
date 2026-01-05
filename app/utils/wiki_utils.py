"""Wiki search and retrieval utilities."""
import httpx
from typing import Optional
from app.config import settings


async def search_wiki(query: str, page: int = 1) -> str:
    """Search wiki for content.
    
    Args:
        query: Search query
        page: Page number (default: 1)
        
    Returns:
        Wiki content or error message
    """
    page = max(1, page)
    block_size = 1800
    wiki_api_base = f"{settings.wiki_base_url.rstrip('/')}/api.php"
    
    # First, try to get the page content
    url = f"{wiki_api_base}?action=query&prop=revisions&rvprop=content|size&format=xml&redirects&titles={query}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # Parse XML response (simplified - in production, use proper XML parser)
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            
            # Extract content size
            size_elem = root.find('.//rev')
            size = int(size_elem.get('size', 0)) if size_elem is not None else 0
            
            # Extract text content
            txt = size_elem.text if size_elem is not None and size_elem.text else ''
            
            page_count = (size + block_size - 1) // block_size if size > 0 else 1
            page = min(page, page_count)
            
            # If content is too long, paginate
            if len(txt) > block_size:
                start = (page - 1) * block_size
                # Simple byte-based slicing (for UTF-8, this is approximate)
                txt = txt[start:start + block_size] + f"\n\n(第{page}/{page_count}页)"
            
            # If no content found, try search
            if not txt:
                search_url = f"{wiki_api_base}?action=query&list=search&format=xml&srlimit=max&srsearch={query}"
                search_response = await client.get(search_url)
                search_response.raise_for_status()
                
                search_root = ET.fromstring(search_response.text)
                search_results = search_root.findall('.//p')
                
                if search_results:
                    count = len(search_results)
                    txt = f"{query} 共搜索到{count} 个词条，请发送完整的词条标题查看内容：\n"
                    for result in search_results:
                        title = result.get('title', '')
                        txt += f"\n {title}\n"
                    
                    if len(txt) > 2000:
                        txt = txt[:2000] + "\n\n内容太长有删节"
                else:
                    txt = "没有查到搜索的词条，请更换关键词再搜索。"
            
            return txt
            
    except Exception as e:
        return f"Error fetching wiki content: {str(e)}"

