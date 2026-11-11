"""AapadaOps Geospatial Services & Distance Calculations."""

import math
from typing import List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.incident import Incident
from app.models.team import ResponseTeam
from app.models.shelter import CycloneShelter


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two GPS coordinates in meters."""
    R = 6371000.0  # Earth's mean radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def is_coordinate_in_odisha(lat: float, lng: float) -> bool:
    """Validate whether GPS coordinate falls within the geographic bounds of Odisha."""
    bounds = settings.ODISHA_BOUNDS
    return (
        bounds["min_lat"] <= lat <= bounds["max_lat"]
        and bounds["min_lng"] <= lng <= bounds["max_lng"]
    )


async def find_nearby_incidents(
    db: AsyncSession,
    latitude: float,
    longitude: float,
    radius_meters: float = 1000.0,
    district_name: str = None,
) -> List[Tuple[Incident, float]]:
    """Query incidents within specified radius meters using spatial geodesic distance."""
    # Approximate bounding box degrees to quickly filter before accurate haversine
    # 1 deg latitude ≈ 111,000 meters
    delta_deg = (radius_meters / 111000.0) * 1.5

    query = select(Incident).where(
        Incident.latitude.between(latitude - delta_deg, latitude + delta_deg),
        Incident.longitude.between(longitude - delta_deg, longitude + delta_deg),
    )
    if district_name:
        query = query.where(Incident.district_name == district_name)

    result = await db.execute(query)
    candidates = result.scalars().all()

    matches = []
    for inc in candidates:
        dist = haversine_distance_meters(latitude, longitude, inc.latitude, inc.longitude)
        if dist <= radius_meters:
            matches.append((inc, dist))

    matches.sort(key=lambda x: x[1])
    return matches


async def find_nearest_response_teams(
    db: AsyncSession,
    target_lat: float,
    target_lng: float,
    limit: int = 5,
) -> List[Tuple[ResponseTeam, float]]:
    """Locate the closest tactical response forces to an emergency coordinate."""
    result = await db.execute(select(ResponseTeam))
    teams = result.scalars().all()

    ranked = []
    for team in teams:
        dist = haversine_distance_meters(target_lat, target_lng, team.latitude, team.longitude)
        ranked.append((team, dist))

    ranked.sort(key=lambda x: x[1])
    return ranked[:limit]

