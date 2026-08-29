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
