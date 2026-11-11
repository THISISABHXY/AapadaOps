"""AapadaOps SATARK Early Warning Alerts & Bulletins."""

import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, String, Text
from app.models.base import BaseModel


class AlertSeverity(str, enum.Enum):
    RED = "RED"
    ORANGE = "ORANGE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class AlertHazard(str, enum.Enum):
    CYCLONE = "CYCLONE"
    FLOOD = "FLOOD"
    STORM_SURGE = "STORM_SURGE"
    HEAVY_RAIN = "HEAVY_RAIN"
    LIGHTNING = "LIGHTNING"


class AlertBroadcast(BaseModel):
    """Early warning advisory issued by IMD, CWC, or OSDMA SATARK system."""

    __tablename__ = "alert_broadcasts"

    alert_code = Column(String(50), unique=True, index=True, nullable=False)
    severity = Column(
        Enum(AlertSeverity, name="alert_severity_enum"),
        default=AlertSeverity.YELLOW,
        nullable=False,
        index=True,
    )
    hazard_type = Column(
        Enum(AlertHazard, name="alert_hazard_enum"),
        default=AlertHazard.CYCLONE,
        nullable=False,
        index=True,
    )
    headline = Column(String(255), nullable=False)
    advisory_body = Column(Text, nullable=False)
    affected_districts_json = Column(Text, nullable=False)  # JSON serialized list of districts
    source = Column(String(50), default="OSDMA_SATARK", nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<AlertBroadcast {self.alert_code}: {self.headline} ({self.severity})>"
