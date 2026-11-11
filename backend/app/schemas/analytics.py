"""AapadaOps Audit, Alert, Analytics, and AI Advisory Schemas."""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.alert import AlertHazard, AlertSeverity
from app.models.incident import IncidentCategory, IncidentSeverity


# --- Audit Logs ---
class AuditLogResponse(BaseModel):
    id: str
    action: str
    entity_type: str
    entity_id: str
    actor_id: Optional[str] = None
    actor_role: Optional[str] = None
    actor_name: Optional[str] = None
    ip_address: Optional[str] = None
    changes_json: Optional[str] = None
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Alert Broadcasts ---
class AlertCreate(BaseModel):
    severity: AlertSeverity
    hazard_type: AlertHazard
    headline: str = Field(..., min_length=5)
    advisory_body: str = Field(..., min_length=10)
    affected_districts: List[str] = Field(..., min_length=1)
    source: str = "OSDMA_SATARK"
    valid_until: datetime


class AlertResponse(BaseModel):
    id: str
    alert_code: str
    severity: AlertSeverity
    hazard_type: AlertHazard
    headline: str
    advisory_body: str
    affected_districts_json: str
    source: str
    issued_at: datetime
    valid_until: datetime
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Analytics & Reporting ---
class OperationalKPIs(BaseModel):
    total_incidents: int
    verified_incidents: int
    active_incidents: int
    resolved_incidents: int
    deployed_units: int
    active_shelters: int
    total_shelter_capacity: int
    current_shelter_occupancy: int
    sla_compliance_rate: float
    avg_response_time_minutes: float


class IncidentVelocityPoint(BaseModel):
    timestamp: str
    reported_count: int
    verified_count: int
    dispatched_count: int


class DistrictReadinessPoint(BaseModel):
    district_name: str
    vulnerability_tier: int
    available_boats: int
    available_pumps: int
    shelter_occupancy_percent: float
    active_incidents: int


class CategoryDistributionPoint(BaseModel):
    category: IncidentCategory
    count: int


class DashboardSummaryResponse(BaseModel):
    kpis: OperationalKPIs
    incident_velocity: List[IncidentVelocityPoint]
    district_readiness: List[DistrictReadinessPoint]
    category_distribution: List[CategoryDistributionPoint]


# --- AI Advisory Processing ---
class AITextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=5)
    language_hint: Optional[str] = None


class AITextAnalysisResponse(BaseModel):
    detected_language: str
    suggested_category: IncidentCategory
    suggested_severity: IncidentSeverity
    confidence_score: float
    urgency_score: float
    extracted_entities: Dict[str, str] = {}
    extracted_stranded_count: int = 0
    extracted_casualties: int = 0
    ai_advisory_statement: str
    is_ai_generated: bool = True


class AIDuplicateScoreResponse(BaseModel):
    incident_a_id: str
    incident_b_id: str
    distance_meters: float
    time_difference_hours: float
    semantic_similarity: float
    overall_duplicate_probability: float
    is_likely_duplicate: bool

