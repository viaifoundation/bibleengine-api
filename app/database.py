"""Database connection and session management."""
import asyncpg
from typing import Optional
from app.config import settings


class Database:
    """Database connection manager."""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool."""
        # Parse PostgreSQL URL
        # Format: postgresql://user:password@host:port/database
        from urllib.parse import urlparse, unquote
        
        try:
            # Try to use the connection string directly first
            # asyncpg supports postgresql:// URLs, but we need to handle encoding
            parsed = urlparse(settings.database_url)
            
            if parsed.scheme and parsed.hostname:
                # Extract components
                user = unquote(parsed.username) if parsed.username else None
                password = unquote(parsed.password) if parsed.password else None
                host = parsed.hostname
                port = parsed.port if parsed.port else 5432
                database = unquote(parsed.path.lstrip('/')) if parsed.path else None
                
                self.pool = await asyncpg.create_pool(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database,
                    min_size=1,
                    max_size=10,
                )
            else:
                raise ValueError("Invalid DATABASE_URL format")
        except Exception as e:
            raise ValueError(f"Failed to connect to database: {str(e)}")
    
    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
    
    async def fetch_one(self, query: str, *args):
        """Execute a query and return one row."""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetch_all(self, query: str, *args):
        """Execute a query and return all rows."""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def execute(self, query: str, *args):
        """Execute a query (INSERT, UPDATE, DELETE)."""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)


# Global database instance
db = Database()

