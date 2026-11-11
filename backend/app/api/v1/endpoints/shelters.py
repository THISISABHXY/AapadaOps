"""AapadaOps Cyclone Shelter Management API."""

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.api.v1.deps import require_roles
from app.models.shelter import CycloneShelter, ShelterStatus
from app.models.user import User, UserRole
from app.schemas.resource import ShelterCreate, ShelterResponse, ShelterUpdate
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/shelters", tags=["Cyclone Shelters"])


@router.get("", response_model=List[ShelterResponse])
async def list_shelters(
    district: Optional[str] = None,
    status: Optional[ShelterStatus] = None,
    db: AsyncSession = Depends(get_db),
):
    """List Multipurpose Cyclone Shelters (MCS) with live occupancy and logistics."""
    query = select(CycloneShelter)
    if district:
        query = query.where(CycloneShelter.district_name == district)
    if status:
        query = query.where(CycloneShelter.status == status)

    query = query.order_by(CycloneShelter.name.asc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ShelterResponse, status_code=status.HTTP_201_CREATED)
async def create_shelter(
    shelter_in: ShelterCreate,
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.DISTRICT_COLLECTOR)),
    db: AsyncSession = Depends(get_db),
):
    """Register a new Multipurpose Cyclone Shelter facility."""
    code = f"MCS-{shelter_in.district_name[:3].upper()}-{shelter_in.village[:3].upper()}"
    shelter = CycloneShelter(
        code=code,
        name=shelter_in.name,
        district_id=shelter_in.district_id,
        district_name=shelter_in.district_name,
        block_id=shelter_in.block_id,
        block_name=shelter_in.block_name,
        village=shelter_in.village,
        capacity=shelter_in.capacity,
        current_occupancy=0,
        latitude=shelter_in.latitude,
        longitude=shelter_in.longitude,
        has_power_backup=shelter_in.has_power_backup,
        generator_fuel_hours=shelter_in.generator_fuel_hours,
        drinking_water_days=shelter_in.drinking_water_days,
        has_medical_kit=shelter_in.has_medical_kit,
        caretaker_name=shelter_in.caretaker_name,
        caretaker_phone=shelter_in.caretaker_phone,
        status=ShelterStatus.ACTIVE,
    )
    db.add(shelter)
    await db.flush()

    await log_audit_event(
        db,
        action="CREATE_SHELTER",
        entity_type="SHELTER",
        entity_id=shelter.id,
        actor=current_user,
        description=f"Registered Cyclone Shelter {shelter.name} in {shelter.district_name} (Capacity: {shelter.capacity}).",
    )
    await db.commit()
    await db.refresh(shelter)
    return shelter


@router.patch("/{shelter_id}", response_model=ShelterResponse)
async def update_shelter(
    shelter_id: str,
    update_in: ShelterUpdate,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.RESPONSE_COORDINATOR,
            UserRole.FIELD_WORKER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Update shelter live occupancy, drinking water supply days, or medical status."""
    result = await db.execute(select(CycloneShelter).where(CycloneShelter.id == shelter_id))
    shelter = result.scalar_one_or_none()
    if not shelter:
        raise NotFoundError("CycloneShelter", shelter_id)

    update_data = update_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(shelter, field, val)

    # Check if full
    if shelter.current_occupancy >= shelter.capacity:
        shelter.status = ShelterStatus.FULL

    await db.commit()
    await db.refresh(shelter)
    return shelter

