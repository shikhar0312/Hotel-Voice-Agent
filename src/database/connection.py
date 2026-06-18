import asyncpg
from contextlib import asynccontextmanager
from typing import Optional
from src.config.settings import settings
from src.utils.logger import logger

class DatabasePool:
    _instance = None
    _pool: Optional[asyncpg.Pool] = None
    _loop = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize_pool(self):
        import asyncio
        current_loop = asyncio.get_event_loop()
        
        if self._pool is not None and self._loop != current_loop:
            try:
                await self._pool.close()
            except:
                pass
            self._pool = None
        
        if self._pool is None:
            try:
                self._pool = await asyncpg.create_pool(
                    host=settings.DB_HOST,
                    port=settings.DB_PORT,
                    database=settings.DB_NAME,
                    user=settings.DB_USER,
                    password=settings.DB_PASSWORD,
                    min_size=1,
                    max_size=10
                )
                self._loop = current_loop
                logger.info(f"Async database connection pool created for {settings.DB_NAME}")
            except Exception as e:
                logger.error(f"Failed to create async database connection pool: {e}")
                raise
    
    @asynccontextmanager
    async def get_connection(self):
        if self._pool is None:
            await self.initialize_pool()
        
        conn = None
        try:
            conn = await self._pool.acquire()
            yield conn
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                await self._pool.release(conn)
    
    async def close_all_connections(self):
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("All async database connections closed")

database_pool = DatabasePool()
