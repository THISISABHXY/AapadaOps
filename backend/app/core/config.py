"""AapadaOps Core Configuration Module."""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings resolved from environment variables."""

    # Project metadata
    APP_NAME: str = "AapadaOps"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", 8000))

    # Security & Tokens
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "dev-insecure-secret-key-replace-in-production-aapadaops-2026-odisha"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ]

    # Database connection string
    # Defaults to SQLite async fallback for seamless zero-dependency developer onboarding
    # Production uses PostgreSQL + PostGIS: postgresql+asyncpg://user:pass@localhost:5432/aapadaops
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///./aapadaops_dev.db"
    )

    # PostGIS Spatial Reference System Identifier (SRID 4326 = WGS 84 GPS standard)
    DEFAULT_SRID: int = 4326

    # Odisha Geo-bounds & Coordinates
    ODISHA_CENTER_LAT: float = 20.9517
    ODISHA_CENTER_LNG: float = 85.0985
    ODISHA_BOUNDS: dict = {
        "min_lat": 17.78,
        "max_lat": 22.57,
        "min_lng": 81.37,
        "max_lng": 87.53,
    }

    # Upload configuration
    UPLOAD_DIR: str = os.getenv(
        "UPLOAD_DIR", str(Path(__file__).resolve().parent.parent / "uploads")
    )
    MAX_FILE_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    ALLOWED_UPLOAD_MIME_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "application/pdf",
        "audio/mpeg",
        "audio/ogg",
        "audio/wav",
    ]

    # Rate limiting configuration (requests per minute per IP)
    DEFAULT_RATE_LIMIT_PER_MINUTE: int = 120
    SUBMIT_RATE_LIMIT_PER_MINUTE: int = 15

    # External APIs (Clearly flagged simulated / mock when keys are unset)
    IMD_API_KEY: str = os.getenv("IMD_API_KEY", "")
    IMD_API_BASE_URL: str = os.getenv(
        "IMD_API_BASE_URL", "https://mausam.imd.gov.in/api/v1"
    )
    CWC_API_KEY: str = os.getenv("CWC_API_KEY", "")
    CWC_API_BASE_URL: str = os.getenv(
        "CWC_API_BASE_URL", "https://ffs.india-water.gov.in/api"
    )

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.DATABASE_URL.lower()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
