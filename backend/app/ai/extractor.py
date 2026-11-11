"""AapadaOps Information Extraction Engine.

Transforms unstructured multilingual (English & Odia) reports and voice transcripts
into rigorously validated Pydantic incident records with explicit missing-field tracking.
Never invents or hallucinates absent data.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple
import httpx
from app.ai.schemas import ExtractedIncidentRecord, ExtractionRequest
from app.core.config import settings
from app.models.incident import IncidentCategory

logger = logging.getLogger("aapadaops.ai.extractor")

# Standardized 30 Odisha Districts with phonetic aliases and Odia script names
ODISHA_DISTRICTS: Dict[str, List[str]] = {
    "Angul": ["angul", "anugul", "ଅନୁଗୋଳ"],
    "Balangir": ["balangir", "bolangir", "ବଲାଙ୍ଗୀର"],
    "Balasore": ["balasore", "baleswar", "ବାଲେଶ୍ୱର", "baleshwar"],
    "Bargarh": ["bargarh", "baragarh", "ବରଗଡ଼", "baragada"],
    "Bhadrak": ["bhadrak", "ଭଦ୍ରକ"],
    "Boudh": ["boudh", "bauda", "ବୌଦ୍ଧ"],
    "Cuttack": ["cuttack", "kataka", "କଟକ"],
    "Deogarh": ["deogarh", "debagarh", "ଦେବଗଡ଼"],
    "Dhenkanal": ["dhenkanal", "ଢେଙ୍କାନାଳ"],
    "Gajapati": ["gajapati", "ଗଜପତି", "paralakhemundi"],
    "Ganjam": ["ganjam", "ଗଞ୍ଜାମ", "berhampur", "chhatrapur"],
    "Jagatsinghpur": ["jagatsinghpur", "jagatsinghapur", "ଜଗତସିଂହପୁର", "paradeep"],
    "Jajpur": ["jajpur", "jajapur", "ଯାଜପୁର"],
    "Jharsuguda": ["jharsuguda", "ଝାରସୁଗୁଡ଼ା"],
    "Kalahandi": ["kalahandi", "କଳାହାଣ୍ଡି", "bhawanipatna"],
    "Kandhamal": ["kandhamal", "କନ୍ଧମାଳ", "phulbani"],
    "Kendrapara": ["kendrapara", "kendrapada", "କେନ୍ଦ୍ରାପଡ଼ା"],
    "Keonjhar": ["keonjhar", "kendujhar", "କେନ୍ଦୁଝର"],
    "Khordha": ["khordha", "khurda", "ଖୋର୍ଦ୍ଧା", "bhubaneswar", "jatni"],
    "Koraput": ["koraput", "କୋରାପୁଟ", "jeypore"],
    "Malkangiri": ["malkangiri", "ମାଲକାନଗିରି", "chitrakonda", "motu"],
    "Mayurbhanj": ["mayurbhanj", "ମୟୂରଭଞ୍ଜ", "baripada"],
    "Nabarangpur": ["nabarangpur", "nawarangpur", "ନବରଙ୍ଗପୁର"],
    "Nayagarh": ["nayagarh", "ନୟାଗଡ଼"],
    "Nuapada": ["nuapada", "ନୂଆପଡ଼ା"],
    "Puri": ["puri", "ପୁରୀ", "konark", "pipili"],
    "Rayagada": ["rayagada", "ରାୟଗଡ଼ା", "gunupur"],
    "Sambalpur": ["sambalpur", "ସମ୍ବଲପୁର", "burla", "hirakud"],
    "Subarnapur": ["subarnapur", "sonepur", "ସୁବର୍ଣ୍ଣପୁର"],
    "Sundargarh": ["sundargarh", "sundergarh", "ସୁନ୍ଦରଗଡ଼", "rourkela"],
}

# Domain Category Dictionaries
CATEGORY_KEYWORDS: Dict[IncidentCategory, List[str]] = {
    IncidentCategory.EMBANKMENT_BREACH: [
        "embankment breached", "embankment breach", "river embankment", "dyke broken", "dyke breached",
        "riverbank collapsed", "ghai", "bund breach", "breached", "breach", "embankment",
        "ବନ୍ଧ ଭାଙ୍ଗିଯାଇଛି", "ବନ୍ଧ ଭାଙ୍ଗିଲା", "ଘାଇ", "ନଦୀବନ୍ଧ", "ବାଲିବନ୍ଧ", "ବନ୍ଧ"
    ],
    IncidentCategory.TREE_FALL: [
        "tree fallen", "fallen tree", "uprooted tree", "tree fall", "blocked by tree",
        "banyan tree", "trees fell", "tree", "trees",
        "ଗଛ ପଡ଼ି", "ଗଛ ପଡିଯାଇଛି", "ଗଛ ଉପୁଡି ପଡିଛି", "ଗଛ", "ବୃକ୍ଷ", "ଡାଳ"
    ],
    IncidentCategory.FLOOD: [
        "flood water", "flash flood", "waterlogging", "submerged", "inundated", "river overflowing",
        "deluge", "water rising", "high tide", "water entered", "rainwater", "flood",
        "ବନ୍ୟା ପାଣି", "ଜଳମଗ୍ନ", "ବୁଡିଯାଇଛି", "ଉଛୁଳୁଛି", "ଜଳବନ୍ଦୀ", "ବନ୍ୟା", "ପାଣି"
    ],
    IncidentCategory.CYCLONE_WIND: [
        "cyclone", "gust", "storm", "gale", "cyclonic wind", "tornado", "squall", "high speed wind",
        "ବାତ୍ୟା", "ଝଡ", "ପବନ", "ପବନର ବେଗ", "ଝଡ଼ତୋଫାନ"
    ],
    IncidentCategory.STRANDED_PERSONS: [
        "stranded on roof", "trapped on roof", "marooned on roof", "villagers stranded", "people trapped",
        "need rescue", "cut off", "stranded", "marooned", "trapped", "rescue operation",
        "ଫସିରହିଛନ୍ତି", "ଆଶ୍ରୟ", "ଘେରି", "ଛାତ ଉପରେ", "ଲୋକେ ଫସିଛନ୍ତି", "ଉଦ୍ଧାର କରନ୍ତୁ"
    ],
    IncidentCategory.ROAD_BLOCK: [
        "road blocked", "highway shut", "culvert collapsed", "traffic cut off", "inaccessible",
        "bridge broken", "road washed away", "road block",
        "ରାସ୍ତା ଅବରୋଧ", "ଜାତୀୟ ରାଜପଥ", "ଯାତାୟତ ବନ୍ଦ", "ପୋଲ ଭାଙ୍ଗିଯାଇଛି", "ରାସ୍ତା", "ଅବରୋଧ"
    ],
    IncidentCategory.POWER_FAILURE: [
        "power cut", "blackout", "electric pole", "transformer damaged", "transformer burnt",
        "no electricity", "live wire hanging", "wires snapped",
        "ବିଦ୍ୟୁତ କଟିଛି", "ଟ୍ରାନ୍ସଫର୍ମର", "ଲାଇନ କଟିଛି", "ଅନ୍ଧାର", "ଖୁଣ୍ଟ ଭାଙ୍ଗିଛି", "ବିଦ୍ୟୁତ", "କରେଣ୍ଟ"
    ],
    IncidentCategory.SHELTER_DEMAND: [
        "shelter overcrowded", "no drinking water", "food packet", "dry ration", "baby food",
        "relief camp", "drinking water crisis",
        "ବାତ୍ୟା ଆଶ୍ରୟସ୍ଥଳ", "ଶେଲ୍ଟର", "ଖାଦ୍ୟ ନାହିଁ", "ପିଇବା ପାଣି ନାହିଁ", "ରିଲିଫ"
    ],
    IncidentCategory.MEDICAL_EMERGENCY: [
        "pregnant woman", "labor pain", "snake bite", "dialysis", "critical patient",
        "ambulance cannot reach", "casualty", "injury", "unconscious", "pregnant",
        "ଗର୍ଭବତୀ ମହିଳା", "ଡାକ୍ତରଖାନା", "ରୋଗୀ", "ଗର୍ଭବତୀ", "ଔଷଧ", "ଆହତ", "ସର୍ପାଘାତ", "ଆମ୍ବୁଲାନ୍ସ"
    ],
}

# Medical Need Indicators
MEDICAL_PATTERNS = {
    "PREGNANT_WOMAN_CARE": ["pregnant", "labor pain", "delivery", "ଗର୍ଭବତୀ", "ପ୍ରସବ"],
    "SNAKE_BITE_ANTIVENOM": ["snake bite", "serpent", "anti-venom", "ସର୍ପାଘାତ", "ସାପ କାମୁଡ଼ା"],
    "DIALYSIS_PATIENT": ["dialysis", "kidney patient", "ଡାଏଲିସିସ୍"],
    "TRAUMA_FIRST_AID": ["injury", "bleeding", "fracture", "stretcher", "ଆହତ", "ରକ୍ତସ୍ରାବ"],
    "OXYGEN_CRITICAL_CARE": ["oxygen", "ventilator", "asthma", "breathless", "ଶ୍ୱାସକଷ୍ଟ"],
}

# Resource Requirement Indicators
RESOURCE_PATTERNS = {
    "INFLATABLE_RESCUE_BOAT": ["boat", "inflatable boat", "odraf boat", "dinghy", "ଡଙ୍ଗା", "ବୋଟ୍"],
    "HIGH_CAPACITY_DEWATERING_PUMP": ["pump", "dewatering", "drainage pump", "ପମ୍ପ", "ଜଳ ନିଷ୍କାସନ"],
    "POWER_CHAINSAW_TREE_CUTTER": ["chainsaw", "tree cutter", "saw", "କରତ", "ଗଛ କଟା ମେସିନ"],
    "POTABLE_DRINKING_WATER_POUCHES": ["drinking water", "water pouches", "tanker", "ପିଇବା ପାଣି", "ଜଳ ଟ୍ୟାଙ୍କର"],
    "DRY_FOOD_RATIONS": ["food packets", "dry ration", "chuda", "biscuit", "ଖାଦ୍ୟ ପ୍ୟାକେଟ", "ଚୁଡ଼ା"],
    "EMERGENCY_POWER_GENERATOR": ["generator", "dg set", "genset", "lighting tower", "ଜେନେରେଟର"],
    "TEMPORARY_TARPAULIN_SHEETS": ["tarpaulin", "plastic sheet", "polythene", "ତାରପୋଲିନ", "ପଲିଥିନ"],
}


class InformationExtractionEngine:
    """Extracts structured disaster incidents with verified missing-field awareness."""

    @staticmethod
    def detect_language(text: str) -> str:
        """Identify if text uses Odia script (U+0B00 to U+0B7F) or Latin."""
        odia_chars = len(re.findall(r"[\u0b00-\u0b7f]", text))
        return "or" if odia_chars >= 3 else "en"

    @staticmethod
    def extract_district(text: str) -> Optional[str]:
        """Match mention of any of the 30 Odisha districts."""
        text_lower = text.lower()
        for district, aliases in ODISHA_DISTRICTS.items():
            for alias in aliases:
                # Use word boundary or simple token match
                if re.search(r"\b" + re.escape(alias) + r"\b", text_lower) or alias in text:
                    return district
        return None

    @staticmethod
    def extract_location(text: str, district: Optional[str]) -> Optional[str]:
        """Extract village, block, or landmark location mention."""
        # Common non-location nouns to reject
        excluded_words = {
            "tree", "trees", "water", "flood", "river", "road", "path", "house", "houses",
            "school", "somewhere", "anywhere", "danger", "hospital", "terrace", "roof",
            "village", "block", "district", "relief", "food", "cyclone", "storm"
        }

        patterns = [
            r"\b(?:at|near|in|village|gp|block)\s+([A-Z\u0b00-\u0b7f][A-Za-z\u0b00-\u0b7f]{2,25}(?:\s+[A-Z\u0b00-\u0b7f][A-Za-z\u0b00-\u0b7f]{2,20})?)",
            r"\b([A-Z\u0b00-\u0b7f][A-Za-z\u0b00-\u0b7f]{2,20})\s+(?:village|gp|gram panchayat|block|bazar|chhak)\b",
            r"([A-Za-z\u0b00-\u0b7f]{3,20})\s+(?:ଗ୍ରାମ|ବ୍ଲକ|ଛକ|ନଦୀ)",
        ]
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                loc = match.group(1).strip()
                # Skip if matched token is just the district name or generic word
                if district and loc.lower() == district.lower():
                    continue
                if loc.lower() in excluded_words:
                    continue
                if len(loc) >= 3:
                    return loc
        return None

    @classmethod
    def extract_category(cls, text: str) -> Tuple[IncidentCategory, float]:
        """Identify disaster incident category with confidence score."""
        text_lower = text.lower()
        scores: Dict[IncidentCategory, int] = {cat: 0 for cat in IncidentCategory}

        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower or kw in text:
                    # Longer/multi-word phrases carry more specificity
                    weight = 4 if (" " in kw or len(kw) > 7) else 2
                    scores[cat] += weight

        # Domain hierarchy resolution:
        # 1. Structural embankment breach is the root physical cause over downstream flood
        if scores[IncidentCategory.EMBANKMENT_BREACH] >= 4:
            scores[IncidentCategory.EMBANKMENT_BREACH] += 6

        # 2. Critical medical emergency (labor, snakebite, unconscious) takes life-priority
        if scores[IncidentCategory.MEDICAL_EMERGENCY] >= 4:
            scores[IncidentCategory.MEDICAL_EMERGENCY] += 6

        # 3. Tree fall is the root cause when a tree blocks roads
        if scores[IncidentCategory.TREE_FALL] >= 4 and scores[IncidentCategory.ROAD_BLOCK] > 0:
            scores[IncidentCategory.TREE_FALL] += 5

        best_cat = max(scores, key=scores.get)
        max_score = scores[best_cat]

        if max_score == 0:
            return IncidentCategory.OTHER, 0.40

        confidence = min(0.96, 0.60 + (max_score * 0.04))
        return best_cat, round(confidence, 2)

    @staticmethod
    def extract_numbers(text: str) -> Tuple[Optional[int], int]:
        """Extract number of people affected/stranded and casualties.
        Returns (people_affected, casualties). If people_affected not mentioned, returns (None, casualties).
        """
        people_affected: Optional[int] = None
        casualties: int = 0

        # Odia numeral mapping
        odia_digits = str.maketrans("୦୧୨୩୪୫୬୭୮୯", "0123456789")
        normalized_text = text.translate(odia_digits)

        # Match stranded / affected count
        affected_match = re.search(
            r"(\d+)\s*(?:people|persons|villagers|families|citizens|residents|children|individuals)?\s*(?:stranded|marooned|trapped|affected|in danger|submerged|homeless|ଫସିଛନ୍ତି|ଜଣ)",
            normalized_text,
            re.IGNORECASE,
        )
        if affected_match:
            people_affected = int(affected_match.group(1))
        else:
            # Check standalone count patterns like "around 40 families"
            alt_match = re.search(r"(?:around|about|over|nearly)?\s*(\d+)\s*(?:families|houses|villagers)", normalized_text, re.IGNORECASE)
            if alt_match:
                people_affected = int(alt_match.group(1))

        # Match casualties / dead / injured
        casualty_match = re.search(
            r"(\d+)\s*(?:dead|deaths|fatalities|casualties|injured|ମୃତ|ଆହତ)",
            normalized_text,
            re.IGNORECASE,
        )
        if casualty_match:
            casualties = int(casualty_match.group(1))

        return people_affected, casualties

    @staticmethod
    def extract_medical_needs(text: str) -> List[str]:
        """Extract explicit medical needs."""
        needs = []
        text_lower = text.lower()
        for need_tag, keywords in MEDICAL_PATTERNS.items():
            if any(kw in text_lower or kw in text for kw in keywords):
                needs.append(need_tag)
        return needs

    @staticmethod
    def extract_resource_requirements(text: str, category: IncidentCategory) -> List[str]:
        """Extract explicit or strongly implied emergency resources."""
        resources = []
        text_lower = text.lower()
        for res_tag, keywords in RESOURCE_PATTERNS.items():
            if any(kw in text_lower or kw in text for kw in keywords):
                resources.append(res_tag)

        # Category-based default recommendations if explicitly absent
        if not resources:
            if category in (IncidentCategory.FLOOD, IncidentCategory.STRANDED_PERSONS):
                resources.append("INFLATABLE_RESCUE_BOAT")
            elif category == IncidentCategory.TREE_FALL:
                resources.append("POWER_CHAINSAW_TREE_CUTTER")
            elif category == IncidentCategory.EMBANKMENT_BREACH:
                resources.append("SANDBAGS_AND_GEOTEXTILE_FILTER")

        return resources

    @staticmethod
    def extract_severity_indicators(text: str, category: IncidentCategory, casualties: int) -> List[str]:
        """Identify observable severity indicators."""
        indicators = []
        text_lower = text.lower()

        if casualties > 0:
            indicators.append("CONFIRMED_CASUALTIES")
        if any(w in text_lower or w in text for w in ["roof", "terrace", "ଛାତ ଉପରେ"]):
            indicators.append("RISING_WATER_FORCING_VERTICAL_EVACUATION")
        if any(w in text_lower or w in text for w in ["breach", "broken", "ଘାଇ", "ଭାଙ୍ଗିଯାଇଛି"]):
            indicators.append("EMBANKMENT_STRUCTURAL_FAILURE")
        if any(w in text_lower or w in text for w in ["fast rising", "sudden rise", "ଦ୍ରୁତ ଜଳବୃଦ୍ଧି"]):
            indicators.append("RAPID_FLASH_INUNDATION")
        if any(w in text_lower or w in text for w in ["cut off", "isolated", "no road", "ବିଚ୍ଛିନ୍ନ"]):
            indicators.append("TERRESTRIAL_ACCESS_SEVERED")
        if any(w in text_lower or w in text for w in ["pregnant", "dialysis", "infant", "baby", "ଗର୍ଭବତୀ"]):
            indicators.append("VULNERABLE_POPULATION_AT_RISK")

        return indicators

    @classmethod
    async def extract_structured_incident(cls, request: ExtractionRequest) -> ExtractedIncidentRecord:
        """Full extraction pipeline converting unstructured input to strict validated record."""
        text = request.text.strip()
        lang = request.language_hint or cls.detect_language(text)

        # Deterministic feature extraction
        category, confidence = cls.extract_category(text)
        district = cls.extract_district(text)
        location = cls.extract_location(text, district)
        people_affected, casualties = cls.extract_numbers(text)
        medical_needs = cls.extract_medical_needs(text)
        resource_requirements = cls.extract_resource_requirements(text, category)
        severity_indicators = cls.extract_severity_indicators(text, category, casualties)

        # Catalogue missing fields strictly
        missing_fields: List[str] = []
        if not district:
            missing_fields.append("district")
        if not location:
            missing_fields.append("location")
        if people_affected is None:
            missing_fields.append("people_affected")
        if not medical_needs:
            missing_fields.append("medical_needs")
        if not severity_indicators:
            missing_fields.append("severity_indicators")

        # Adjust confidence based on completeness
        penalty = len(missing_fields) * 0.05
        final_confidence = max(0.40, min(0.95, confidence - penalty))

        record = ExtractedIncidentRecord(
            incident_category=category,
            location=location,
            district=district,
            description=text,
            severity_indicators=severity_indicators,
            people_affected=people_affected,
            medical_needs=medical_needs,
            resource_requirements=resource_requirements,
            timestamp=request.recorded_at or datetime.now(timezone.utc),
            source=request.source,
            confidence=round(final_confidence, 2),
            missing_fields=missing_fields,
            detected_language=lang,
            is_advisory=True,
            requires_human_verification=True,
        )

        return record


extraction_engine = InformationExtractionEngine()
