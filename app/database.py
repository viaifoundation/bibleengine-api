"""Database connection and session management."""
import aiomysql
from typing import Optional, Dict, Any, List
from app.config import settings


class Database:
    """Database connection manager for MariaDB/MySQL."""
    
    def __init__(self):
        self.pool: Optional[aiomysql.Pool] = None
    
    async def connect(self):
        """Create database connection pool."""
        # Parse MySQL/MariaDB URL
        # Format: mysql://user:password@host:port/database
        from urllib.parse import urlparse, unquote
        
        try:
            parsed = urlparse(settings.database_url)
            
            if parsed.scheme and parsed.hostname:
                # Extract components
                user = unquote(parsed.username) if parsed.username else None
                password = unquote(parsed.password) if parsed.password else None
                host = parsed.hostname
                port = parsed.port if parsed.port else 3306
                database = unquote(parsed.path.lstrip('/')) if parsed.path else None
                
                self.pool = await aiomysql.create_pool(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    db=database,
                    minsize=1,
                    maxsize=10,
                    charset='utf8mb4',
                    autocommit=True
                )
            else:
                raise ValueError("Invalid DATABASE_URL format")
        except Exception as e:
            raise ValueError(f"Failed to connect to database: {str(e)}")
    
    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Execute a query and return one row as a dictionary."""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, args)
                return await cursor.fetchone()
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute a query and return all rows as a list of dictionaries."""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, args)
                return await cursor.fetchall()
    
    async def execute(self, query: str, *args) -> int:
        """Execute a query (INSERT, UPDATE, DELETE) and return affected rows."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                affected = await cursor.execute(query, args)
                await conn.commit()
                return affected


# Global database instance
db = Database()

