"""AapadaOps ODRN Resource Inventory Models."""

import enum
from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String
from app.models.base import BaseModel


class ResourceType(str, enum.Enum):
    POWER_BOAT = "POWER_BOAT"
    INFLATABLE_BOAT = "INFLATABLE_BOAT"
    JCB_EXCAVATOR = "JCB_EXCAVATOR"
    DEWATERING_PUMP = "DEWATERING_PUMP"
    HAM_RADIO_UNIT = "HAM_RADIO_UNIT"
    DIESEL_GENERATOR = "DIESEL_GENERATOR"
    MOBILE_WATER_PURIFIER = "MOBILE_WATER_PURIFIER"
    DRONE_SURVEY_TEAM = "DRONE_SURVEY_TEAM"
    EMERGENCY_RATION_KIT = "EMERGENCY_RATION_KIT"
    FIRST_AID_KIT = "FIRST_AID_KIT"


class ResourceStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    DISPATCHED = "DISPATCHED"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"
    DECOMMISSIONED = "DECOMMISSIONED"


class Resource(BaseModel):
    """Odisha Disaster Resource Network (ODRN) tactical equipment and supplies."""

    __tablename__ = "resources"

    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    category = Column(
        Enum(ResourceType, name="resource_type_enum"),
        default=ResourceType.POWER_BOAT,
        nullable=False,
        index=True,
    )
    organization = Column(String(100), nullable=False)  # ODRAF, NDRF, Fire Services, OSDMA
    district_id = Column(String(36), ForeignKey("districts.id"), nullable=True, index=True)
    district_name = Column(String(100), nullable=False, index=True)
    status = Column(
        Enum(ResourceStatus, name="resource_status_enum"),
        default=ResourceStatus.AVAILABLE,
        nullable=False,
        index=True,
    )
    quantity = Column(Integer, default=1, nullable=False)
    unit_of_measure = Column(String(50), default="units", nullable=False)
    capacity = Column(Integer, default=10, nullable=False)
    capacity_unit = Column(String(50), default="units", nullable=False)
    assigned_incident_id = Column(String(36), nullable=True, index=True)
    assigned_plan_id = Column(String(36), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    contact_person = Column(String(150), nullable=True)
    contact_phone = Column(String(20), nullable=True)

    def __repr__(self) -> str:
        return f"<Resource {self.code}: {self.name} ({self.status})>"

