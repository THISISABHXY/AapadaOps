"""AapadaOps Field and Citizen Incident Reports."""

import enum
from sqlalchemy import Column, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class ReportSource(str, enum.Enum):
    CITIZEN_WEB = "CITIZEN_WEB"
    CITIZEN_SOS = "CITIZEN_SOS"
    FIELD_WORKER_APP = "FIELD_WORKER_APP"
    HELPLINE_1070 = "HELPLINE_1070"
    JANA_SUNANI = "JANA_SUNANI"


class IncidentReport(BaseModel):
    """Raw disaster report received from citizens, field responders, or grievance helplines."""

    __tablename__ = "incident_reports"

    incident_id = Column(
        String(36),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_type = Column(
        Enum(ReportSource, name="report_source_enum"),
        default=ReportSource.CITIZEN_WEB,
        nullable=False,
    )
    raw_text = Column(Text, nullable=False)
    text_language = Column(String(10), default="en", nullable=False)  # 'en' or 'or' (Odia)
    audio_url = Column(String(500), nullable=True)
    transcript_text = Column(Text, nullable=True)
    reporter_name = Column(String(150), nullable=False)
    reporter_phone = Column(String(20), nullable=False)
    gps_lat = Column(Float, nullable=True)
    gps_lng = Column(Float, nullable=True)
    submission_ip = Column(String(45), nullable=True)

    # Relationships
    incident = relationship("Incident", back_populates="reports")
    evidence_files = relationship("EvidenceFile", back_populates="report")

    def __repr__(self) -> str:
        return f"<IncidentReport {self.id} for {self.incident_id}>"
