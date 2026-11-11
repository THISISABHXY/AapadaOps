"""AapadaOps Automated Test Suite Fixtures and Configuration."""

import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.main import app
from app.models.user import User, UserRole
from app.db.init_db import seed_database

# Test SQLite database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_suite.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create session-scoped event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create clean schema and seed reference data once for test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        await seed_database(session)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide isolated transactional session for individual tests."""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client overriding get_db dependency."""
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_tokens() -> dict:
    """Generate JWT tokens using actual seeded database user IDs."""
    async with TestSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        user_by_role = {u.role: u for u in users}

        tokens = {}
        for role, user in user_by_role.items():
            tokens[role] = create_access_token(
                subject=user.id,
                role=user.role.value,
                district=user.jurisdiction_district,
            )
        return tokens
