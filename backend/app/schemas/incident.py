"""AapadaOps Incident Schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.incident import (
    IncidentCategory,
    IncidentSeverity,
    IncidentStatus,
)


class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    category: IncidentCategory = IncidentCategory.FLOOD
    reported_severity: IncidentSeverity = IncidentSeverity.MEDIUM
    district_name: str = Field(..., min_length=2)
    district_id: Optional[str] = None
    block_name: Optional[str] = None
    block_id: Optional[str] = None
    village_name: Optional[str] = None
    latitude: float = Field(..., ge=17.0, le=23.5)
    longitude: float = Field(..., ge=81.0, le=88.0)
    reporter_name: str = Field(..., min_length=2, max_length=150)
    reporter_phone: str = Field(..., min_length=10, max_length=20)
    reporter_role: str = "CITIZEN"
    estimated_affected_people: int = Field(default=0, ge=0)
    casualties_reported: int = Field(default=0, ge=0)
    stranded_count: int = Field(default=0, ge=0)


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[IncidentCategory] = None
    reported_severity: Optional[IncidentSeverity] = None
    district_name: Optional[str] = None
    block_name: Optional[str] = None
    village_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    estimated_affected_people: Optional[int] = None
    casualties_reported: Optional[int] = None
    stranded_count: Optional[int] = None


class IncidentStatusTransition(BaseModel):
    status: IncidentStatus
    notes: Optional[str] = None
    verified_priority: Optional[IncidentSeverity] = None


class IncidentResponse(BaseModel):
    id: str
    incident_code: str
    title: str
    description: str
    category: IncidentCategory
    reported_severity: IncidentSeverity
    verified_priority: Optional[IncidentSeverity] = None
    status: IncidentStatus
    district_id: Optional[str] = None
    district_name: str
    block_id: Optional[str] = None
    block_name: Optional[str] = None
    village_name: Optional[str] = None
    latitude: float
    longitude: float
    reporter_name: str
    reporter_phone: str
    reporter_role: str
    is_verified: bool
    verified_by_id: Optional[str] = None
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    ai_confidence_score: float
    ai_raw_classification: Optional[str] = None
    ai_urgency_score: float
    is_duplicate: bool
    duplicate_of_id: Optional[str] = None
    duplicate_cluster_id: Optional[str] = None
    estimated_affected_people: int
    casualties_reported: int
    stranded_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncidentListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[IncidentResponse]
