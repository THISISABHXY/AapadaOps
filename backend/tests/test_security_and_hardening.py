"""AapadaOps Security, Hardening & Compliance Test Suite.

Verifies:
1. File upload defense: magic bytes, prohibited extension rejection, size limits.
2. HTTP security headers (nosniff, DENY, HSTS, XSS protection).
3. Citizen PII masking (reporter phone masking for unauthenticated/unprivileged viewers under DPDP Act).
4. RBAC enforcement (blocking unauthorized state transitions).
"""

import io
import uuid
import pytest
from httpx import AsyncClient
from app.models.incident import Incident, IncidentCategory, IncidentSeverity
from app.models.user import UserRole


@pytest.mark.asyncio
async def test_security_headers_present(client: AsyncClient):
    """Verify HTTP security defensive headers are injected on all endpoints."""
    res = await client.get("/health/live")
    assert res.status_code == 200
    assert res.headers.get("x-content-type-options") == "nosniff"
    assert res.headers.get("x-frame-options") == "DENY"
    assert "max-age=" in res.headers.get("strict-transport-security", "")
    assert res.headers.get("x-xss-protection") == "1; mode=block"


@pytest.mark.asyncio
async def test_file_upload_legitimate_jpeg_accepted(client: AsyncClient, auth_tokens):
    """Verify genuine JPEG image with valid magic bytes is accepted."""
    collector_token = auth_tokens[UserRole.DISTRICT_COLLECTOR]
    valid_jpeg_content = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00" + b"\x00" * 200

    res = await client.post(
        "/api/v1/evidence/upload",
        files={"file": ("field_photo.jpg", io.BytesIO(valid_jpeg_content), "image/jpeg")},
        headers={"Authorization": f"Bearer {collector_token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["file_name"] == "field_photo.jpg"
    assert len(data["sha256_hash"]) == 64


@pytest.mark.asyncio
async def test_file_upload_spoofed_mime_type_rejected(client: AsyncClient):
    """Verify non-image content spoofing an image MIME type is rejected by magic byte inspection."""
    fake_image_content = b"Non-binary text payload that does not contain valid image signatures"

    res = await client.post(
        "/api/v1/evidence/upload",
        files={"file": ("photo.jpg", io.BytesIO(fake_image_content), "image/jpeg")},
    )
    assert res.status_code == 400
    data = res.json()
    error_msg = data.get("error", {}).get("message", "") or data.get("detail", "")
    error_code = data.get("error", {}).get("code", "")
    assert "magic-byte" in error_msg.lower() or "signature" in error_msg.lower() or error_code == "MALICIOUS_FILE_SIGNATURE"


@pytest.mark.asyncio
async def test_file_upload_prohibited_extension_rejected(client: AsyncClient):
    """Verify forbidden extensions (.sh, .exe, .py) are rejected."""
    script_content = b"echo test script execution"

    res = await client.post(
        "/api/v1/evidence/upload",
        files={"file": ("script.sh", io.BytesIO(script_content), "application/x-sh")},
    )
    assert res.status_code == 400
    data = res.json()
    error_msg = data.get("error", {}).get("message", "") or data.get("detail", "")
    error_code = data.get("error", {}).get("code", "")
    assert "forbidden" in error_msg.lower() or "extension" in error_msg.lower() or error_code == "PROHIBITED_FILE_EXTENSION"


@pytest.mark.asyncio
async def test_file_upload_empty_file_rejected(client: AsyncClient):
    """Verify empty 0-byte file is rejected."""
    res = await client.post(
        "/api/v1/evidence/upload",
        files={"file": ("empty.jpg", io.BytesIO(b""), "image/jpeg")},
    )
    assert res.status_code == 400
    data = res.json()
    error_msg = data.get("error", {}).get("message", "") or data.get("detail", "")
    error_code = data.get("error", {}).get("code", "")
    assert "empty" in error_msg.lower() or error_code == "EMPTY_FILE"


@pytest.mark.asyncio
async def test_pii_phone_masking_for_unauthenticated_requests(client: AsyncClient, auth_tokens, db_session):
    """Verify citizen reporter phone numbers are masked for unauthenticated public requests."""
    code_suffix = uuid.uuid4().hex[:5].upper()
    incident = Incident(
        incident_code=f"INC-OD-2026-{code_suffix}",
        title="Cyclone Wind Damage to Roofs",
        description="Strong gusts blew tin roofs off several houses in village.",
        category=IncidentCategory.CYCLONE_WIND,
        reported_severity=IncidentSeverity.MEDIUM,
        latitude=19.8135,
        longitude=85.8312,
        district_name="Puri",
        village_name="Brahmagiri",
        reporter_name="Citizen Ramesh Behera",
        reporter_phone="+91 94370 12345",
    )
    db_session.add(incident)
    await db_session.commit()
    await db_session.refresh(incident)

    # 1. Unauthenticated request -> should mask phone number
    res = await client.get(f"/api/v1/incidents/{incident.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["reporter_phone"] != "+91 94370 12345"
    assert "XXXXX" in data["reporter_phone"]

    # 2. Authenticated Officer request (Super Admin) -> full phone number visible
    admin_token = auth_tokens[UserRole.SUPER_ADMIN]
    auth_res = await client.get(
        f"/api/v1/incidents/{incident.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert auth_res.status_code == 200
    auth_data = auth_res.json()
    assert auth_data["reporter_phone"] == "+91 94370 12345"


@pytest.mark.asyncio
async def test_rbac_unauthorized_state_transition_blocked(client: AsyncClient, auth_tokens, db_session):
    """Verify unauthorized role (e.g. Field Worker) is blocked from approving/verifying incidents."""
    fw_token = auth_tokens[UserRole.FIELD_WORKER]
    code_suffix = uuid.uuid4().hex[:5].upper()

    incident = Incident(
        incident_code=f"INC-OD-2026-{code_suffix}",
        title="Waterlogging in Market Area",
        description="Market street flooded with knee-deep water.",
        category=IncidentCategory.FLOOD,
        reported_severity=IncidentSeverity.LOW,
        latitude=20.2961,
        longitude=85.8245,
        district_name="Khordha",
        village_name="Bhubaneswar",
        reporter_name="Shopkeeper Panda",
        reporter_phone="+91 94370 55443",
    )
    db_session.add(incident)
    await db_session.commit()
    await db_session.refresh(incident)

    # Field Worker tries to transition incident directly to VERIFIED
    res = await client.patch(
        f"/api/v1/incidents/{incident.id}/status",
        json={"status": "VERIFIED", "notes": "Unauthorized worker bypass attempt"},
        headers={"Authorization": f"Bearer {fw_token}"},
    )
    assert res.status_code == 403
    data = res.json()
    error_msg = data.get("error", {}).get("message", "") or data.get("detail", "")
    assert "permission denied" in error_msg.lower() or "denied" in error_msg.lower()
