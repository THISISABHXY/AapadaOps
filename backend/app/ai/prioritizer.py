"""AapadaOps Explainable Prioritization Engine.

Deterministic, multi-factor operational urgency scoring framework (0 to 100)
aligned with OSDMA Standard Operating Procedures.
Outputs itemized factor breakdown and plain-language justification for every decision.
"""

from typing import List, Tuple
from app.ai.schemas import (
    PrioritizationFactor,
    PrioritizationRequest,
    PrioritizationResponse,
)
from app.models.incident import IncidentCategory, IncidentSeverity


class ExplainablePrioritizationEngine:
    """Calculates objective response priorities with full factor transparency."""

    @classmethod
    def evaluate(cls, req: PrioritizationRequest) -> PrioritizationResponse:
        """Execute deterministic multi-factor evaluation."""
        factors: List[PrioritizationFactor] = []

        # -------------------------------------------------------------
        # Factor 1: Threat to Human Life (Max 35.0 pts)
        # -------------------------------------------------------------
        life_points = 0.0
        life_reasons = []

        if req.casualties > 0:
            life_points += 25.0
            life_reasons.append(f"{req.casualties} confirmed casualties or critical injuries")

        if req.category == IncidentCategory.EMBANKMENT_BREACH:
            life_points += 10.0
            life_reasons.append("Active river embankment breach posing rapid inundation risk")
        elif req.category in (IncidentCategory.FLOOD, IncidentCategory.STRANDED_PERSONS):
            if req.stranded_count >= 10:
                life_points += 10.0
                life_reasons.append(f"{req.stranded_count} individuals marooned in active flood zone")
            else:
                life_points += 6.0
                life_reasons.append("Active flood water surrounding residential structures")
        elif req.category == IncidentCategory.CYCLONE_WIND:
            life_points += 7.0
            life_reasons.append("High-velocity cyclonic gales posing flying debris hazard")
        else:
            life_points += 2.0
            life_reasons.append(f"Non-life-threatening infrastructure event ({req.category.value})")

        life_points = min(35.0, round(life_points, 1))
        factors.append(
            PrioritizationFactor(
                factor_name="THREAT_TO_HUMAN_LIFE",
                points_awarded=life_points,
                max_points=35.0,
                reason="; ".join(life_reasons),
            )
        )

        # -------------------------------------------------------------
        # Factor 2: Medical Urgency (Max 20.0 pts)
        # -------------------------------------------------------------
        med_points = 0.0
        med_reasons = []

        critical_med_tags = {"PREGNANT_WOMAN_CARE", "SNAKE_BITE_ANTIVENOM", "DIALYSIS_PATIENT", "OXYGEN_CRITICAL_CARE"}
        has_critical_med = any(tag in critical_med_tags for tag in req.medical_needs)

        if has_critical_med:
            med_points += 20.0
            med_reasons.append(
                f"Life-critical medical emergencies identified: {', '.join(req.medical_needs)}"
            )
        elif req.medical_needs:
            med_points += 12.0
            med_reasons.append(f"Urgent medical support required: {', '.join(req.medical_needs)}")
        else:
            med_points += 0.0
            med_reasons.append("No immediate medical intervention requested")

        med_points = min(20.0, round(med_points, 1))
        factors.append(
            PrioritizationFactor(
                factor_name="MEDICAL_URGENCY",
                points_awarded=med_points,
                max_points=20.0,
                reason="; ".join(med_reasons),
            )
        )

        # -------------------------------------------------------------
        # Factor 3: People Affected Scale (Max 15.0 pts)
        # -------------------------------------------------------------
        scale_points = 0.0
        scale_reason = ""
        count = max(req.stranded_count, 0)

        if count >= 100:
            scale_points = 15.0
            scale_reason = f"Mass population impact ({count} individuals affected)"
        elif count >= 50:
            scale_points = 12.0
            scale_reason = f"Large community impact ({count} individuals affected)"
        elif count >= 20:
            scale_points = 9.0
            scale_reason = f"Significant group affected ({count} individuals)"
        elif count >= 5:
            scale_points = 6.0
            scale_reason = f"Small group affected ({count} individuals)"
        elif count >= 1:
            scale_points = 3.0
            scale_reason = f"Individual household affected ({count} person)"
        else:
            scale_points = 1.0
            scale_reason = "Affected population count unverified / not stated"

        factors.append(
            PrioritizationFactor(
                factor_name="PEOPLE_AFFECTED_SCALE",
                points_awarded=scale_points,
                max_points=15.0,
                reason=scale_reason,
            )
        )

        # -------------------------------------------------------------
        # Factor 4: Accessibility / Isolation (Max 10.0 pts)
        # -------------------------------------------------------------
        access_points = 0.0
        access_reason = ""

        if req.access_cut_off:
            access_points = 10.0
            access_reason = "Terrestrial access severed; village completely marooned by water or washed-out bridge"
        elif req.is_coastal_block:
            access_points = 6.0
            access_reason = "Vulnerable low-lying coastal block with tidal ingress risks"
        else:
            access_points = 2.0
            access_reason = "Standard road access remains passable"

        factors.append(
            PrioritizationFactor(
                factor_name="ACCESSIBILITY_AND_ISOLATION",
                points_awarded=access_points,
                max_points=10.0,
                reason=access_reason,
            )
        )

        # -------------------------------------------------------------
        # Factor 5: Resource Complexity (Max 10.0 pts)
        # -------------------------------------------------------------
        res_points = 0.0
        res_reason = ""

        if req.category in (IncidentCategory.EMBANKMENT_BREACH, IncidentCategory.STRANDED_PERSONS):
            res_points = 10.0
            res_reason = "Requires tactical motorized boats, dive teams (ODRAF/NDRF), and flood rescue equipment"
        elif req.category in (IncidentCategory.TREE_FALL, IncidentCategory.ROAD_BLOCK):
            res_points = 6.0
            res_reason = "Requires hydraulic tree cutters, cranes, and heavy road clearance machinery"
        elif req.category == IncidentCategory.POWER_FAILURE:
            res_points = 5.0
            res_reason = "Requires electric DISCOM lineman crews and transformer repair"
        else:
            res_points = 3.0
            res_reason = "Requires standard municipal or civil supply dispatch"

        factors.append(
            PrioritizationFactor(
                factor_name="RESOURCE_COMPLEXITY",
                points_awarded=res_points,
                max_points=10.0,
                reason=res_reason,
            )
        )

        # -------------------------------------------------------------
        # Factor 6: Report Freshness (Max 5.0 pts)
        # -------------------------------------------------------------
        fresh_points = 0.0
        fresh_reason = ""

        if req.report_freshness_hours <= 1.0:
            fresh_points = 5.0
            fresh_reason = f"Fresh report ({round(req.report_freshness_hours, 1)}h old); active unfolding emergency"
        elif req.report_freshness_hours <= 6.0:
            fresh_points = 4.0
            fresh_reason = f"Recent report ({round(req.report_freshness_hours, 1)}h old); steady degradation risk"
        elif req.report_freshness_hours <= 24.0:
            fresh_points = 2.0
            fresh_reason = f"Ongoing situation ({round(req.report_freshness_hours, 1)}h old)"
        else:
            fresh_points = 1.0
            fresh_reason = f"Stale incident ({round(req.report_freshness_hours, 1)}h old); field re-verification recommended"

        factors.append(
            PrioritizationFactor(
                factor_name="REPORT_FRESHNESS",
                points_awarded=fresh_points,
                max_points=5.0,
                reason=fresh_reason,
            )
        )

        # -------------------------------------------------------------
        # Factor 7: Verification Status (Max 5.0 pts)
        # -------------------------------------------------------------
        verif_points = 5.0 if req.is_verified else 2.0
        verif_reason = (
            "Officially verified by field officer / drone reconnaissance"
            if req.is_verified
            else "Unverified citizen report; prioritized with verification contingency"
        )

        factors.append(
            PrioritizationFactor(
                factor_name="VERIFICATION_STATUS",
                points_awarded=verif_points,
                max_points=5.0,
                reason=verif_reason,
            )
        )

        # -------------------------------------------------------------
        # Composite Score & SLA Mapping
        # -------------------------------------------------------------
        composite = sum(f.points_awarded for f in factors)
        composite = min(100.0, max(0.0, round(composite, 1)))

        if composite >= 75.0:
            priority_level = IncidentSeverity.CRITICAL
            sla_hours = 2
            summary_tier = "CRITICAL PRIORITY (Immediate Life Threat)"
        elif composite >= 50.0:
            priority_level = IncidentSeverity.HIGH
            sla_hours = 6
            summary_tier = "HIGH PRIORITY (Urgent Rescue / Severe Impact)"
        elif composite >= 25.0:
            priority_level = IncidentSeverity.MEDIUM
            sla_hours = 12
            summary_tier = "MEDIUM PRIORITY (Infrastructure Disruption)"
        else:
            priority_level = IncidentSeverity.LOW
            sla_hours = 24
            summary_tier = "LOW PRIORITY (Routine Maintenance / Non-critical)"

        plain_summary = (
            f"Evaluated as {summary_tier} with composite urgency score of {composite}/100. "
            f"Recommended SLA: dispatch within {sla_hours} hours. "
            f"Primary driver: {factors[0].reason}."
        )

        return PrioritizationResponse(
            composite_score=composite,
            priority_level=priority_level,
            factors=factors,
            plain_language_summary=plain_summary,
            recommended_sla_hours=sla_hours,
            is_deterministic=True,
            is_advisory=True,
        )


prioritizer_engine = ExplainablePrioritizationEngine()
