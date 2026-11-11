"""AapadaOps Multi-Factor Operational Prioritization Engine."""

from typing import Tuple
from app.models.incident import IncidentCategory, IncidentSeverity


class PrioritizationEngine:
    """Calculates objective response priority scores (0 to 100) based on vulnerability and impact."""

    @staticmethod
    def calculate_priority(
        category: IncidentCategory,
        severity: IncidentSeverity,
        stranded_count: int,
        casualties: int,
        district_vulnerability_tier: int = 3,
        is_coastal_block: bool = False,
    ) -> Tuple[IncidentSeverity, float]:
        """Compute composite priority score and mapped severity level."""
        # 1. Base Severity Weight (Max 40)
        base_weights = {
            IncidentSeverity.CRITICAL: 40.0,
            IncidentSeverity.HIGH: 28.0,
            IncidentSeverity.MEDIUM: 16.0,
            IncidentSeverity.LOW: 8.0,
        }
        score = base_weights.get(severity, 16.0)

        # 2. Human Life Impact (Max 30)
        if casualties > 0:
            score += 25.0
        score += min(20.0, stranded_count * 1.5)

        # 3. Category Urgency Multiplier (Max 15)
        category_boost = {
            IncidentCategory.EMBANKMENT_BREACH: 15.0,
            IncidentCategory.MEDICAL_EMERGENCY: 14.0,
            IncidentCategory.STRANDED_PERSONS: 12.0,
            IncidentCategory.FLOOD: 10.0,
            IncidentCategory.CYCLONE_WIND: 8.0,
            IncidentCategory.SHELTER_DEMAND: 8.0,
            IncidentCategory.ROAD_BLOCK: 5.0,
            IncidentCategory.POWER_FAILURE: 4.0,
            IncidentCategory.TREE_FALL: 3.0,
            IncidentCategory.OTHER: 2.0,
        }
        score += category_boost.get(category, 5.0)

        # 4. District Vulnerability & Geography (Max 15)
        score += district_vulnerability_tier * 2.0
        if is_coastal_block:
            score += 5.0

        # Cap score at 100.0
        final_score = min(100.0, round(score, 1))

        # Map to final verified priority enum
        if final_score >= 70.0:
            mapped_priority = IncidentSeverity.CRITICAL
        elif final_score >= 50.0:
            mapped_priority = IncidentSeverity.HIGH
        elif final_score >= 30.0:
            mapped_priority = IncidentSeverity.MEDIUM
        else:
            mapped_priority = IncidentSeverity.LOW

        return mapped_priority, final_score


prioritization_engine = PrioritizationEngine()
