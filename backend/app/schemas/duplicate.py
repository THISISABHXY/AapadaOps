"""AapadaOps Duplicate Cluster and Verification Schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.duplicate import ClusterStatus
from app.models.incident import IncidentSeverity, IncidentStatus
from app.schemas.incident import IncidentResponse


class DuplicateClusterResponse(BaseModel):
    id: str
    primary_incident_id: str
    status: ClusterStatus
    spatial_radius_meters: float
    confidence_score: float
    cluster_summary: Optional[str] = None
    duplicate_count: int
    created_at: datetime
    primary_incident: Optional[IncidentResponse] = None
    duplicate_incidents: List[IncidentResponse] = []

    model_config = {"from_attributes": True}


class MergeDuplicateRequest(BaseModel):
    master_incident_id: str
    duplicate_incident_ids: List[str] = Field(..., min_length=1)
    merge_notes: Optional[str] = None


class VerificationSubmitRequest(BaseModel):
    new_status: IncidentStatus = IncidentStatus.VERIFIED
    verified_priority: IncidentSeverity
    verification_notes: str = Field(..., min_length=5)
    confidence_override: Optional[float] = None


class VerificationResponse(BaseModel):
    id: str
    incident_id: str
    officer_id: str
    previous_status: str
    new_status: str
    previous_priority: Optional[str] = None
    new_priority: str
    verification_notes: str
    confidence_override: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}
