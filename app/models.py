"""Pydantic models for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class VerseResult(BaseModel):
    """Single verse result."""
    reference: str
    text: str
    book: int
    chapter: int
    verse: int
    translation: Optional[str] = None
    likes: Optional[int] = 0


class SearchResponse(BaseModel):
    """Search API response."""
    success: bool
    data: List[VerseResult]
    count: int
    query: Optional[str] = None


class WikiResponse(BaseModel):
    """Wiki API response."""
    success: bool
    data: Optional[str] = None
    error: Optional[str] = None
    query: Optional[str] = None


class LikeRequest(BaseModel):
    """Like API request."""
    book: int = Field(..., ge=1, le=66, description="Book ID (1-66)")
    chapter: int = Field(..., ge=1, description="Chapter number")
    verse: int = Field(..., ge=1, description="Verse number")


class LikeResponse(BaseModel):
    """Like API response."""
    success: bool
    likes: Optional[int] = None
    error: Optional[str] = None

