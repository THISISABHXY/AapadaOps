"""AapadaOps Response Teams and Tactical Forces API."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.api.v1.deps import require_roles
from app.models.team import ResponseTeam, TeamStatus
from app.models.user import User, UserRole
from app.schemas.resource import TeamCreate, TeamResponse, TeamUpdate
from app.services.spatial_service import find_nearest_response_teams
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/teams", tags=["Response Teams"])


@router.get("", response_model=List[TeamResponse])
async def list_teams(
    organization: Optional[str] = None,
    status: Optional[TeamStatus] = None,
    district: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List tactical response units (NDRF, ODRAF, Fire & Emergency Services, Civil Defence)."""
    query = select(ResponseTeam)
    if organization:
        query = query.where(ResponseTeam.organization == organization)
    if status:
        query = query.where(ResponseTeam.status == status)
    if district:
        query = query.where(ResponseTeam.current_district_name == district)

    query = query.order_by(ResponseTeam.name.asc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/nearest")
async def get_nearest_teams(
    latitude: float = Query(..., ge=17.0, le=23.5),
    longitude: float = Query(..., ge=81.0, le=88.0),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Find closest available tactical forces to an incident location using spatial distance."""
    ranked = await find_nearest_response_teams(db, latitude, longitude, limit)
    return [
        {
            "team": TeamResponse.model_validate(team),
            "distance_meters": round(dist, 1),
            "distance_km": round(dist / 1000.0, 2),
            "estimated_arrival_minutes": max(15, int(dist / 600.0)),  # Approx 36 km/h travel
        }
        for team, dist in ranked
    ]


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_in: TeamCreate,
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.RESPONSE_COORDINATOR)),
    db: AsyncSession = Depends(get_db),
):
    """Register a tactical response battalion or station unit."""
    code = f"{team_in.organization[:3].upper()}-{team_in.current_district_name[:3].upper()}-01"
    team = ResponseTeam(
        code=code,
        name=team_in.name,
        organization=team_in.organization,
        battalion=team_in.battalion,
        team_lead_name=team_in.team_lead_name,
        team_lead_phone=team_in.team_lead_phone,
        total_personnel=team_in.total_personnel,
        current_district_id=team_in.current_district_id,
        current_district_name=team_in.current_district_name,
        latitude=team_in.latitude,
        longitude=team_in.longitude,
        status=TeamStatus.STANDBY,
    )
    db.add(team)
    await db.flush()

    await log_audit_event(
        db,
        action="CREATE_TEAM",
        entity_type="TEAM",
        entity_id=team.id,
        actor=current_user,
        description=f"Registered response force {team.name} ({team.code}).",
    )
    await db.commit()
    await db.refresh(team)
    return team


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    team_in: TeamUpdate,
    current_user: User = Depends(
        require_roles(UserRole.SUPER_ADMIN, UserRole.RESPONSE_COORDINATOR, UserRole.FIELD_WORKER)
    ),
    db: AsyncSession = Depends(get_db),
):
    """Update team readiness status (STANDBY, DEPLOYED, RESTING) or GPS coordinates."""
    result = await db.execute(select(ResponseTeam).where(ResponseTeam.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise NotFoundError("ResponseTeam", team_id)

    update_data = team_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(team, field, val)

    await db.commit()
    await db.refresh(team)
    return team

