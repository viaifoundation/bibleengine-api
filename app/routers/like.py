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
        # Update likes count
        query = """
            UPDATE bible_books
            SET likes = likes + 1
            WHERE book = $1 AND chapter = $2 AND verse = $3
            RETURNING likes
        """
        
        result = await db.fetch_one(
            query,
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

