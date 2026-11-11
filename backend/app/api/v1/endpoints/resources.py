"""AapadaOps ODRN Resource Inventory API."""

import random
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.api.v1.deps import require_roles
from app.models.resource import Resource, ResourceStatus, ResourceType
from app.models.user import User, UserRole
from app.schemas.resource import ResourceCreate, ResourceResponse, ResourceUpdate
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/resources", tags=["ODRN Resources"])


@router.get("", response_model=List[ResourceResponse])
async def list_resources(
    category: Optional[ResourceType] = None,
    status: Optional[ResourceStatus] = None,
    district: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List Odisha Disaster Resource Network equipment with status and district filtering."""
    query = select(Resource)
    if category:
        query = query.where(Resource.category == category)
    if status:
        query = query.where(Resource.status == status)
    if district:
        query = query.where(Resource.district_name == district)

    query = query.order_by(Resource.name.asc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    res_in: ResourceCreate,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.RESPONSE_COORDINATOR,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Register new equipment or emergency supply batch into the ODRN database."""
    res_code = f"ODRN-{res_in.category.value[:3]}-{random.randint(100, 999)}"
    resource = Resource(
        code=res_code,
        name=res_in.name,
        category=res_in.category,
        organization=res_in.organization,
        district_id=res_in.district_id,
        district_name=res_in.district_name,
        status=ResourceStatus.AVAILABLE,
        quantity=res_in.quantity,
        unit_of_measure=res_in.unit_of_measure,
        latitude=res_in.latitude,
        longitude=res_in.longitude,
        contact_person=res_in.contact_person,
        contact_phone=res_in.contact_phone,
    )
    db.add(resource)
    await db.flush()

    await log_audit_event(
        db,
        action="CREATE_RESOURCE",
        entity_type="RESOURCE",
        entity_id=resource.id,
        actor=current_user,
        description=f"Added resource {resource.name} ({resource.code}) in {resource.district_name}.",
    )
    await db.commit()
    await db.refresh(resource)
    return resource


@router.patch("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: str,
    update_in: ResourceUpdate,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.RESPONSE_COORDINATOR,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Update resource status (AVAILABLE, DISPATCHED, IN_USE, MAINTENANCE) or quantity."""
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    resource = result.scalar_one_or_none()
    if not resource:
        raise NotFoundError("Resource", resource_id)

    update_data = update_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(resource, field, val)

    await log_audit_event(
        db,
        action="UPDATE_RESOURCE",
        entity_type="RESOURCE",
        entity_id=resource.id,
        actor=current_user,
        description=f"Updated resource {resource.code} status to {resource.status.value}.",
        changes=update_data,
    )
    await db.commit()
    await db.refresh(resource)
    return resource
