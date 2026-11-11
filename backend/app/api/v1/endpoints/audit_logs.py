"""AapadaOps Regulatory Audit Logs API."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.deps import PaginationParams, require_roles
from app.models.audit import AuditLog
from app.models.user import User, UserRole
from app.schemas.analytics import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit & Governance"])


@router.get("", response_model=List[AuditLogResponse])
async def list_audit_logs(
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.INCIDENT_VERIFICATION_OFFICER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve immutable audit trail records for compliance, dispute resolution, and forensics."""
    query = select(AuditLog)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type.upper())
    if action:
        query = query.where(AuditLog.action == action.upper())

    query = query.order_by(AuditLog.created_at.desc()).offset(pagination.skip).limit(pagination.limit)
    result = await db.execute(query)
    return result.scalars().all()

