"""AapadaOps Operational Mission Tasks."""

import enum
from sqlalchemy import (
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


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Task(BaseModel):
    """Tactical mission dispatched to response teams with strict SLA enforcement."""

    __tablename__ = "tasks"

    task_code = Column(String(50), unique=True, index=True, nullable=False)
    incident_id = Column(
        String(36),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_team_id = Column(
        String(36),
        ForeignKey("response_teams.id"),
        nullable=True,
        index=True,
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(50), default="HIGH", nullable=False)
    sla_hours = Column(Integer, default=4, nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(
        Enum(TaskStatus, name="task_status_enum"),
        default=TaskStatus.PENDING,
        nullable=False,
        index=True,
    )
    target_village = Column(String(150), nullable=False)
    target_latitude = Column(Float, nullable=False)
    target_longitude = Column(Float, nullable=False)
    dispatch_notes = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Relationships
    incident = relationship("Incident", back_populates="tasks")
    assigned_team = relationship("ResponseTeam")
    evidence_files = relationship("EvidenceFile", back_populates="task")

    def __repr__(self) -> str:
        return f"<Task {self.task_code}: {self.title} ({self.status})>"
