"""AapadaOps User and Role Models."""

import enum
from sqlalchemy import Boolean, Column, Enum, String
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    DISTRICT_COLLECTOR = "DISTRICT_COLLECTOR"
    INCIDENT_VERIFICATION_OFFICER = "INCIDENT_VERIFICATION_OFFICER"
    RESPONSE_COORDINATOR = "RESPONSE_COORDINATOR"
    FIELD_WORKER = "FIELD_WORKER"
    OBSERVER = "OBSERVER"
    CITIZEN_REPORTER = "CITIZEN_REPORTER"


class User(BaseModel):
    """User account entity with role-based access control and jurisdiction boundaries."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRole, name="user_role_enum"),
        default=UserRole.FIELD_WORKER,
        nullable=False,
        index=True,
    )
    phone_number = Column(String(20), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    jurisdiction_district = Column(String(100), nullable=True, index=True)
    badge_number = Column(String(50), nullable=True)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"

