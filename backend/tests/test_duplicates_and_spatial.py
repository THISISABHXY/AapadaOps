"""Tests for Spatial Distance Calculations, Duplicate Detection, and Incident Merging."""

import pytest
from httpx import AsyncClient
from app.models.user import UserRole
from app.services.spatial_service import haversine_distance_meters, is_coordinate_in_odisha


def test_haversine_distance():
    """Verify haversine distance calculation between Bhubaneswar and Cuttack (~25-28km)."""
    # Bhubaneswar: 20.2961, 85.8245
    # Cuttack: 20.4625, 85.8828
    dist = haversine_distance_meters(20.2961, 85.8245, 20.4625, 85.8828)
    assert 15000 < dist < 25000  # Expected ~19.5 km straight-line great circle


def test_coordinate_in_odisha():
    """Verify coordinate bounding checks for Odisha."""
    assert is_coordinate_in_odisha(20.5014, 86.4225) is True  # Kendrapara
    assert is_coordinate_in_odisha(19.8135, 85.8312) is True  # Puri
    assert is_coordinate_in_odisha(13.0827, 80.2707) is False  # Chennai (outside)


@pytest.mark.asyncio
async def test_duplicate_incident_clustering_and_merge(client: AsyncClient, auth_tokens: dict):
    """Verify that reports within 500m are clustered and can be merged into a master incident."""
    # 1. Primary incident
    res1 = await client.post(
        "/api/v1/incidents",
        json={
            "title": "Severe Saline Inundation in Rajnagar Ward 4",
            "description": "Saline water gushing into village, 30 people trapped.",
            "category": "FLOOD",
            "reported_severity": "HIGH",
            "district_name": "Kendrapara",
            "village_name": "Rajnagar",
            "latitude": 20.5750,
            "longitude": 86.6850,
            "reporter_name": "Villager A",
            "reporter_phone": "+91 94371 00001",
            "stranded_count": 30,
        },
    )
    assert res1.status_code == 201
    primary_id = res1.json()["id"]

    # 2. Duplicate incident nearby (within 200m)
    res2 = await client.post(
        "/api/v1/incidents",
        json={
            "title": "Water entered houses in Rajnagar Ward 4",
            "description": "Flood water entering houses, people trapped on roof.",
            "category": "FLOOD",
            "reported_severity": "HIGH",
            "district_name": "Kendrapara",
            "village_name": "Rajnagar",
            "latitude": 20.5760,  # ~110m away
            "longitude": 86.6855,
            "reporter_name": "Villager B",
            "reporter_phone": "+91 94371 00002",
            "stranded_count": 15,
        },
    )
    assert res2.status_code == 201
    duplicate_id = res2.json()["id"]

    # 3. Merge duplicate into master
    token = auth_tokens[UserRole.INCIDENT_VERIFICATION_OFFICER]
    merge_res = await client.post(
        "/api/v1/duplicates/merge",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "master_incident_id": primary_id,
            "duplicate_incident_ids": [duplicate_id],
            "merge_notes": "Verified same geographic cluster on ground.",
        },
    )
    assert merge_res.status_code == 200
    merged_data = merge_res.json()
    assert merged_data["id"] == primary_id
    # Stranded count should be aggregated: 30 + 15 = 45
    assert merged_data["stranded_count"] == 45

    # Verify duplicate incident status is now DUPLICATE
    dup_check = await client.get(f"/api/v1/incidents/{duplicate_id}")
    assert dup_check.status_code == 200
    assert dup_check.json()["status"] == "DUPLICATE"
    assert dup_check.json()["is_duplicate"] is True
