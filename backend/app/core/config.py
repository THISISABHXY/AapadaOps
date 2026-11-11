"""AapadaOps Core Configuration Module."""

import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings resolved from environment variables."""

    # Project metadata
    APP_NAME: str = "AapadaOps"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Security & Tokens
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "dev-insecure-secret-key-replace-in-production-aapadaops-2026"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # CORS origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Database connection string
    # Defaults to SQLite async fallback for seamless zero-dependency developer onboarding
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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
