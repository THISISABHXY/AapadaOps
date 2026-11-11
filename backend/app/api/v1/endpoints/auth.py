"""AapadaOps Authentication API Endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.api.v1.deps import get_current_user
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse, UserSummary
from app.schemas.user import UserCreate, UserResponse
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate operational personnel with email and password, returning JWT session tokens."""
    result = await db.execute(select(User).where(User.email == credentials.email.lower()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password.")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Contact District Collectorate.",
        )

    access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        district=user.jurisdiction_district,
    )
    refresh_token = create_refresh_token(subject=user.id)

    await log_audit_event(
        db,
        action="USER_LOGIN",
        entity_type="USER",
        entity_id=user.id,
        actor=user,
        description=f"User {user.email} logged in successfully.",
    )
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=UserSummary.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Renew expired access token using a valid refresh token."""
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid or expired refresh token.")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedError("User session is no longer active.")

    new_access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        district=user.jurisdiction_district,
    )
    new_refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=UserSummary.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve authenticated user's profile and permissions."""
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create initial user account (or for public responder registration)."""
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
    await db.commit()
    await db.refresh(new_user)
    return new_user

