"""
src/database/db.py
──────────────────
Shared async PostgreSQL connection helper.
Reads DB config directly from environment variables.
"""

import os
import asyncpg
from contextlib import asynccontextmanager


def _db_url() -> str:
    host     = os.getenv("DB_HOST", "db")
    port     = os.getenv("DB_PORT", "5432")
    name     = os.getenv("DB_NAME", "hotel_room_service")
    user     = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "Admin")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


@asynccontextmanager
async def get_db_conn():
    conn = await asyncpg.connect(_db_url())
    try:
        yield conn
    finally:
        await conn.close()
