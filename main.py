"""Main FastAPI application for BibleEngine API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import db
from app.routers import search, wiki, like

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown)."""
    # Startup
    await db.connect()
    yield
    # Shutdown
    await db.disconnect()


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description="Next-generation backend API for Bible verse search, multi-translation access, wiki integration, and user interaction features.",
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,  # Disable docs in production
    redoc_url="/redoc" if settings.is_development else None,  # Disable redoc in production
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    search.router,
    prefix="/v1/api",
    tags=["search"]
)

app.include_router(
    wiki.router,
    prefix="/v1/api",
    tags=["wiki"]
)

app.include_router(
    like.router,
    prefix="/v1/api",
    tags=["like"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "BibleEngine API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "search": "/v1/api/search",
            "wiki": "/v1/api/wiki",
            "like": "/v1/api/like"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

