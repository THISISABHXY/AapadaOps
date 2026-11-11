"""AapadaOps User Management Schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=150)
    role: UserRole = UserRole.FIELD_WORKER
    phone_number: Optional[str] = None
    jurisdiction_district: Optional[str] = None
    badge_number: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    jurisdiction_district: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    phone_number: Optional[str] = None
    is_active: bool
    jurisdiction_district: Optional[str] = None
    badge_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
