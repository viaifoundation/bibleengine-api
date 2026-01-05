"""Wiki API router for MediaWiki integration."""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.models import WikiResponse
from app.utils.wiki_utils import search_wiki

router = APIRouter()


@router.get("/wiki", response_model=WikiResponse)
async def search_wiki_endpoint(
    q: str = Query(..., description="Wiki search query"),
    p: Optional[int] = Query(1, ge=1, description="Page number")
):
    """Search bible.world MediaWiki for content.
    
    Examples:
    - /v1/api/wiki?q=Jesus
    - /v1/api/wiki?q=Gospel&p=1
    """
    try:
        content = await search_wiki(q, p)
        
        return WikiResponse(
            success=True,
            data=content,
            query=q
        )
    except Exception as e:
        return WikiResponse(
            success=False,
            error=str(e),
            query=q
        )

