"""AapadaOps Advanced Duplicate Detection Engine.

Combines text embeddings (character and word n-gram TF-IDF cosine similarity),
geographic distance, time difference, category alignment, and shared operational attributes.
Strict safety rule: Never merges incidents automatically.
"""

import math
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple
import numpy as np
from app.ai.schemas import (
    AIDuplicateDetectionResponse,
    AIDuplicateMatch,
    CandidateIncidentInput,
    DuplicateMatchFactor,
)
from app.models.incident import IncidentCategory
from app.services.spatial_service import haversine_distance_meters

# Category compatibility matrix: pairs of disaster categories that frequently co-occur in the same event
COMPATIBLE_CATEGORIES = {
    (IncidentCategory.FLOOD, IncidentCategory.EMBANKMENT_BREACH),
    (IncidentCategory.FLOOD, IncidentCategory.STRANDED_PERSONS),
    (IncidentCategory.CYCLONE_WIND, IncidentCategory.TREE_FALL),
    (IncidentCategory.CYCLONE_WIND, IncidentCategory.POWER_FAILURE),
    (IncidentCategory.TREE_FALL, IncidentCategory.ROAD_BLOCK),
    (IncidentCategory.STRANDED_PERSONS, IncidentCategory.MEDICAL_EMERGENCY),
}


def build_char_ngram_vector(text: str, n: int = 3) -> Dict[str, float]:
    """Generate normalized character n-gram frequency vector."""
    clean = re.sub(r"\s+", " ", text.lower().strip())
    if len(clean) < n:
        return {clean: 1.0}
    counts: Dict[str, float] = {}
    total = 0
    for i in range(len(clean) - n + 1):
        gram = clean[i : i + n]
        counts[gram] = counts.get(gram, 0.0) + 1.0
        total += 1
    # Normalize L2 norm
    norm = math.sqrt(sum(v * v for v in counts.values()))
    if norm > 0:
        return {k: v / norm for k, v in counts.items()}
    return counts


def cosine_similarity(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    """Calculate dot product of normalized sparse vectors."""
    if not v1 or not v2:
        return 0.0
    # Iterate over smaller dict
    small, big = (v1, v2) if len(v1) < len(v2) else (v2, v1)
    dot = sum(val * big.get(key, 0.0) for key, val in small.items())
    return max(0.0, min(1.0, float(dot)))


class AdvancedDuplicateDetector:
    """Multi-factor explainable duplicate detector with strict human review guardrail."""

    @classmethod
    def calculate_text_similarity(cls, text_a: str, text_b: str) -> float:
        """Compute hybrid word Jaccard and character 3-gram semantic similarity."""
        # 1. Word token Jaccard
        words_a = set(re.findall(r"\w+", text_a.lower()))
        words_b = set(re.findall(r"\w+", text_b.lower()))
        jaccard = 0.0
        if words_a and words_b:
            jaccard = len(words_a.intersection(words_b)) / len(words_a.union(words_b))

        # 2. Character 3-gram cosine similarity (robust to spelling variations & Odia suffixes)
        v1 = build_char_ngram_vector(text_a, n=3)
        v2 = build_char_ngram_vector(text_b, n=3)
        ngram_sim = cosine_similarity(v1, v2)

        # Blended text similarity (60% character n-gram, 40% word tokens)
        return round((ngram_sim * 0.6) + (jaccard * 0.4), 3)

    @classmethod
    def evaluate_pair(
        cls,
        candidate: CandidateIncidentInput,
        existing: CandidateIncidentInput,
    ) -> AIDuplicateMatch:
        """Evaluate match likelihood between an incoming report and an existing incident."""
        factors: List[DuplicateMatchFactor] = []

        # 1. Geographic distance (Weight 0.35, threshold 2000m)
        dist_m = haversine_distance_meters(
            candidate.latitude, candidate.longitude, existing.latitude, existing.longitude
        )
        geo_score = max(0.0, 1.0 - (dist_m / 2000.0))
        factors.append(
            DuplicateMatchFactor(
                factor="GEOGRAPHIC_PROXIMITY",
                score=round(geo_score, 2),
                weight=0.35,
                detail=f"Reports are located {int(dist_m)} meters apart (threshold: 2000m).",
            )
        )

        # 2. Text Semantic Similarity (Weight 0.30)
        text_sim = cls.calculate_text_similarity(
            f"{candidate.title}. {candidate.description}",
            f"{existing.title}. {existing.description}",
        )
        factors.append(
            DuplicateMatchFactor(
                factor="TEXT_SEMANTIC_SIMILARITY",
                score=round(text_sim, 2),
                weight=0.30,
                detail=f"Character and vocabulary overlap measured at {int(text_sim * 100)}%.",
            )
        )

        # 3. Category Match (Weight 0.15)
        cat_score = 0.2
        if candidate.category == existing.category:
            cat_score = 1.0
            cat_detail = f"Identical disaster category '{candidate.category.value}'."
        elif (candidate.category, existing.category) in COMPATIBLE_CATEGORIES or (
            existing.category,
            candidate.category,
        ) in COMPATIBLE_CATEGORIES:
            cat_score = 0.75
            cat_detail = (
                f"Compatible disaster phenomena ('{candidate.category.value}' and '{existing.category.value}')."
            )
        else:
            cat_detail = (
                f"Different categories ('{candidate.category.value}' vs '{existing.category.value}')."
            )

        factors.append(
            DuplicateMatchFactor(
                factor="CATEGORY_ALIGNMENT",
                score=round(cat_score, 2),
                weight=0.15,
                detail=cat_detail,
            )
        )

        # 4. Temporal Proximity (Weight 0.10, window 72 hours)
        now = datetime.now(timezone.utc)
        time_a = candidate.created_at or now
        time_b = existing.created_at or now
        if time_a.tzinfo is None:
            time_a = time_a.replace(tzinfo=timezone.utc)
        if time_b.tzinfo is None:
            time_b = time_b.replace(tzinfo=timezone.utc)

        time_diff_hours = abs((time_a - time_b).total_seconds()) / 3600.0
        time_score = max(0.0, 1.0 - (time_diff_hours / 72.0))
        factors.append(
            DuplicateMatchFactor(
                factor="TEMPORAL_PROXIMITY",
                score=round(time_score, 2),
                weight=0.10,
                detail=f"Reports filed within {round(time_diff_hours, 1)} hours of each other.",
            )
        )

        # 5. Shared Attributes (Weight 0.10)
        attr_score = 0.0
        attr_notes = []
        if candidate.district_name and existing.district_name and candidate.district_name.lower() == existing.district_name.lower():
            attr_score += 0.4
            attr_notes.append(f"same district ({candidate.district_name})")
        if candidate.village_name and existing.village_name and candidate.village_name.lower() in existing.village_name.lower():
            attr_score += 0.4
            attr_notes.append(f"same village ({candidate.village_name})")
        if candidate.reporter_phone and existing.reporter_phone and candidate.reporter_phone == existing.reporter_phone:
            attr_score += 0.6
            attr_notes.append("identical reporter phone")

        attr_score = min(1.0, attr_score)
        factors.append(
            DuplicateMatchFactor(
                factor="SHARED_ATTRIBUTES",
                score=round(attr_score, 2),
                weight=0.10,
                detail="; ".join(attr_notes) if attr_notes else "No shared specific metadata tags.",
            )
        )

        # Composite Score Calculation
        overall = sum(f.score * f.weight for f in factors)
        overall = round(min(1.0, max(0.0, overall)), 2)
        is_dup = overall >= 0.65

        # Plain language explanation
        explanation_parts = [
            f"Distance: {int(dist_m)}m",
            f"Time Delta: {round(time_diff_hours, 1)}h",
            f"Text Sim: {int(text_sim * 100)}%",
        ]
        if candidate.category == existing.category:
            explanation_parts.append(f"Category: {candidate.category.value}")
        if attr_notes:
            explanation_parts.append(", ".join(attr_notes))

        plain_explanation = (
            f"Potential duplicate ({int(overall * 100)}% match): "
            + "; ".join(explanation_parts)
            + ". Human review required before merging."
        )

        return AIDuplicateMatch(
            incident_id=existing.id or "UNKNOWN",
            incident_code=existing.incident_code or "INC-REF",
            title=existing.title,
            category=existing.category,
            distance_meters=round(dist_m, 1),
            time_diff_hours=round(time_diff_hours, 1),
            text_similarity=round(text_sim, 2),
            overall_score=overall,
            is_probable_duplicate=is_dup,
            factors=factors,
            plain_explanation=plain_explanation,
        )

    @classmethod
    def scan_duplicates(
        cls,
        candidate: CandidateIncidentInput,
        existing_incidents: List[CandidateIncidentInput],
        min_threshold: float = 0.50,
    ) -> AIDuplicateDetectionResponse:
        """Scan candidate against all active incidents, returning sorted matches."""
        matches: List[AIDuplicateMatch] = []

        for existing in existing_incidents:
            if existing.id == candidate.id:
                continue
            match = cls.evaluate_pair(candidate, existing)
            if match.overall_score >= min_threshold:
                matches.append(match)

        # Sort matches by overall score descending
        matches.sort(key=lambda m: m.overall_score, reverse=True)
        probable_count = sum(1 for m in matches if m.is_probable_duplicate)

        return AIDuplicateDetectionResponse(
            candidate_id=candidate.id or "CANDIDATE",
            total_candidates_analyzed=len(existing_incidents),
            probable_duplicates_count=probable_count,
            matches=matches,
        )


duplicate_detector = AdvancedDuplicateDetector()

