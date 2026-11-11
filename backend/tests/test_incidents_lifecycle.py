"""Tests for Incident Submission, AI Auto-Triage, and Lifecycle State Machine."""

import pytest
from httpx import AsyncClient
from app.models.incident import IncidentCategory, IncidentSeverity, IncidentStatus
from app.models.user import UserRole


@pytest.mark.asyncio
async def test_create_incident_valid_coordinates(client: AsyncClient):
    """Verify incident creation within Odisha bounds runs AI triage and generates code."""
    payload = {
        "title": "Severe Waterlogging and Submerged Houses in Dhamra",
        "description": "Brahmani flood water entering low-lying houses in Dhamra village. Around 25 people are stranded on rooftops needing immediate rescue.",
        "category": "FLOOD",
        "reported_severity": "HIGH",
        "district_name": "Bhadrak",
        "village_name": "Dhamra",
        "latitude": 20.8010,
        "longitude": 86.9530,
        "reporter_name": "Priyabrata Nayak",
        "reporter_phone": "+91 94371 55667",
        "estimated_affected_people": 25,
        "stranded_count": 25,
    }
    response = await client.post("/api/v1/incidents", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["incident_code"].startswith("INC-OD-2026-")
    assert data["status"] == "SUBMITTED"
    assert data["ai_confidence_score"] > 0.6
    assert data["stranded_count"] == 25


@pytest.mark.asyncio
async def test_create_incident_out_of_bounds_rejected(client: AsyncClient):
    """Verify coordinates outside Odisha are strictly rejected with 400."""
    payload = {
        "title": "Incident outside Odisha",
        "description": "Report submitted from Delhi coordinates.",
        "category": "OTHER",
        "reported_severity": "LOW",
        "district_name": "Kendrapara",
        "latitude": 28.6139,  # Delhi latitude
        "longitude": 77.2090,  # Delhi longitude
        "reporter_name": "Invalid Tester",
        "reporter_phone": "+91 94370 00000",
    }
    response = await client.post("/api/v1/incidents", json=payload)
    # Pydantic or custom boundary validator rejects coordinates
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_incident_state_machine_valid_transition(client: AsyncClient, auth_tokens: dict):
    """Verify state transition from SUBMITTED -> NEEDS_VERIFICATION -> VERIFIED."""
    # 1. Create incident
    create_res = await client.post(
        "/api/v1/incidents",
        json={
            "title": "Road blocked by fallen banyan tree on NH-16",
            "description": "Major highway road blocked by storm debris.",
            "category": "ROAD_BLOCK",
            "reported_severity": "MEDIUM",
            "district_name": "Jajpur",
            "latitude": 20.8500,
            "longitude": 86.3333,
            "reporter_name": "NHAI Patrol",
            "reporter_phone": "+91 94371 11222",
        },
    )
    assert create_res.status_code == 201
    incident_id = create_res.json()["id"]

    token = auth_tokens[UserRole.INCIDENT_VERIFICATION_OFFICER]

    # 2. Transition SUBMITTED -> NEEDS_VERIFICATION
    t1_res = await client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "NEEDS_VERIFICATION", "notes": "Dispatched local revenue inspector to verify."},
    )
    assert t1_res.status_code == 200
    assert t1_res.json()["status"] == "NEEDS_VERIFICATION"

    # 3. Transition NEEDS_VERIFICATION -> VERIFIED
    t2_res = await client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "VERIFIED", "verified_priority": "HIGH", "notes": "Verified by ground RI."},
    )
    assert t2_res.status_code == 200
    assert t2_res.json()["status"] == "VERIFIED"
    assert t2_res.json()["is_verified"] is True


@pytest.mark.asyncio
async def test_incident_state_machine_invalid_transition_rejected(client: AsyncClient, auth_tokens: dict):
    """Verify transitioning SUBMITTED directly to CLOSED is rejected with HTTP 400."""
    create_res = await client.post(
        "/api/v1/incidents",
        json={
            "title": "Electrical short circuit at substation",
            "description": "Power failure across 3 wards.",
            "category": "POWER_FAILURE",
            "reported_severity": "MEDIUM",
            "district_name": "Cuttack",
            "latitude": 20.4625,
            "longitude": 85.8828,
            "reporter_name": "TPCODL Staff",
            "reporter_phone": "+91 94371 88990",
        },
    )
    incident_id = create_res.json()["id"]

    token = auth_tokens[UserRole.SUPER_ADMIN]
    # Attempt invalid jump: SUBMITTED -> CLOSED
    bad_res = await client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "CLOSED", "notes": "Attempting illegal skip"},
    )
    assert bad_res.status_code == 400
    assert "Invalid incident lifecycle transition" in bad_res.json()["error"]["message"]
