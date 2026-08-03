"""Central configuration, loaded from environment variables.

In containers these come from docker-compose `environment:` / an `.env` file;
locally they fall back to the sensible defaults below.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    app_name: str = "Campus Event Portal"
    environment: str = "development"
    api_prefix: str = "/api"

    # --- Database ---
    database_url: str = "postgresql://postgres:postgres@db:5432/campus"

    # --- JWT auth ---
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24h

    # --- File uploads (event banners) ---
    upload_dir: str = "/app/uploads"
    max_upload_bytes: int = 5 * 1024 * 1024  # 5 MB

    # --- Seeded admin account (created on first startup) ---
    admin_email: str = "admin@campus.edu"
    admin_password: str = "admin123"
    admin_name: str = "Portal Admin"

    # --- CORS (used in dev; in prod Nginx makes this same-origin) ---
    cors_origins: str = "http://localhost:5173,http://localhost"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached so the file/env is parsed once per process."""
    return Settings()


settings = get_settings()
