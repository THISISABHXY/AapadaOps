"""AapadaOps Response Forces and Tactical Teams."""

import enum
from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String
from app.models.base import BaseModel


class TeamStatus(str, enum.Enum):
    STANDBY = "STANDBY"
    DEPLOYED = "DEPLOYED"
    RESTING = "RESTING"
    TRANSIT = "TRANSIT"


class ResponseTeam(BaseModel):
    """Tactical disaster response unit (NDRF, ODRAF, Fire & Emergency Services, Civil Defence)."""

    __tablename__ = "response_teams"

    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    organization = Column(String(100), nullable=False)  # NDRF, ODRAF, FIRE_SERVICES, CIVIL_DEFENCE
    battalion = Column(String(150), nullable=True)
    team_lead_name = Column(String(150), nullable=False)
    team_lead_phone = Column(String(20), nullable=False)
    total_personnel = Column(Integer, default=10, nullable=False)
    specialization = Column(String(100), default="WATER_RESCUE", nullable=False)
    rescue_capacity_persons = Column(Integer, default=30, nullable=False)
    assigned_incident_id = Column(String(36), nullable=True, index=True)
    assigned_plan_id = Column(String(36), nullable=True, index=True)
    current_district_id = Column(String(36), ForeignKey("districts.id"), nullable=True, index=True)
    current_district_name = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(
        Enum(TeamStatus, name="team_status_enum"),
        default=TeamStatus.STANDBY,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<ResponseTeam {self.code}: {self.name} ({self.status})>"

