"""Tests for Authentication, Password Hashing, JWT, and Role-Based Access Control."""

import pytest
from httpx import AsyncClient
from app.models.user import UserRole


@pytest.mark.asyncio
async def test_root_and_health_endpoints(client: AsyncClient):
    """Verify system root metadata and health check probes."""
    root_res = await client.get("/")
    assert root_res.status_code == 200
    assert root_res.json()["service"] == "AapadaOps"

    live_res = await client.get("/healthz")
    assert live_res.status_code == 200
    assert live_res.json()["status"] == "LIVE"

    ready_res = await client.get("/health/ready")
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "READY"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Verify login with seeded super admin credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@aapadaops.odisha.gov.in", "password": "Password@123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["role"] == "SUPER_ADMIN"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    """Verify 401 Unauthorized returned on wrong credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@aapadaops.odisha.gov.in", "password": "WrongPassword999"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_rbac_super_admin_access(client: AsyncClient, auth_tokens: dict):
    """Verify Super Administrator can access administrative users endpoint."""
    token = auth_tokens[UserRole.SUPER_ADMIN]
    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_rbac_observer_restricted(client: AsyncClient, auth_tokens: dict):
    """Verify Observer role is forbidden from creating new users."""
    token = auth_tokens[UserRole.OBSERVER]
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "illegal@aapadaops.odisha.gov.in",
            "password": "Password@123",
            "full_name": "Illegal User",
            "role": "FIELD_WORKER",
        },
    )
    assert response.status_code == 403
