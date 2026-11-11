"""AapadaOps Response Coordination & Resource Optimization Models."""

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


class CoordinationStatus(str, enum.Enum):
    AI_RECOMMENDED = "AI_RECOMMENDED"
    COORDINATOR_REVIEW = "COORDINATOR_REVIEW"
    APPROVED = "APPROVED"
    ASSIGNED = "ASSIGNED"
    TEAM_ACKNOWLEDGED = "TEAM_ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    EVIDENCE_ATTACHED = "EVIDENCE_ATTACHED"
    HUMAN_CLOSED = "HUMAN_CLOSED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class CoordinationPlan(BaseModel):
    """Operational response coordination plan with human governance workflow."""

    __tablename__ = "coordination_plans"

    plan_code = Column(String(50), unique=True, index=True, nullable=False)
    incident_id = Column(
        String(36),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(255), nullable=False)
    strategy_name = Column(String(50), nullable=False)  # MINIMAL_TIME, MAXIMAL_CAPACITY, RESERVE_PRESERVATION

    status = Column(
        Enum(CoordinationStatus, name="coordination_status_enum"),
        default=CoordinationStatus.AI_RECOMMENDED,
        nullable=False,
        index=True,
    )

    # Allocated entity references stored as JSON lists of IDs
    allocated_team_ids_json = Column(Text, default="[]", nullable=False)
    allocated_resource_ids_json = Column(Text, default="[]", nullable=False)

    # Operational geography
    target_latitude = Column(Float, nullable=False)
    target_longitude = Column(Float, nullable=False)
    target_district = Column(String(100), nullable=False, index=True)
    target_village = Column(String(150), nullable=False)

    # Calculated travel and telemetry (strictly flagged as estimated)
    estimated_distance_km = Column(Float, default=0.0, nullable=False)
    estimated_arrival_minutes = Column(Float, default=30.0, nullable=False)
    telemetry_source = Column(String(50), default="CALCULATED_ESTIMATE", nullable=False)
    is_live_telemetry = Column(Boolean, default=False, nullable=False)

    # Explainability & Operational Impact
    reasoning_text = Column(Text, nullable=False)
    assumptions_text = Column(Text, nullable=False)
    limitations_text = Column(Text, nullable=False)
    resource_impact_json = Column(Text, default="{}", nullable=False)

    # Workflow Audit Trail & Sign-offs
    reviewed_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    approved_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    acknowledged_by = Column(String(150), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

    progress_notes = Column(Text, nullable=True)

    evidence_file_id = Column(String(36), ForeignKey("evidence_files.id"), nullable=True)

    closed_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    closure_notes = Column(Text, nullable=True)

    # Relationships
    incident = relationship("Incident")
    evidence_file = relationship("EvidenceFile")
    reviewer = relationship("User", foreign_keys=[reviewed_by_id])
    approver = relationship("User", foreign_keys=[approved_by_id])
    closer = relationship("User", foreign_keys=[closed_by_id])

    def __repr__(self) -> str:
        return f"<CoordinationPlan {self.plan_code}: {self.strategy_name} ({self.status})>"

