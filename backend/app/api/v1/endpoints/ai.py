"""AapadaOps AI Advisory Processing API."""

from fastapi import APIRouter
from app.schemas.analytics import (
    AIDuplicateScoreResponse,
    AITextAnalysisRequest,
    AITextAnalysisResponse,
)
from app.services.ai_service import ai_engine
from app.services.duplicate_service import jaccard_similarity
from app.services.spatial_service import haversine_distance_meters

router = APIRouter(prefix="/ai", tags=["AI Advisory Engine"])


@router.post("/analyze-text", response_model=AITextAnalysisResponse)
async def analyze_report_text(request: AITextAnalysisRequest):
    """Analyze raw citizen or field text in English or Odia to generate automated triage advisory."""
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
    """Evaluate duplicate probability between two incident reports."""
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
