"""AapadaOps Background Telemetry & Incident Lifecycle Worker."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident, IncidentStatus, IncidentSeverity
from app.models.shelter import Shelter
from app.services.audit_service import log_audit_event

logger = logging.getLogger("aapadaops.workers.telemetry")


async def monitor_stale_incidents(
    db: AsyncSession,
    stale_threshold_hours: float = 2.0,
) -> Dict[str, Any]:
    """Identify high-priority incidents that remain unassigned beyond the SLA window."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=stale_threshold_hours)

    stmt = select(Incident).where(
        Incident.status.in_([IncidentStatus.SUBMITTED, IncidentStatus.VERIFIED, IncidentStatus.PRIORITIZED]),
        Incident.created_at < cutoff,
    )
    result = await db.execute(stmt)
    stale_incidents = result.scalars().all()

    stale_codes: List[str] = []
    for inc in stale_incidents:
        stale_codes.append(inc.incident_code)
        # Automatically bump escalation note
        if not inc.description.startswith("[ESCALATED: STALE]"):
            inc.description = f"[ESCALATED: STALE] {inc.description}"
            logger.warning(f"Incident {inc.incident_code} marked STALE/ESCALATED (Unassigned > {stale_threshold_hours}h).")

    if stale_codes:
        await db.commit()

    return {
        "timestamp": now.isoformat(),
        "stale_incidents_count": len(stale_codes),
        "stale_incident_codes": stale_codes,
        "status": "COMPLETED",
    }


async def check_shelter_capacities(
    db: AsyncSession,
    overcrowd_threshold_pct: float = 90.0,
) -> Dict[str, Any]:
    """Scan cyclone shelters to identify those nearing or exceeding max capacity."""
    stmt = select(Shelter).where(Shelter.is_operational == True)
    result = await db.execute(stmt)
    shelters = result.scalars().all()

    overcrowded: List[Dict[str, Any]] = []
    for s in shelters:
        if s.capacity > 0:
            occ_pct = (s.current_occupancy / s.capacity) * 100.0
            if occ_pct >= overcrowd_threshold_pct:
                overcrowded.append({
                    "shelter_code": s.code,
                    "name": s.name,
                    "district": s.district_name,
                    "occupancy": s.current_occupancy,
                    "capacity": s.capacity,
                    "occupancy_pct": round(occ_pct, 1),
                })

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_operational_shelters": len(shelters),
        "overcrowded_shelters_count": len(overcrowded),
        "overcrowded_shelters": overcrowded,
        "status": "COMPLETED",
    }
