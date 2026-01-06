"""Like API router for verse likes."""
from fastapi import APIRouter, HTTPException
from app.models import LikeRequest, LikeResponse
from app.database import db

router = APIRouter()


@router.post("/like", response_model=LikeResponse)
async def like_verse(request: LikeRequest):
    """Like a verse (increment like count).
    
    Examples:
    - POST /v1/api/like with body: {"book": 43, "chapter": 3, "verse": 16}
    """
    try:
        # Update likes count (MySQL doesn't support RETURNING, so we do it in two steps)
        update_query = """
            UPDATE bible_books
            SET likes = likes + 1
            WHERE book = %s AND chapter = %s AND verse = %s
        """
        
        await db.execute(
            update_query,
            request.book,
            request.chapter,
            request.verse
        )
        
        # Get updated likes count
        select_query = """
            SELECT likes
            FROM bible_books
            WHERE book = %s AND chapter = %s AND verse = %s
        """
        
        result = await db.fetch_one(
            select_query,
            request.book,
            request.chapter,
            request.verse
        )
        
        if result:
            return LikeResponse(
                success=True,
                likes=result['likes']
            )
        else:
            # Verse not found, but don't error - just return 0
            return LikeResponse(
                success=True,
                likes=0
            )
            
    except Exception as e:
        return LikeResponse(
            success=False,
            error=str(e)
        )

