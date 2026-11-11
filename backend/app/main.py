"""AapadaOps Backend Application Entrypoint."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, Base, engine, get_db
from app.core.exceptions import AppException, app_exception_handler
from app.db.init_db import seed_database
# Import models to ensure all metadata is registered with declarative Base
import app.models  # noqa: F401

# Setup logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("AapadaOps")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI modern lifespan context manager for startup and shutdown."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.APP_ENV}]")

    # Initialize tables and seed reference data
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema verification complete.")

    async with AsyncSessionLocal() as session:
        try:
            await seed_database(session)
        except Exception as exc:
            logger.error(f"Error seeding database: {exc}")
            await session.rollback()

    logger.info("System operational readiness verified.")
    yield
    logger.info("Disposing database connection pool...")
    await engine.dispose()
    logger.info(f"{settings.APP_NAME} shutdown complete.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AapadaOps: Complete AI-powered Disaster-Response Coordination Platform for Odisha. "
        "Engineered for the Odisha State Disaster Management Authority (OSDMA) and State Emergency Operations Center (EOC)."
    ),
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists and mount for static file serving
upload_path = Path(settings.UPLOAD_DIR)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")


@app.get("/", tags=["System"])
async def root():
    """Root metadata endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "description": "Odisha Disaster-Response Coordination Platform (OSDMA / EOC)",
        "docs": "/docs" if not settings.is_production else "disabled",
        "api_v1": "/api/v1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/healthz", tags=["System"])
@app.get("/health/live", tags=["System"])
async def liveness_probe():
    """Liveness probe verifying that the application process is running."""
    return {"status": "LIVE", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/health/ready", tags=["System"])
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    """Readiness probe verifying database connectivity and operational state."""
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error(f"Database readiness check failed: {exc}")
        db_status = f"unhealthy: {str(exc)}"

    is_ready = db_status == "healthy"
    return {
        "status": "READY" if is_ready else "NOT_READY",
        "database": db_status,
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Register API v1 Router
app.include_router(api_router, prefix="/api/v1")
