"""AapadaOps Verification Audit Trail."""

from sqlalchemy import Column, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class VerificationLog(BaseModel):
    """Immutable log of verification actions performed by authorized officers."""

    __tablename__ = "verification_logs"

    incident_id = Column(
        String(36),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    officer_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    previous_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    previous_priority = Column(String(50), nullable=True)
    new_priority = Column(String(50), nullable=False)
    verification_notes = Column(Text, nullable=False)
    confidence_override = Column(Float, nullable=True)

    # Relationships
    incident = relationship("Incident", back_populates="verification_logs")
    officer = relationship("User")

    def __repr__(self) -> str:
        return f"<VerificationLog for {self.incident_id} by {self.officer_id}>"
