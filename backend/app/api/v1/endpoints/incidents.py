"""AapadaOps Incident Management and Lifecycle State Machine API."""

import random
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException, InvalidStateTransitionError, NotFoundError
from app.core.rate_limiter import rate_limiter
from app.core.websocket_manager import ws_manager
from app.api.v1.deps import PaginationParams, get_current_user, get_optional_user, require_roles
from app.models.incident import (
    Incident,
    IncidentCategory,
    IncidentSeverity,
    IncidentStatus,
)
from app.models.report import IncidentReport, ReportSource
from app.models.user import User, UserRole
from app.schemas.incident import (
    IncidentCreate,
    IncidentListResponse,
    IncidentResponse,
    IncidentStatusTransition,
    IncidentUpdate,
)
from app.services.ai_service import ai_engine
from app.services.audit_service import log_audit_event
from app.services.duplicate_service import check_for_duplicates
from app.services.spatial_service import is_coordinate_in_odisha

router = APIRouter(prefix="/incidents", tags=["Incidents"])

AUTHORIZED_PII_ROLES = {
    UserRole.SUPER_ADMIN,
    UserRole.DISTRICT_COLLECTOR,
    UserRole.INCIDENT_VERIFICATION_OFFICER,
    UserRole.RESPONSE_COORDINATOR,
    UserRole.FIELD_WORKER,
}


def mask_phone_pii(phone: str) -> str:
    """Mask citizen reporter phone numbers for DPDP 2023 privacy compliance."""
    if not phone:
        return "XXXXX-XXXXX"
    clean = phone.strip()
    if len(clean) >= 10:
        return clean[:-5] + "XXXXX"
    return clean[:2] + "****" + clean[-2:]


def serialize_incident_with_privacy(incident: Incident, current_user: Optional[User]) -> IncidentResponse:
    """Serialize incident model to response schema, masking sensitive citizen PII for unprivileged viewers."""
    can_view_pii = current_user is not None and current_user.role in AUTHORIZED_PII_ROLES
    resp_data = IncidentResponse.model_validate(incident)
    if not can_view_pii:
        resp_data.reporter_phone = mask_phone_pii(resp_data.reporter_phone)
    return resp_data

# Permitted state transitions in the AapadaOps Lifecycle
VALID_TRANSITIONS = {
    IncidentStatus.SUBMITTED: {
        IncidentStatus.PROCESSING,
        IncidentStatus.NEEDS_VERIFICATION,
        IncidentStatus.VERIFIED,
        IncidentStatus.REJECTED,
        IncidentStatus.DUPLICATE,
    },
    IncidentStatus.PROCESSING: {
        IncidentStatus.NEEDS_VERIFICATION,
        IncidentStatus.VERIFIED,
        IncidentStatus.REJECTED,
        IncidentStatus.DUPLICATE,
    },
    IncidentStatus.NEEDS_VERIFICATION: {
        IncidentStatus.VERIFIED,
        IncidentStatus.REJECTED,
        IncidentStatus.DUPLICATE,
        IncidentStatus.DISPUTED,
    },
    IncidentStatus.VERIFIED: {
        IncidentStatus.PRIORITIZED,
        IncidentStatus.ASSIGNED,
        IncidentStatus.REOPENED,
    },
    IncidentStatus.PRIORITIZED: {
        IncidentStatus.ASSIGNED,
        IncidentStatus.IN_PROGRESS,
        IncidentStatus.REOPENED,
    },
    IncidentStatus.ASSIGNED: {
        IncidentStatus.IN_PROGRESS,
        IncidentStatus.VERIFIED,
        IncidentStatus.REOPENED,
    },
    IncidentStatus.IN_PROGRESS: {
        IncidentStatus.RESOLVED,
        IncidentStatus.ASSIGNED,
        IncidentStatus.DISPUTED,
    },
    IncidentStatus.RESOLVED: {
        IncidentStatus.CLOSED,
        IncidentStatus.REOPENED,
    },
    IncidentStatus.CLOSED: {
        IncidentStatus.REOPENED,
    },
    IncidentStatus.DUPLICATE: {
        IncidentStatus.REOPENED,
    },
    IncidentStatus.REJECTED: {
        IncidentStatus.REOPENED,
    },
    IncidentStatus.DISPUTED: {
        IncidentStatus.NEEDS_VERIFICATION,
        IncidentStatus.VERIFIED,
        IncidentStatus.REOPENED,
    },
    IncidentStatus.REOPENED: {
        IncidentStatus.NEEDS_VERIFICATION,
        IncidentStatus.VERIFIED,
        IncidentStatus.PRIORITIZED,
    },
}


def generate_incident_code() -> str:
    """Generate official Odisha disaster incident code: INC-OD-2026-XXXX."""
    random_num = random.randint(1000, 9999)
    return f"INC-OD-2026-{random_num}"


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_in: IncidentCreate,
    request: Request,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a disaster incident report (citizen SOS or official field dispatch)."""
    # Rate limit public incident submissions
    rate_limiter.check(request, max_requests=15, window_seconds=60)

    # Validate coordinates inside Odisha
    if not is_coordinate_in_odisha(incident_in.latitude, incident_in.longitude):
        raise AppException(
            message=f"Provided coordinates ({incident_in.latitude}, {incident_in.longitude}) fall outside the administrative boundaries of Odisha.",
            status_code=400,
            code="OUT_OF_BOUNDS_LOCATION",
        )

    # Run AI Natural Language Analysis and Advisory Assessment
    ai_advisory = ai_engine.analyze_report(f"{incident_in.title}. {incident_in.description}")

    # Build Incident Entity
    incident_code = generate_incident_code()
    incident = Incident(
        incident_code=incident_code,
        title=incident_in.title,
        description=incident_in.description,
        category=incident_in.category,
        reported_severity=incident_in.reported_severity,
        status=IncidentStatus.SUBMITTED,
        district_id=incident_in.district_id,
        district_name=incident_in.district_name,
        block_id=incident_in.block_id,
        block_name=incident_in.block_name,
        village_name=incident_in.village_name,
        latitude=incident_in.latitude,
        longitude=incident_in.longitude,
        reporter_name=incident_in.reporter_name,
        reporter_phone=incident_in.reporter_phone,
        reporter_role="OFFICIAL" if current_user else "CITIZEN",
        ai_confidence_score=ai_advisory["confidence_score"],
        ai_raw_classification=ai_advisory["ai_advisory_statement"],
        ai_urgency_score=ai_advisory["urgency_score"],
        estimated_affected_people=max(incident_in.estimated_affected_people, ai_advisory["extracted_stranded_count"]),
        casualties_reported=max(incident_in.casualties_reported, ai_advisory["extracted_casualties"]),
        stranded_count=max(incident_in.stranded_count, ai_advisory["extracted_stranded_count"]),
    )
    db.add(incident)
    await db.flush()

    # Create associated primary report record
    report = IncidentReport(
        incident_id=incident.id,
        source_type=ReportSource.FIELD_WORKER_APP if current_user else ReportSource.CITIZEN_WEB,
        raw_text=f"{incident_in.title}\n\n{incident_in.description}",
        text_language=ai_advisory["detected_language"],
        reporter_name=incident_in.reporter_name,
        reporter_phone=incident_in.reporter_phone,
        gps_lat=incident_in.latitude,
        gps_lng=incident_in.longitude,
        submission_ip=request.client.host if request.client else None,
    )
    db.add(report)

    # Run Automated Duplicate Detection
    await check_for_duplicates(db, incident)

    # Audit Trail
    await log_audit_event(
        db,
        action="SUBMIT_INCIDENT",
        entity_type="INCIDENT",
        entity_id=incident.id,
        actor=current_user,
        description=f"Incident {incident.incident_code} submitted at {incident.district_name}.",
        changes={"category": incident.category.value, "severity": incident.reported_severity.value},
        ip_address=request.client.host if request.client else None,
    )

    await db.commit()
    await db.refresh(incident)

    # Real-time WebSocket Broadcast
    await ws_manager.broadcast(
        channel="incidents",
        message={
            "event": "INCIDENT_CREATED",
            "incident": {
                "id": incident.id,
                "incident_code": incident.incident_code,
                "title": incident.title,
                "category": incident.category.value,
                "severity": incident.reported_severity.value,
                "district_name": incident.district_name,
                "latitude": incident.latitude,
                "longitude": incident.longitude,
                "status": incident.status.value,
                "created_at": incident.created_at.isoformat(),
            },
        },
    )

    return incident


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    district: Optional[str] = None,
    status: Optional[IncidentStatus] = None,
    severity: Optional[IncidentSeverity] = None,
    category: Optional[IncidentCategory] = None,
    is_verified: Optional[bool] = None,
    is_duplicate: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Query incidents with filtering by district, lifecycle status, severity, and full-text keyword."""
    query = select(Incident)

    if district:
        query = query.where(Incident.district_name == district)
    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(
            or_(Incident.verified_priority == severity, Incident.reported_severity == severity)
        )
    if category:
        query = query.where(Incident.category == category)
    if is_verified is not None:
        query = query.where(Incident.is_verified == is_verified)
    if is_duplicate is not None:
        query = query.where(Incident.is_duplicate == is_duplicate)
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                Incident.title.ilike(search_filter),
                Incident.description.ilike(search_filter),
                Incident.incident_code.ilike(search_filter),
                Incident.village_name.ilike(search_filter),
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.order_by(desc(Incident.created_at)).offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    # Apply PII masking for unauthorized viewers
    serialized_items = [
        serialize_incident_with_privacy(item, current_user) for item in items
    ]

    return IncidentListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=serialized_items,
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve full operational incident record by ID with PII protection."""
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise NotFoundError("Incident", incident_id)
    return serialize_incident_with_privacy(incident, current_user)


@router.patch("/{incident_id}/status", response_model=IncidentResponse)
async def transition_incident_status(
    incident_id: str,
    transition: IncidentStatusTransition,
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
    """Execute lifecycle state transition enforcing validated transition matrix and audit logging."""
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise NotFoundError("Incident", incident_id)

    # Enforce State Machine Rules
    allowed = VALID_TRANSITIONS.get(incident.status, set())
    if transition.status not in allowed:
        raise InvalidStateTransitionError(
            current_state=incident.status.value,
            attempted_state=transition.status.value,
            reason=f"Transition from '{incident.status.value}' to '{transition.status.value}' is forbidden by OSDMA protocol.",
        )

    previous_status = incident.status
    incident.status = transition.status

    if transition.verified_priority:
        incident.verified_priority = transition.verified_priority

    if transition.status == IncidentStatus.VERIFIED:
        incident.is_verified = True
        incident.verified_by_id = current_user.id
        incident.verified_at = datetime.now(timezone.utc)
        incident.verification_notes = transition.notes

    await log_audit_event(
        db,
        action="TRANSITION_STATUS",
        entity_type="INCIDENT",
        entity_id=incident.id,
        actor=current_user,
        description=f"Status changed from {previous_status.value} to {incident.status.value}.",
        changes={
            "from_status": previous_status.value,
            "to_status": incident.status.value,
            "notes": transition.notes,
        },
    )

    await db.commit()
    await db.refresh(incident)

    # Broadcast status change
    await ws_manager.broadcast(
        channel="incidents",
        message={
            "event": "INCIDENT_STATUS_CHANGED",
            "incident_id": incident.id,
            "incident_code": incident.incident_code,
            "previous_status": previous_status.value,
            "new_status": incident.status.value,
            "updated_at": incident.updated_at.isoformat(),
        },
    )

    return incident

