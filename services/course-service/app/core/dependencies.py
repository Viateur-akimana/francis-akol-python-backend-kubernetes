"""FastAPI dependencies for dependency injection."""

from typing import Generator

from app.db.session import async_session
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db() -> Generator[AsyncSession, None, None]:
    """
    Dependency to get database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
