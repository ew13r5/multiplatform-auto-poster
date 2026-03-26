import os
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

# Read URLs from env with fallbacks for testing
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "sqlite+aiosqlite:///:memory:"
)
DATABASE_URL_SYNC = os.environ.get(
    "DATABASE_URL_SYNC", "sqlite:///:memory:"
)

async_engine = create_async_engine(DATABASE_URL, echo=False)
sync_engine = create_engine(DATABASE_URL_SYNC, echo=False)

AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)
SyncSessionLocal = sessionmaker(bind=sync_engine)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
