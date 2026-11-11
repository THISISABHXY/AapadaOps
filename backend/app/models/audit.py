"""AapadaOps Immutable Audit Trail for Regulatory Compliance."""

from sqlalchemy import Column, ForeignKey, String, Text
from app.models.base import BaseModel


class AuditLog(BaseModel):
    """Immutable audit trail recording every state transition and administrative decision."""

    __tablename__ = "audit_logs"

    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # INCIDENT, TASK, RESOURCE, USER, VERIFICATION
    entity_id = Column(String(36), nullable=False, index=True)
    actor_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    actor_role = Column(String(50), nullable=True)
    actor_name = Column(String(150), nullable=True)
    ip_address = Column(String(45), nullable=True)
    changes_json = Column(Text, nullable=True)
    description = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} on {self.entity_type}:{self.entity_id}>"
