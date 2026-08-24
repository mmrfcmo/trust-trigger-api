"""Database engine and session management."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Force SQLite for now - Render free tier doesn't have PostgreSQL easily available
# To switch to PostgreSQL, set DATABASE_URL env var and add psycopg2 to requirements
_database_url = settings.async_database_url

# If the URL contains postgresql but psycopg2 isn't installed, fall back to SQLite
if "postgresql" in _database_url and "sqlite" not in _database_url:
    try:
        import psycopg2  # noqa
    except ImportError:
        _database_url = "sqlite+aiosqlite:///./trust_trigger.db"

engine = create_async_engine(_database_url, echo=settings.debug, future=True)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Yield an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()