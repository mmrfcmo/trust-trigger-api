"""Application configuration using Pydantic Settings."""
from pydantic import BaseSettings  # pydantic v1
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Trust Trigger Agency"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_key: Optional[str] = None

    # Auth
    jwt_secret_key: str = "change-me-to-a-random-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440

    # OpenAI
    openai_api_key: Optional[str] = None

    # Google Places
    google_places_api_key: Optional[str] = None

    # Security
    cors_origins: str = "https://srv16.aisoftllc.com,http://localhost:3000,http://localhost:5173"

    @property
    def cors_origin_list(self) -> list:
        origins = [o.strip() for o in self.cors_origins.split(",")]
        if "*" in origins:
            return ["*"]
        return origins

    @property
    def async_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return "sqlite+aiosqlite:///./trust_trigger.db"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()