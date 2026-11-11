"""AapadaOps Verified Evidence Media and Documents."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class EvidenceFile(BaseModel):
    """File attachment (photo, audio note, damage report, or completion proof)."""

    __tablename__ = "evidence_files"

    incident_id = Column(
        String(36),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    report_id = Column(
        String(36),
        ForeignKey("incident_reports.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    task_id = Column(
        String(36),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    sha256_hash = Column(String(64), nullable=False, index=True)
    uploader_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    incident = relationship("Incident", back_populates="evidence_files")
    report = relationship("IncidentReport", back_populates="evidence_files")
    task = relationship("Task", back_populates="evidence_files")

    def __repr__(self) -> str:
        return f"<EvidenceFile {self.file_name} ({self.mime_type})>"

