"""AapadaOps Incident Lifecycle and Domain Entities."""

import enum
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class IncidentStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
    VERIFIED = "VERIFIED"
    PRIORITIZED = "PRIORITIZED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    DUPLICATE = "DUPLICATE"
    REJECTED = "REJECTED"
    DISPUTED = "DISPUTED"
    REOPENED = "REOPENED"


class IncidentSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class IncidentCategory(str, enum.Enum):
    FLOOD = "FLOOD"
    CYCLONE_WIND = "CYCLONE_WIND"
    TREE_FALL = "TREE_FALL"
    ROAD_BLOCK = "ROAD_BLOCK"
    EMBANKMENT_BREACH = "EMBANKMENT_BREACH"
    STRANDED_PERSONS = "STRANDED_PERSONS"
    POWER_FAILURE = "POWER_FAILURE"
    SHELTER_DEMAND = "SHELTER_DEMAND"
    MEDICAL_EMERGENCY = "MEDICAL_EMERGENCY"
    OTHER = "OTHER"


class Incident(BaseModel):
    """Core disaster incident tracking entity managed through state machine lifecycle."""

    __tablename__ = "incidents"

    incident_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(
        Enum(IncidentCategory, name="incident_category_enum"),
        default=IncidentCategory.FLOOD,
        nullable=False,
        index=True,
    )
    reported_severity = Column(
        Enum(IncidentSeverity, name="incident_severity_enum"),
        default=IncidentSeverity.MEDIUM,
        nullable=False,
        index=True,
    )
    verified_priority = Column(
        Enum(IncidentSeverity, name="incident_verified_priority_enum"),
        nullable=True,
        index=True,
    )
    status = Column(
        Enum(IncidentStatus, name="incident_status_enum"),
        default=IncidentStatus.SUBMITTED,
        nullable=False,
        index=True,
    )

    # Spatial & Administrative Location
    district_id = Column(String(36), ForeignKey("districts.id"), nullable=True, index=True)
    district_name = Column(String(100), index=True, nullable=False)
    block_id = Column(String(36), ForeignKey("blocks.id"), nullable=True, index=True)
    block_name = Column(String(100), nullable=True)
    village_name = Column(String(150), nullable=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)

    # Reporter Metadata
    reporter_name = Column(String(150), nullable=False)
    reporter_phone = Column(String(20), nullable=False, index=True)
    reporter_role = Column(String(50), default="CITIZEN", nullable=False)

    # Verification Details
    is_verified = Column(Boolean, default=False, nullable=False, index=True)
    verified_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_notes = Column(Text, nullable=True)

    # AI Advisory Metrics
    ai_confidence_score = Column(Float, default=0.0, nullable=False)
    ai_raw_classification = Column(Text, nullable=True)
    ai_urgency_score = Column(Float, default=0.0, nullable=False)

    # Duplicate Clustering
    is_duplicate = Column(Boolean, default=False, nullable=False, index=True)
    duplicate_of_id = Column(String(36), ForeignKey("incidents.id"), nullable=True)
    duplicate_cluster_id = Column(String(36), nullable=True, index=True)

    # Operational Impact
    estimated_affected_people = Column(Integer, default=0, nullable=False)
    casualties_reported = Column(Integer, default=0, nullable=False)
    stranded_count = Column(Integer, default=0, nullable=False)

    # Relationships
    reports = relationship("IncidentReport", back_populates="incident", cascade="all, delete-orphan")
    evidence_files = relationship("EvidenceFile", back_populates="incident", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="incident")
    verification_logs = relationship("VerificationLog", back_populates="incident", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Incident {self.incident_code}: {self.title} ({self.status})>"
