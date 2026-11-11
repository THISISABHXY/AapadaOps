"""AapadaOps Strict AI Schemas for Information Extraction, Voice, Duplicates, Prioritization & RAG."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from app.models.incident import IncidentCategory, IncidentSeverity


# ============================================================================
# Service A: Information Extraction Schemas
# ============================================================================

class ExtractedIncidentRecord(BaseModel):
    """Structured incident record strictly extracted from unstructured report.
    Missing fields are explicitly catalogued and never fabricated.
    """
    incident_category: IncidentCategory
    location: Optional[str] = None
    district: Optional[str] = None
    description: str
    severity_indicators: List[str] = Field(default_factory=list)
    people_affected: Optional[int] = None
    medical_needs: List[str] = Field(default_factory=list)
    resource_requirements: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "TEXT_REPORT"
    confidence: float = Field(ge=0.0, le=1.0)
    missing_fields: List[str] = Field(default_factory=list)
    detected_language: str = "en"
    is_advisory: bool = True
    requires_human_verification: bool = True

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        return round(v, 2)


class ExtractionRequest(BaseModel):
    """Input payload for extracting structured incident fields from raw report text."""
    text: str = Field(..., min_length=4, description="Raw report text in English, Odia, or mixed transliterated format")
    source: str = Field(default="CITIZEN_REPORT", description="Source channel (CITIZEN_REPORT, FIELD_DISPATCH, CALL_CENTER, etc.)")
    language_hint: Optional[str] = Field(default=None, description="Optional ISO code hint (e.g. 'or', 'en')")
    recorded_at: Optional[datetime] = None


# ============================================================================
# Service B: Odia & English Voice Processing Schemas
# ============================================================================

class VoiceTranscriptionRequest(BaseModel):
    """Request for transcribing an audio report file."""
    audio_file_id: Optional[str] = None
    original_filename: str = Field(..., min_length=1)
    mime_type: str = "audio/wav"
    language_hint: Optional[str] = None
    simulated_audio_text: Optional[str] = None  # Used for testing/simulated audio feeds


class VoiceTranscriptionResponse(BaseModel):
    """Result of automated audio transcription with acoustic confidence flags."""
    audio_file_id: Optional[str] = None
    original_filename: str
    mime_type: str
    duration_seconds: float
    detected_language: str
    raw_transcript: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    is_low_confidence: bool
    confidence_flags: List[str] = Field(default_factory=list)
    acoustic_notes: str
    requires_human_correction: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TranscriptCorrectionRequest(BaseModel):
    """Human correction of an automated speech transcript."""
    transcript_id: str
    corrected_transcript: str = Field(..., min_length=1)
    correction_notes: Optional[str] = None
    verified_by_user_id: str


class TranscriptCorrectionResponse(BaseModel):
    """Record of human-verified and corrected transcript."""
    transcript_id: str
    original_transcript: str
    corrected_transcript: str
    is_human_verified: bool = True
    verified_by_user_id: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================================
# Service C: Duplicate Detection Schemas
# ============================================================================

class CandidateIncidentInput(BaseModel):
    """Incident payload for duplicate detection comparison."""
    id: Optional[str] = "CANDIDATE"
    incident_code: Optional[str] = "INC-PENDING"
    title: str
    description: str
    category: IncidentCategory
    latitude: float
    longitude: float
    district_name: Optional[str] = None
    village_name: Optional[str] = None
    reporter_phone: Optional[str] = None
    created_at: Optional[datetime] = None


class DuplicateMatchFactor(BaseModel):
    """Individual similarity component breakdown."""
    factor: str
    score: float
    weight: float
    detail: str


class AIDuplicateMatch(BaseModel):
    """Detailed comparison between an incoming report and an existing incident."""
    incident_id: str
    incident_code: str
    title: str
    category: IncidentCategory
    distance_meters: float
    time_diff_hours: float
    text_similarity: float
    overall_score: float = Field(ge=0.0, le=1.0)
    is_probable_duplicate: bool
    factors: List[DuplicateMatchFactor]
    plain_explanation: str


class AIDuplicateDetectionResponse(BaseModel):
    """Comprehensive duplicate evaluation response with strict human confirmation guardrail."""
    candidate_id: str
    total_candidates_analyzed: int
    probable_duplicates_count: int
    matches: List[AIDuplicateMatch]
    safety_warning: str = (
        "AI duplicate predictions are advisory suggestions. Automatic incident merging is strictly "
        "disabled. Authorized administrative review is mandatory before executing any merge."
    )


# ============================================================================
# Service D: Explainable Prioritization Schemas
# ============================================================================

class PrioritizationFactor(BaseModel):
    """Individual factor contributing to the composite urgency score."""
    factor_name: str
    points_awarded: float
    max_points: float
    reason: str


class PrioritizationRequest(BaseModel):
    """Input attributes for computing multi-factor operational priority."""
    category: IncidentCategory
    reported_severity: IncidentSeverity
    stranded_count: int = Field(default=0, ge=0)
    casualties: int = Field(default=0, ge=0)
    medical_needs: List[str] = Field(default_factory=list)
    is_coastal_block: bool = False
    access_cut_off: bool = False
    is_verified: bool = False
    report_freshness_hours: float = Field(default=0.5, ge=0.0)
    district_vulnerability_tier: int = Field(default=3, ge=1, le=5)


class PrioritizationResponse(BaseModel):
    """Explainable priority recommendation with full point breakdown."""
    composite_score: float = Field(ge=0.0, le=100.0)
    priority_level: IncidentSeverity
    factors: List[PrioritizationFactor]
    plain_language_summary: str
    recommended_sla_hours: int
    is_deterministic: bool = True
    is_advisory: bool = True
    safety_notice: str = (
        "Priority scoring is calculated using the documented multi-factor OSDMA framework. "
        "Dispatch officers may override recommended priorities based on tactical ground realities."
    )


# ============================================================================
# Service E: RAG Verified SOP Knowledge Assistant Schemas
# ============================================================================

class RAGCitation(BaseModel):
    """Grounding citation from verified official government manuals."""
    document_name: str
    section: str
    page: int
    relevant_excerpt: str
    relevance_score: float


class RAGQueryRequest(BaseModel):
    """User query seeking official SOP protocols."""
    query: str = Field(..., min_length=3)
    category_filter: Optional[str] = None
    top_k: int = Field(default=3, ge=1, le=5)


class RAGResponse(BaseModel):
    """Grounded answer synthesized strictly from verified disaster SOP manuals."""
    query: str
    grounded_answer: str
    citations: List[RAGCitation]
    grounding_confidence: float
    is_official_sop: bool
    refusal_reason: Optional[str] = None
    source_manuals: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "All instructions are grounded strictly in verified OSDMA, NDMA, and Government of Odisha SOPs. "
        "The system does not hallucinate unofficial actions."
    )


# ============================================================================
# Service F: Evaluation Benchmark Metrics Schemas
# ============================================================================

class EvaluationMetricSummary(BaseModel):
    """Empirical evaluation metric report for an AI subsystem."""
    service_name: str
    total_samples: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    avg_latency_ms: float
    evaluation_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = Field(default_factory=dict)


class SystemAIEvaluationReport(BaseModel):
    """Consolidated benchmark evaluation report across all AI capabilities."""
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    platform_name: str = "AapadaOps Disaster Intelligence Engine"
    benchmarks: List[EvaluationMetricSummary]
    safety_compliance: Dict[str, bool]
