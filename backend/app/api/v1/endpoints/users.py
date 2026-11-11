"""AapadaOps User Management API Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import get_password_hash
from app.api.v1.deps import PaginationParams, require_roles
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
async def list_users(
    role: Optional[UserRole] = None,
    district: Optional[str] = None,
    search: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.DISTRICT_COLLECTOR)),
    db: AsyncSession = Depends(get_db),
):
    """List operational users with filtering by role, district, and name."""
    query = select(User)
    if role:
        query = query.where(User.role == role)
    if district:
        query = query.where(User.jurisdiction_district == district)
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                User.full_name.ilike(search_filter),
                User.email.ilike(search_filter),
                User.phone_number.ilike(search_filter),
            )
        )

    query = query.order_by(User.created_at.desc()).offset(pagination.skip).limit(pagination.limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.DISTRICT_COLLECTOR)),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve user account details by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User", user_id)
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.DISTRICT_COLLECTOR)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new official user account with specific role and district."""
    result = await db.execute(select(User).where(User.email == user_in.email.lower()))
    if result.scalar_one_or_none():
        raise ConflictError(f"User with email '{user_in.email}' already exists.")

    new_user = User(
        email=user_in.email.lower(),
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        phone_number=user_in.phone_number,
        jurisdiction_district=user_in.jurisdiction_district,
        badge_number=user_in.badge_number,
        is_active=True,
    )
    db.add(new_user)
    await db.flush()

    await log_audit_event(
        db,
        action="CREATE_USER",
        entity_type="USER",
        entity_id=new_user.id,
        actor=current_user,
        description=f"Created user account {new_user.email} with role {new_user.role.value}.",
    )
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.DISTRICT_COLLECTOR)),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile, status, or role permissions."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User", user_id)

    update_data = user_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(user, field, val)

    await log_audit_event(
        db,
        action="UPDATE_USER",
        entity_type="USER",
        entity_id=user.id,
        actor=current_user,
        description=f"Updated user account {user.email}.",
        changes=update_data,
    )
    await db.commit()
    await db.refresh(user)
    return user
