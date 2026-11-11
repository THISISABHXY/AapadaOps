"""AapadaOps AI Advisory and Bilingual Natural Language Parser."""

import re
from typing import Dict, Tuple
from app.models.incident import IncidentCategory, IncidentSeverity


# Specialized Odisha Disaster Vocabularies
ODIA_KEYWORD_MAP: Dict[IncidentCategory, list] = {
    IncidentCategory.FLOOD: ["ବନ୍ୟା", "ପାଣି", "ଜଳମଗ୍ନ", "ବୁଡିଯାଇଛି", "ନଦୀ", "ଉଛୁଳୁଛି"],
    IncidentCategory.CYCLONE_WIND: ["ବାତ୍ୟା", "ଝଡ", "ପବନ", "ପବନର ବେଗ", "ଝଡ଼ତୋଫାନ"],
    IncidentCategory.TREE_FALL: ["ଗଛ", "ବୃକ୍ଷ", "ଡାଳ", "ଗଛ ପଡିଯାଇଛି"],
    IncidentCategory.ROAD_BLOCK: ["ରାସ୍ତା", "ଜାତୀୟ ରାଜପଥ", "ଯାତାୟତ", "ବନ୍ଦ", "ଅବରୋଧ"],
    IncidentCategory.EMBANKMENT_BREACH: ["ବନ୍ଧ", "ଘାଇ", "ନଦୀବନ୍ଧ", "ଭାଙ୍ଗିଯାଇଛି", "ବାଲିବନ୍ଧ"],
    IncidentCategory.STRANDED_PERSONS: ["ଫସିରହିଛନ୍ତି", "ଆଶ୍ରୟ", "ଘେରି", "ଛାତ ଉପରେ", "ଲୋକେ ଫସିଛନ୍ତି"],
    IncidentCategory.POWER_FAILURE: ["ବିଦ୍ୟୁତ", "କରେଣ୍ଟ", "ଟ୍ରାନ୍ସଫର୍ମର", "ଲାଇନ କଟିଛି", "ଅନ୍ଧାର"],
    IncidentCategory.SHELTER_DEMAND: ["ବାତ୍ୟା ଆଶ୍ରୟସ୍ଥଳ", "ଶେଲ୍ଟର", "ଖାଦ୍ୟ ନାହିଁ", "ପିଇବା ପାଣି ନାହିଁ"],
    IncidentCategory.MEDICAL_EMERGENCY: ["ଡାକ୍ତରଖାନା", "ରୋଗୀ", "ଗର୍ଭବତୀ", "ଔଷଧ", "ଆହତ"],
}

ENGLISH_KEYWORD_MAP: Dict[IncidentCategory, list] = {
    IncidentCategory.FLOOD: ["flood", "waterlogging", "submerged", "inundated", "river overflowing", "deluge"],
    IncidentCategory.CYCLONE_WIND: ["cyclone", "gust", "storm", "gale", "cyclonic wind", "tornado"],
    IncidentCategory.TREE_FALL: ["tree fallen", "uprooted tree", "branch", "blocked by tree"],
    IncidentCategory.ROAD_BLOCK: ["road blocked", "highway shut", "culvert collapsed", "traffic cut off", "inaccessible"],
    IncidentCategory.EMBANKMENT_BREACH: ["breach", "embankment", "dyke broken", "riverbank collapsed", "ghai"],
    IncidentCategory.STRANDED_PERSONS: ["stranded", "marooned", "trapped on roof", "surrounded by water", "need rescue"],
    IncidentCategory.POWER_FAILURE: ["power cut", "blackout", "electric pole", "transformer damaged", "no electricity"],
    IncidentCategory.SHELTER_DEMAND: ["shelter overcrowded", "no drinking water", "food packet", "dry ration", "baby food"],
    IncidentCategory.MEDICAL_EMERGENCY: ["pregnant", "dialysis", "critical patient", "ambulance cannot reach", "casualty", "injury"],
}


class AIAdvisoryEngine:
    """Analyzes unstructured citizen and field reports into structured operational metadata."""

    @staticmethod
    def detect_language(text: str) -> str:
        """Detect whether text is predominantly Odia script or Latin/English."""
        # Odia Unicode block: U+0B00 to U+0B7F
        odia_chars = len(re.findall(r"[\u0b00-\u0b7f]", text))
        return "or" if odia_chars > 3 else "en"

    @classmethod
    def classify_category(cls, text: str) -> Tuple[IncidentCategory, float]:
        """Classify incident disaster category with confidence metric."""
        text_lower = text.lower()
        scores: Dict[IncidentCategory, int] = {cat: 0 for cat in IncidentCategory}

        # Match English terms
        for cat, keywords in ENGLISH_KEYWORD_MAP.items():
            for kw in keywords:
                if kw in text_lower:
                    scores[cat] += 2

        # Match Odia terms
        for cat, keywords in ODIA_KEYWORD_MAP.items():
            for kw in keywords:
                if kw in text:
                    scores[cat] += 3

        best_cat = max(scores, key=scores.get)
        max_score = scores[best_cat]

        if max_score == 0:
            return IncidentCategory.OTHER, 0.45

        # Normalize confidence between 0.65 and 0.95
        confidence = min(0.95, 0.65 + (max_score * 0.05))
        return best_cat, round(confidence, 2)

    @staticmethod
    def extract_counts(text: str) -> Tuple[int, int]:
        """Extract estimated stranded people and casualties using regex heuristics."""
        stranded_count = 0
        casualties_count = 0

        # Extract patterns like "15 people stranded", "40 villagers trapped", "୨୫ ଜଣ ଫସିଛନ୍ତି"
        stranded_match = re.search(r"(\d+)\s*(?:people|persons|villagers|families|citizens)?\s*(?:stranded|trapped|marooned)", text, re.IGNORECASE)
        if stranded_match:
            stranded_count = int(stranded_match.group(1))

        # Extract casualties or injuries
        casualty_match = re.search(r"(\d+)\s*(?:injured|casualties|dead|deaths)", text, re.IGNORECASE)
        if casualty_match:
            casualties_count = int(casualty_match.group(1))

        return stranded_count, casualties_count

    @classmethod
    def evaluate_severity(
        cls,
        category: IncidentCategory,
        text: str,
        stranded_count: int,
        casualties: int,
    ) -> Tuple[IncidentSeverity, float]:
        """Determine severity and urgency index (0.0 to 1.0)."""
        text_lower = text.lower()

        # Critical triggers
        critical_keywords = [
            "immediate rescue", "life threatening", "drowning", "pregnant woman",
            "medical emergency", "dyke breach", "completely inundated", "ଭାଙ୍ଗିଯାଇଛି", "ଜୀବନ ପ୍ରତି ବିପଦ"
        ]
        has_critical_words = any(kw in text_lower for kw in critical_keywords)

        if casualties > 0 or stranded_count >= 20 or category == IncidentCategory.EMBANKMENT_BREACH or has_critical_words:
            urgency = min(0.98, 0.80 + (stranded_count * 0.01))
            return IncidentSeverity.CRITICAL, round(urgency, 2)

        if stranded_count > 0 or category in (IncidentCategory.FLOOD, IncidentCategory.MEDICAL_EMERGENCY, IncidentCategory.CYCLONE_WIND):
            return IncidentSeverity.HIGH, 0.72

        if category in (IncidentCategory.ROAD_BLOCK, IncidentCategory.TREE_FALL, IncidentCategory.POWER_FAILURE):
            return IncidentSeverity.MEDIUM, 0.50

        return IncidentSeverity.LOW, 0.30

    @classmethod
    def analyze_report(cls, text: str) -> dict:
        """Full automated pipeline returning AI advisory envelope."""
        lang = cls.detect_language(text)
        category, confidence = cls.classify_category(text)
        stranded_count, casualties = cls.extract_counts(text)
        severity, urgency = cls.evaluate_severity(category, text, stranded_count, casualties)

        return {
            "detected_language": lang,
            "suggested_category": category,
            "suggested_severity": severity,
            "confidence_score": confidence,
            "urgency_score": urgency,
            "extracted_stranded_count": stranded_count,
            "extracted_casualties": casualties,
            "ai_advisory_statement": (
                f"AI Advisory: Automated assessment classified as '{category.value}' with {severity.value} urgency "
                f"({int(confidence * 100)}% confidence). Human verification required."
            ),
            "is_ai_generated": True,
        }


ai_engine = AIAdvisoryEngine()
