"""AapadaOps Districts & Geographic Boundaries API."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.district import District
from app.schemas.district import DistrictDetailResponse, DistrictResponse

router = APIRouter(prefix="/districts", tags=["Districts & Geography"])


@router.get("", response_model=List[DistrictResponse])
async def list_districts(db: AsyncSession = Depends(get_db)):
    """Retrieve all 30 districts of Odisha with disaster vulnerability tiers and coastal flags."""
    result = await db.execute(select(District).order_by(District.name.asc()))
    return result.scalars().all()


@router.get("/{district_id}", response_model=DistrictDetailResponse)
async def get_district_details(district_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve district details including all administrative blocks and Gram Panchayats."""
    result = await db.execute(
        select(District).options(selectinload(District.blocks)).where(District.id == district_id)
    )
    district = result.scalar_one_or_none()
    if not district:
        raise NotFoundError("District", district_id)
    return district

