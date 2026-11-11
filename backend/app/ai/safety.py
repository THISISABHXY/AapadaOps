"""AapadaOps AI Safety Guardrails and Human Governance Enforcer.

Ensures that AI outputs remain strictly advisory and never trigger autonomous
dispatches, evacuations, incident closures, or automatic record merges.
"""

import logging
from typing import Any, Dict
from app.core.exceptions import AppException

logger = logging.getLogger("aapadaops.ai.safety")

# Operations that are strictly prohibited from autonomous AI execution
CRITICAL_SAFETY_ACTIONS = {
    "DISPATCH_RESPONSE_TEAM": "Dispatching tactical search and rescue teams (NDRF/ODRAF) requires authorized human signature.",
    "AUTHORIZE_ZONE_EVACUATION": "Ordering mandatory village or coastal evacuation requires District Magistrate / Collector sanction.",
    "CLOSE_INCIDENT": "Closing or marking a disaster incident resolved requires on-ground officer verification.",
    "AUTONOMOUS_INCIDENT_MERGE": "Merging disaster incident records permanently requires human verification to prevent data loss.",
    "DISMISS_ALERT": "Dismissing or downgrading a SATARK early warning alert requires meteorological officer approval.",
}


class AISafetyEnforcer:
    """Enforces safety policies prohibiting autonomous high-consequence decisions."""

    @classmethod
    def assert_action_permitted(cls, action_name: str, is_ai_invoked: bool = True):
        """Block any safety-critical action if initiated autonomously without human authorization."""
        if is_ai_invoked and action_name in CRITICAL_SAFETY_ACTIONS:
            reason = CRITICAL_SAFETY_ACTIONS[action_name]
            logger.warning("SAFETY VIOLATION PREVENTED: AI attempted blocked action '%s'.", action_name)
            raise AppException(
                message=f"Autonomous action blocked by AapadaOps safety policy: {reason}",
                status_code=403,
                code="AUTONOMOUS_ACTION_PROHIBITED",
            )

    @classmethod
    def wrap_advisory_payload(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Inject mandatory advisory flags into AI response envelopes."""
        payload["is_ai_advisory"] = True
        payload["requires_human_approval"] = True
        payload["governance_status"] = "ADVISORY_PENDING_HUMAN_REVIEW"
        return payload


safety_enforcer = AISafetyEnforcer()
