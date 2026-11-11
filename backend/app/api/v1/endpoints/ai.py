"""AapadaOps Comprehensive AI Disaster-Response Intelligence Endpoints.

Exposes REST APIs for Information Extraction, Odia Voice Processing,
Duplicate Detection, Explainable Prioritization, RAG Verified SOP Retrieval,
and Empirical Evaluation Reporting.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.duplicate_detector import duplicate_detector
from app.ai.evaluator import evaluator
from app.ai.extractor import extraction_engine
from app.ai.prioritizer import prioritizer_engine
from app.ai.rag_assistant import rag_assistant
from app.ai.safety import safety_enforcer
from app.ai.schemas import (
    AIDuplicateDetectionResponse,
    AIDuplicateMatch,
    CandidateIncidentInput,
    ExtractedIncidentRecord,
    ExtractionRequest,
    PrioritizationRequest,
    PrioritizationResponse,
    RAGQueryRequest,
    RAGResponse,
    SystemAIEvaluationReport,
    TranscriptCorrectionRequest,
    TranscriptCorrectionResponse,
    VoiceTranscriptionRequest,
    VoiceTranscriptionResponse,
)
from app.ai.voice_processor import voice_processor
from app.core.database import get_db
from app.models.incident import Incident
from app.schemas.analytics import (
    AIDuplicateScoreResponse,
    AITextAnalysisRequest,
    AITextAnalysisResponse,
)
from app.services.ai_service import ai_engine
from app.services.duplicate_service import jaccard_similarity
from app.services.spatial_service import haversine_distance_meters

router = APIRouter(prefix="/ai", tags=["AI Intelligence Engine"])


# ============================================================================
# Service A: Information Extraction
# ============================================================================

@router.post("/extract", response_model=ExtractedIncidentRecord)
async def extract_structured_incident(request: ExtractionRequest):
    """Convert unstructured text or transcribed voice report into a strictly validated incident record.
    Identifies category, district, location, counts, medical needs, and catalogued missing fields.
    """
    return await extraction_engine.extract_structured_incident(request)


@router.post("/analyze-text", response_model=AITextAnalysisResponse)
async def analyze_report_text(request: AITextAnalysisRequest):
    """Backward-compatible fast triage text classification in English or Odia."""
    analysis = ai_engine.analyze_report(request.text)
    return AITextAnalysisResponse(
        detected_language=analysis["detected_language"],
        suggested_category=analysis["suggested_category"],
        suggested_severity=analysis["suggested_severity"],
        confidence_score=analysis["confidence_score"],
        urgency_score=analysis["urgency_score"],
        extracted_stranded_count=analysis["extracted_stranded_count"],
        extracted_casualties=analysis["extracted_casualties"],
        ai_advisory_statement=analysis["ai_advisory_statement"],
        is_ai_generated=True,
    )


# ============================================================================
# Service B: Odia Voice Processing
# ============================================================================

@router.post("/voice/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_voice_report(request: VoiceTranscriptionRequest):
    """Process disaster voice audio in Odia or English, flag acoustic noise, and return speech transcript."""
    return await voice_processor.transcribe_audio(request)


@router.post("/voice/correct", response_model=TranscriptCorrectionResponse)
async def submit_transcript_correction(request: TranscriptCorrectionRequest):
    """Submit human correction and validation for an automated speech transcript."""
    return await voice_processor.correct_transcript(request)


# ============================================================================
# Service C: Duplicate Detection
# ============================================================================

@router.post("/detect-duplicates", response_model=AIDuplicateDetectionResponse)
async def detect_duplicate_incidents(
    candidate: CandidateIncidentInput,
    db: AsyncSession = Depends(get_db),
):
    """Scan candidate incident against existing database records using text embeddings,
    geographic proximity, time difference, category alignment, and shared attributes.
    Strictly advisory: automatic merging is prohibited.
    """
    # Fetch active incidents from database to compare
    from sqlalchemy import select
    stmt = select(Incident).order_by(Incident.created_at.desc()).limit(50)
    result = await db.execute(stmt)
    db_incidents = result.scalars().all()

    existing_inputs = [
        CandidateIncidentInput(
            id=inc.id,
            incident_code=inc.incident_code,
            title=inc.title,
            description=inc.description,
            category=inc.category,
            latitude=inc.latitude,
            longitude=inc.longitude,
            district_name=inc.district_name,
            village_name=inc.village_name,
            created_at=inc.created_at,
        )
        for inc in db_incidents
    ]

    return duplicate_detector.scan_duplicates(candidate, existing_inputs)


@router.post("/score-duplicate", response_model=AIDuplicateScoreResponse)
async def score_duplicate(
    lat_a: float,
    lng_a: float,
    text_a: str,
    lat_b: float,
    lng_b: float,
    text_b: str,
    time_diff_hours: float = 1.5,
):
    """Fast pairwise duplicate probability score between two coordinate and text pairs."""
    dist_meters = haversine_distance_meters(lat_a, lng_a, lat_b, lng_b)
    spatial_score = max(0.0, 1.0 - (dist_meters / 1000.0))
    semantic_sim = jaccard_similarity(text_a, text_b)
    temporal_score = max(0.0, 1.0 - (time_diff_hours / 24.0))

    prob = (spatial_score * 0.45) + (semantic_sim * 0.35) + (temporal_score * 0.20)
    prob = round(min(1.0, prob), 2)

    return AIDuplicateScoreResponse(
        incident_a_id="A",
        incident_b_id="B",
        distance_meters=round(dist_meters, 1),
        time_difference_hours=time_diff_hours,
        semantic_similarity=round(semantic_sim, 2),
        overall_duplicate_probability=prob,
        is_likely_duplicate=prob >= 0.60,
    )


# ============================================================================
# Service D: Explainable Prioritization
# ============================================================================

@router.post("/prioritize", response_model=PrioritizationResponse)
async def calculate_explainable_priority(request: PrioritizationRequest):
    """Compute deterministic multi-factor priority score (0-100) with complete factor breakdown.
    Considers life threat, medical urgency, population affected, accessibility, resources, and freshness.
    """
    return prioritizer_engine.evaluate(request)


# ============================================================================
# Service E: RAG Knowledge Assistant
# ============================================================================

@router.post("/rag/query", response_model=RAGResponse)
async def query_disaster_knowledge_base(request: RAGQueryRequest):
    """Query verified official OSDMA and NDMA disaster management Standard Operating Procedures.
    Returns source citations with document, section, and page numbers. Refuses out-of-domain queries.
    """
    return await rag_assistant.answer_query(request)


# ============================================================================
# Service F: Evaluation Benchmarks
# ============================================================================

@router.get("/evaluation/report", response_model=SystemAIEvaluationReport)
async def get_ai_evaluation_report():
    """Run labelled benchmark evaluation test suites across all AI engines and return measured results."""
    return await evaluator.run_full_evaluation_suite()
