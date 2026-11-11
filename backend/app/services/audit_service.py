"""AapadaOps Immutable Audit Logging Service."""

import json
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog
from app.models.user import User


async def log_audit_event(
    db: AsyncSession,
    action: str,
    entity_type: str,
    entity_id: str,
    description: str,
    actor: Optional[User] = None,
    changes: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """Record an immutable compliance event to the audit trail."""
    changes_str = json.dumps(changes, default=str) if changes else None

    audit_entry = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor.id if actor else None,
        actor_role=str(actor.role) if actor else "SYSTEM",
        actor_name=actor.full_name if actor else "Automated System",
        ip_address=ip_address,
        changes_json=changes_str,
        description=description,
    )
    db.add(audit_entry)
    # Flushes so the audit entry is attached to the current transaction
    await db.flush()
    return audit_entry
