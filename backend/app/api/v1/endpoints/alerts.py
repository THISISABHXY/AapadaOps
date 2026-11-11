"""AapadaOps SATARK Early Warning Alerts API."""

import json
import random
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.websocket_manager import ws_manager
from app.api.v1.deps import require_roles
from app.models.alert import AlertBroadcast
from app.models.user import User, UserRole
from app.schemas.analytics import AlertCreate, AlertResponse
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/alerts", tags=["SATARK Alerts"])


@router.get("", response_model=List[AlertResponse])
async def list_active_alerts(db: AsyncSession = Depends(get_db)):
    """Retrieve active early warning advisories and meteorological alerts."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(AlertBroadcast)
        .where(AlertBroadcast.is_active == True, AlertBroadcast.valid_until > now)  # noqa: E712
        .order_by(AlertBroadcast.issued_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_in: AlertCreate,
    current_user: User = Depends(
        require_roles(UserRole.SUPER_ADMIN, UserRole.DISTRICT_COLLECTOR)
    ),
    db: AsyncSession = Depends(get_db),
):
    """Publish SATARK meteorological bulletin or emergency evacuation broadcast."""
    alert_code = f"SATARK-{alert_in.severity.value}-{random.randint(100, 999)}"
    now = datetime.now(timezone.utc)

    alert = AlertBroadcast(
        alert_code=alert_code,
        severity=alert_in.severity,
        hazard_type=alert_in.hazard_type,
        headline=alert_in.headline,
        advisory_body=alert_in.advisory_body,
        affected_districts_json=json.dumps(alert_in.affected_districts),
        source=alert_in.source,
        issued_at=now,
        valid_until=alert_in.valid_until,
        is_active=True,
    )
    db.add(alert)
    await db.flush()

    await log_audit_event(
        db,
        action="ISSUE_ALERT",
        entity_type="ALERT",
        entity_id=alert.id,
        actor=current_user,
        description=f"Issued {alert.severity.value} warning: {alert.headline}.",
        changes={"affected_districts": alert_in.affected_districts},
    )

    await db.commit()
    await db.refresh(alert)

    # Real-time WebSocket broadcast to all subscribers
    await ws_manager.broadcast(
        channel="alerts",
        message={
            "event": "ALERT_ISSUED",
            "alert": {
                "id": alert.id,
                "alert_code": alert.alert_code,
                "severity": alert.severity.value,
                "hazard_type": alert.hazard_type.value,
                "headline": alert.headline,
                "affected_districts": alert_in.affected_districts,
                "valid_until": alert.valid_until.isoformat(),
            },
        },
    )

    return alert
