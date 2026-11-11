"""AapadaOps Human-in-the-Loop Incident Verification API."""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.websocket_manager import ws_manager
from app.api.v1.deps import require_roles
from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.models.user import User, UserRole
from app.models.verification import VerificationLog
from app.schemas.incident import IncidentResponse
from app.schemas.duplicate import VerificationResponse, VerificationSubmitRequest
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/verification", tags=["Verification"])


@router.get("/queue", response_model=List[IncidentResponse])
async def get_verification_queue(
    district: Optional[str] = None,
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
    """Retrieve unverified incidents awaiting human officer signoff."""
    query = select(Incident).where(
        or_(
            Incident.status == IncidentStatus.SUBMITTED,
            Incident.status == IncidentStatus.NEEDS_VERIFICATION,
        ),
        Incident.is_verified == False,  # noqa: E712
    )
    if district:
        query = query.where(Incident.district_name == district)
    elif current_user.jurisdiction_district and current_user.role != UserRole.SUPER_ADMIN:
        query = query.where(Incident.district_name == current_user.jurisdiction_district)

    query = query.order_by(Incident.created_at.asc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/{incident_id}/verify", response_model=IncidentResponse)
async def verify_incident(
    incident_id: str,
    verification_in: VerificationSubmitRequest,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.INCIDENT_VERIFICATION_OFFICER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Verify an incident report, confirming authenticity, assigning verified priority, and signing off."""
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise NotFoundError("Incident", incident_id)

    previous_status = incident.status
    previous_priority = incident.verified_priority or incident.reported_severity

    incident.is_verified = True
    incident.status = verification_in.new_status
    incident.verified_priority = verification_in.verified_priority
    incident.verified_by_id = current_user.id
    incident.verified_at = datetime.now(timezone.utc)
    incident.verification_notes = verification_in.verification_notes

    # Create immutable verification record
    v_log = VerificationLog(
        incident_id=incident.id,
        officer_id=current_user.id,
        previous_status=previous_status.value,
        new_status=incident.status.value,
        previous_priority=previous_priority.value if previous_priority else None,
        new_priority=verification_in.verified_priority.value,
        verification_notes=verification_in.verification_notes,
        confidence_override=verification_in.confidence_override,
    )
    db.add(v_log)

    # Record audit log
    await log_audit_event(
        db,
        action="VERIFY_INCIDENT",
        entity_type="INCIDENT",
        entity_id=incident.id,
        actor=current_user,
        description=f"Incident {incident.incident_code} verified as {incident.status.value} ({incident.verified_priority.value}).",
        changes={
            "status": incident.status.value,
            "verified_priority": incident.verified_priority.value,
            "verification_notes": incident.verification_notes,
        },
    )

    await db.commit()
    await db.refresh(incident)

    # Real-time WebSocket notification
    await ws_manager.broadcast(
        channel="incidents",
        message={
            "event": "INCIDENT_VERIFIED",
            "incident_id": incident.id,
            "incident_code": incident.incident_code,
            "verified_priority": incident.verified_priority.value,
            "verified_by": current_user.full_name,
            "verified_at": incident.verified_at.isoformat(),
        },
    )

    return incident
