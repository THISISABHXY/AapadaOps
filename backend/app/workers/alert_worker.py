"""AapadaOps Background Alert & Common Alerting Protocol (CAP) Worker."""

import logging
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import DisasterAlert, AlertSeverity
from app.services.audit_service import log_audit_event

logger = logging.getLogger("aapadaops.workers.alert")


async def process_pending_alerts(db: AsyncSession) -> Dict[str, Any]:
    """Scan and process active disaster alerts, expiring outdated broadcasts."""
    now = datetime.now(timezone.utc)
    stmt = select(DisasterAlert).where(DisasterAlert.is_active == True)
    result = await db.execute(stmt)
    active_alerts = result.scalars().all()

    expired_count = 0
    active_count = 0

    for alert in active_alerts:
        if alert.expires_at and alert.expires_at < now:
            alert.is_active = False
            expired_count += 1
            logger.info(f"Alert {alert.headline} (ID: {alert.id}) has expired and was marked inactive.")
        else:
            active_count += 1

    if expired_count > 0:
        await db.commit()

    return {
        "timestamp": now.isoformat(),
        "active_alerts_count": active_count,
        "expired_alerts_count": expired_count,
        "status": "COMPLETED",
    }

