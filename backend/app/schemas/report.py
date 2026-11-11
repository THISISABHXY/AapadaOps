"""AapadaOps Field Report & Evidence Schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.report import ReportSource


class ReportCreate(BaseModel):
    incident_id: str
    source_type: ReportSource = ReportSource.CITIZEN_WEB
    raw_text: str = Field(..., min_length=5)
    text_language: str = "en"
    audio_url: Optional[str] = None
    transcript_text: Optional[str] = None
    reporter_name: str
    reporter_phone: str
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None


class ReportResponse(BaseModel):
    id: str
    incident_id: str
    source_type: ReportSource
    raw_text: str
    text_language: str
    audio_url: Optional[str] = None
    transcript_text: Optional[str] = None
    reporter_name: str
    reporter_phone: str
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EvidenceResponse(BaseModel):
    id: str
    incident_id: Optional[str] = None
    report_id: Optional[str] = None
    task_id: Optional[str] = None
    file_name: str
    file_path: str
    file_size_bytes: int
    mime_type: str
    sha256_hash: str
    uploader_id: Optional[str] = None
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}
