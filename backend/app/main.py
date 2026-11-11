"""AapadaOps Backend Application Entrypoint."""

import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db, engine, Base

# Setup logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("AapadaOps")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AapadaOps: Complete AI-powered Disaster-Response Coordination Platform for Odisha. "
        "Engineered for the Odisha State Disaster Management Authority (OSDMA) and State Emergency Operations Center (EOC)."
    ),
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    """Application startup initialization hook."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.APP_ENV}]")
    async with engine.begin() as conn:
        # Create tables for local development SQLite fallback if required
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema verification complete.")


@app.on_event("shutdown")
async def on_shutdown():
    """Application shutdown cleanup hook."""
    logger.info("Disposing database connection pool...")
    await engine.dispose()
    logger.info(f"{settings.APP_NAME} shutdown complete.")


@app.get("/", tags=["System"])
async def root():
    """Root metadata endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "description": "Odisha Disaster-Response Coordination Platform (OSDMA / EOC)",
        "docs": "/docs" if not settings.is_production else "disabled",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/healthz", tags=["System"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """System health check verifying database and service liveness."""
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error(f"Database healthcheck failed: {exc}")
        db_status = f"unhealthy: {str(exc)}"

    return {
        "status": "UP" if db_status == "healthy" else "DEGRADED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION,
    }


# Placeholder for API v1 Router Registration
# from app.api.v1.api import api_router
# app.include_router(api_router, prefix="/api/v1")
