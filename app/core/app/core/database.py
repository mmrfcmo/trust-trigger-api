"""Database engine and session management."""
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
def _get_async_database_url() -> str:
    url = settings.database_url or os.environ.get("DATABASE_URL", "")
    if url:
        if url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url
    return "sqlite+aiosqlite:///./trust_trigger.db"
_database_url = _get_async_database_url()
engine = create_async_engine(_database_url, echo=settings.debug, future=True)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
class Base(DeclarativeBase):
    pass
async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
