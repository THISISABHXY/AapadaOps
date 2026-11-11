"""AapadaOps Multipurpose Cyclone Shelter (MCS) Models."""

import enum
from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, String
from app.models.base import BaseModel


class ShelterStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    FULL = "FULL"


class CycloneShelter(BaseModel):
    """Multipurpose Cyclone Shelter (MCS) tracked by OSDMA and District Collectorates."""

    __tablename__ = "cyclone_shelters"

    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    district_id = Column(String(36), ForeignKey("districts.id"), nullable=True, index=True)
    district_name = Column(String(100), nullable=False, index=True)
    block_id = Column(String(36), ForeignKey("blocks.id"), nullable=True, index=True)
    block_name = Column(String(100), nullable=True)
    village = Column(String(150), nullable=False)
    capacity = Column(Integer, default=500, nullable=False)
    current_occupancy = Column(Integer, default=0, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    has_power_backup = Column(Boolean, default=True, nullable=False)
    generator_fuel_hours = Column(Integer, default=24, nullable=False)
    drinking_water_days = Column(Integer, default=5, nullable=False)
    has_medical_kit = Column(Boolean, default=True, nullable=False)
    caretaker_name = Column(String(150), nullable=False)
    caretaker_phone = Column(String(20), nullable=False)
    status = Column(
        Enum(ShelterStatus, name="shelter_status_enum"),
        default=ShelterStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<CycloneShelter {self.name} ({self.current_occupancy}/{self.capacity})>"
