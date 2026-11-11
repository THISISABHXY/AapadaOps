"""Tests for Tactical Response Teams, Resource Allocations, and Task Dispatch."""

import pytest
from httpx import AsyncClient
from app.models.user import UserRole


@pytest.mark.asyncio
async def test_list_odrn_resources(client: AsyncClient):
    """Verify listing seeded ODRN resources."""
    response = await client.get("/api/v1/resources")
    assert response.status_code == 200
    resources = response.json()
    assert len(resources) >= 3
    categories = [r["category"] for r in resources]
    assert "POWER_BOAT" in categories


@pytest.mark.asyncio
async def test_find_nearest_teams(client: AsyncClient):
    """Verify spatial query locating closest response battalions."""
    # Near Kendrapara town: 20.5014, 86.4225
    response = await client.get("/api/v1/teams/nearest?latitude=20.5014&longitude=86.4225&limit=3")
    assert response.status_code == 200
    teams = response.json()
    assert len(teams) > 0
    # First match should be closest
    assert teams[0]["distance_meters"] <= teams[-1]["distance_meters"]


@pytest.mark.asyncio
async def test_task_dispatch_and_completion(client: AsyncClient, auth_tokens: dict):
    """Verify dispatching a tactical team with SLA hours and completing the mission."""
    # 1. Get an existing incident
    inc_list = await client.get("/api/v1/incidents?page_size=1")
    incident_id = inc_list.json()["items"][0]["id"]

    # 2. Dispatch task
    token = auth_tokens[UserRole.RESPONSE_COORDINATOR]
    dispatch_res = await client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "incident_id": incident_id,
            "title": "Evacuate 30 stranded villagers using power boats",
            "priority": "CRITICAL",
            "sla_hours": 3,
            "target_village": "Dangamal",
            "target_latitude": 20.7380,
            "target_longitude": 86.8420,
            "dispatch_notes": "Take inflatable rescue craft and child lifejackets.",
        },
    )
    assert dispatch_res.status_code == 201
    task_data = dispatch_res.json()
    task_id = task_data["id"]
    assert task_data["status"] == "PENDING"
    assert task_data["sla_hours"] == 3

    # 3. Field worker transitions task to IN_PROGRESS
    field_token = auth_tokens[UserRole.FIELD_WORKER]
    prog_res = await client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {field_token}"},
        json={"status": "IN_PROGRESS", "resolution_notes": "Team arrived at site, beginning boat rescue."},
    )
    assert prog_res.status_code == 200
    assert prog_res.json()["status"] == "IN_PROGRESS"

    # 4. Field worker completes task
    comp_res = await client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers={"Authorization": f"Bearer {field_token}"},
        json={"status": "COMPLETED", "resolution_notes": "All 30 citizens safely evacuated to Multipurpose Shelter."},
    )
    assert comp_res.status_code == 200
    assert comp_res.json()["status"] == "COMPLETED"
    assert comp_res.json()["completed_at"] is not None
