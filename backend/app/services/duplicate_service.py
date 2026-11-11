"""AapadaOps Spatial-Temporal Incident Duplicate Detection & Merging."""

import re
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident import Incident, IncidentStatus
from app.models.duplicate import DuplicateCluster, ClusterStatus
from app.models.user import User
from app.services.spatial_service import find_nearby_incidents
from app.services.audit_service import log_audit_event


def tokenize(text: str) -> set:
    """Split text into lowercase token words."""
    words = re.findall(r"\w+", text.lower())
    return set(words)


def jaccard_similarity(text1: str, text2: str) -> float:
    """Calculate token Jaccard overlap similarity (0.0 to 1.0)."""
    s1 = tokenize(text1)
    s2 = tokenize(text2)
    if not s1 or not s2:
        return 0.0
    intersection = len(s1.intersection(s2))
    union = len(s1.union(s2))
    return intersection / union if union > 0 else 0.0


async def check_for_duplicates(
    db: AsyncSession,
    incident: Incident,
    radius_meters: float = 500.0,
    time_window_hours: float = 24.0,
) -> Optional[DuplicateCluster]:
    """Scan existing incidents to identify if new incident is a duplicate candidate."""
    nearby = await find_nearby_incidents(
        db,
        latitude=incident.latitude,
        longitude=incident.longitude,
        radius_meters=radius_meters,
        district_name=incident.district_name,
    )

    candidates: List[Tuple[Incident, float]] = []
    now = datetime.now(timezone.utc)

    for cand_inc, dist in nearby:
        if cand_inc.id == incident.id:
            continue
        # Ensure timezone compatibility across SQLite and PostgreSQL
        created_at = cand_inc.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        time_diff = abs((now - created_at).total_seconds()) / 3600.0
        if time_diff <= time_window_hours:
            candidates.append((cand_inc, dist))

    if not candidates:
        return None

    # Pick the closest candidate as primary
    primary_candidate, dist = candidates[0]
    semantic_sim = jaccard_similarity(incident.description, primary_candidate.description)
    category_match = 1.0 if incident.category == primary_candidate.category else 0.3

    # Calculate overall duplicate confidence
    spatial_score = max(0.0, 1.0 - (dist / radius_meters))
    confidence = (spatial_score * 0.4) + (category_match * 0.3) + (semantic_sim * 0.3)

    if confidence >= 0.60:
        # Create or update duplicate cluster
        cluster = DuplicateCluster(
            primary_incident_id=primary_candidate.id,
            status=ClusterStatus.PENDING_REVIEW,
            spatial_radius_meters=radius_meters,
            confidence_score=round(confidence, 2),
            duplicate_count=2,
            cluster_summary=(
                f"Potential duplicate reports near {incident.village_name or 'village'} "
                f"({int(dist)}m apart, category '{incident.category.value}', similarity {int(confidence*100)}%)."
            ),
        )
        db.add(cluster)
        await db.flush()

        incident.is_duplicate = True
        incident.duplicate_cluster_id = cluster.id
        return cluster

    return None


async def merge_duplicate_incidents(
    db: AsyncSession,
    master_incident: Incident,
    duplicate_incidents: List[Incident],
    officer: User,
    merge_notes: str = "",
) -> Incident:
    """Merge confirmed duplicate incidents into the designated master incident."""
    for dup in duplicate_incidents:
        dup.is_duplicate = True
        dup.duplicate_of_id = master_incident.id
        dup.status = IncidentStatus.DUPLICATE
        dup.verification_notes = f"Merged into master {master_incident.incident_code}. Note: {merge_notes}"

        # Aggregate affected estimates
        master_incident.estimated_affected_people += dup.estimated_affected_people
        master_incident.stranded_count += dup.stranded_count
        master_incident.casualties_reported += dup.casualties_reported

        await log_audit_event(
            db,
            action="MERGE_DUPLICATE",
            entity_type="INCIDENT",
            entity_id=dup.id,
            actor=officer,
            description=f"Incident {dup.incident_code} merged into master {master_incident.incident_code}.",
            changes={"master_incident_id": master_incident.id, "merge_notes": merge_notes},
        )

    await log_audit_event(
        db,
        action="UPDATE_MASTER_FROM_DUPLICATES",
        entity_type="INCIDENT",
        entity_id=master_incident.id,
        actor=officer,
        description=f"Master incident {master_incident.incident_code} updated with merged duplicate data.",
        changes={"merged_count": len(duplicate_incidents)},
    )

    await db.commit()
    await db.refresh(master_incident)
    return master_incident
