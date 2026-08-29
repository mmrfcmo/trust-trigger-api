"""Database engine and session management."""
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
def _get_async_database_url() -> str:
    """Get the async database URL, handling PostgreSQL vs SQLite.

    Render sets DATABASE_URL in environment. We need to convert
    postgresql:// to postgresql+asyncpg:// for async support.
    """
    url = settings.database_url or os.environ.get("DATABASE_URL", "")

    if url:
        # Convert postgresql:// to postgresql+asyncpg://
        if url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    # Fallback to SQLite for local dev
    return "sqlite+aiosqlite:///./trust_trigger.db"

_database_url = _get_async_database_url()

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

Only this, nothing else. Then click Commit changes.

Now you'll also need to fix config.py — go to github.com/mmrfcmo/trust-trigger-api/blob/main/app/core/config.py

Delete everything and paste just this:

"""Application configuration using Pydantic Settings."""
from pydantic import BaseSettings
from typing import Optional
class Settings(BaseSettings):
    app_name: str = "Trust Trigger Agency"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_key: Optional[str] = None

    jwt_secret_key: str = "change-me-to-a-random-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440

    openai_api_key: Optional[str] = None
    google_places_api_key: Optional[str] = None

    gmail_email: Optional[str] = None
    gmail_app_password: Optional[str] = None
    owner_email: str = "mmr1979@hotmail.co.uk"

    cors_origins: str = "https://srv16.aisoftllc.com,http://localhost:3000,http://localhost:5173"

    @property
    def cors_origin_list(self) -> list:
        origins = [o.strip() for o in self.cors_origins.split(",")]
        if "*" in origins:
            return ["*"]
        return origins

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
