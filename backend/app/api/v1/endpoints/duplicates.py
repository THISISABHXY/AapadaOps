"""AapadaOps Incident Duplicate Review & Merge API."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.api.v1.deps import require_roles
from app.models.duplicate import ClusterStatus, DuplicateCluster
from app.models.incident import Incident
from app.models.user import User, UserRole
from app.schemas.duplicate import DuplicateClusterResponse, MergeDuplicateRequest
from app.schemas.incident import IncidentResponse
from app.services.duplicate_service import merge_duplicate_incidents

router = APIRouter(prefix="/duplicates", tags=["Duplicate Detection"])


@router.get("/clusters", response_model=List[DuplicateClusterResponse])
async def list_duplicate_clusters(
    status: ClusterStatus = ClusterStatus.PENDING_REVIEW,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.INCIDENT_VERIFICATION_OFFICER,
            UserRole.RESPONSE_COORDINATOR,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve clusters of potential duplicate incidents detected within 500m/24h."""
    result = await db.execute(
        select(DuplicateCluster)
        .where(DuplicateCluster.status == status)
        .order_by(DuplicateCluster.created_at.desc())
    )
    clusters = result.scalars().all()
    response_items = []

    for cl in clusters:
        # Load primary incident
        p_res = await db.execute(select(Incident).where(Incident.id == cl.primary_incident_id))
        primary_inc = p_res.scalar_one_or_none()

        # Load linked duplicates
        d_res = await db.execute(select(Incident).where(Incident.duplicate_cluster_id == cl.id))
        duplicates = d_res.scalars().all()

        response_items.append(
            DuplicateClusterResponse(
                id=cl.id,
                primary_incident_id=cl.primary_incident_id,
                status=cl.status,
                spatial_radius_meters=cl.spatial_radius_meters,
                confidence_score=cl.confidence_score,
                cluster_summary=cl.cluster_summary,
                duplicate_count=cl.duplicate_count,
                created_at=cl.created_at,
                primary_incident=IncidentResponse.model_validate(primary_inc) if primary_inc else None,
                duplicate_incidents=[IncidentResponse.model_validate(d) for d in duplicates],
            )
        )
    return response_items


@router.post("/merge", response_model=IncidentResponse)
async def merge_incidents(
    merge_req: MergeDuplicateRequest,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.INCIDENT_VERIFICATION_OFFICER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Merge confirmed duplicate incidents into the designated master incident."""
    master_res = await db.execute(
        select(Incident).where(Incident.id == merge_req.master_incident_id)
    )
    master = master_res.scalar_one_or_none()
    if not master:
        raise NotFoundError("Master Incident", merge_req.master_incident_id)

    dup_res = await db.execute(
        select(Incident).where(Incident.id.in_(merge_req.duplicate_incident_ids))
    )
    duplicates = dup_res.scalars().all()
    if not duplicates:
        raise NotFoundError("Duplicate Incidents", merge_req.duplicate_incident_ids)

    merged_master = await merge_duplicate_incidents(
        db,
        master_incident=master,
        duplicate_incidents=duplicates,
        officer=current_user,
        merge_notes=merge_req.merge_notes or "",
    )
    return merged_master


@router.post("/dismiss/{cluster_id}")
async def dismiss_cluster(
    cluster_id: str,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.INCIDENT_VERIFICATION_OFFICER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Dismiss a duplicate alert as separate distinct incidents."""
    result = await db.execute(select(DuplicateCluster).where(DuplicateCluster.id == cluster_id))
    cluster = result.scalar_one_or_none()
    if not cluster:
        raise NotFoundError("DuplicateCluster", cluster_id)

    cluster.status = ClusterStatus.DISMISSED
    await db.commit()
    return {"message": f"Cluster {cluster_id} dismissed. Incidents kept distinct."}

