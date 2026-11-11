"""AapadaOps Authentication Pydantic Schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserSummary(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    phone_number: Optional[str] = None
    jurisdiction_district: Optional[str] = None
    badge_number: Optional[str] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserSummary


class RefreshTokenRequest(BaseModel):
    refresh_token: str
