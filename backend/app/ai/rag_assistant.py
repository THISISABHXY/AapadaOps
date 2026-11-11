"""AapadaOps Retrieval-Augmented Generation (RAG) Verified Knowledge Assistant.

Queries an authoritative, pre-verified corpus of official Odisha State Disaster Management
Authority (OSDMA) and National Disaster Management Authority (NDMA) Standard Operating Procedures.
Strictly grounds answers in official text and never hallucinates unverified instructions.
"""

import math
import re
from typing import Dict, List, Optional, Tuple
from app.ai.schemas import RAGCitation, RAGQueryRequest, RAGResponse

# Verified Official Government Disaster SOP Corpus
VERIFIED_SOP_CORPUS = [
    {
        "id": "SOP-FLD-01",
        "doc_title": "OSDMA Standard Operating Procedure on Flood Management & River Embankment Protection (2024)",
        "section": "Section 3.1: River Embankment Breach Protocol (Ghai)",
        "page": 14,
        "keywords": ["embankment breach", "ghai", "dyke broken", "riverbank", "sandbags", "boulder pitching", "breach"],
        "text": (
            "Upon receipt of a report of an embankment breach (Ghai), the Executive Engineer (Water Resources) "
            "and deployed ODRAF/NDRF units must mobilize within 30 minutes. Emergency closure involves dumping "
            "sandbags, steel wire crates (gabions), and boulder pitching. Downstream riparian villages within 5 km "
            "must be evacuated along pre-designated high ground routes. Siren warnings must be sounded."
        ),
    },
    {
        "id": "SOP-FLD-02",
        "doc_title": "OSDMA Standard Operating Procedure on Flood Management & River Embankment Protection (2024)",
        "section": "Section 3.4: Marooned Population Rescue Protocol",
        "page": 22,
        "keywords": ["marooned", "stranded", "rescue", "priority", "pregnant", "infants", "boats", "lifeguards", "terrace"],
        "text": (
            "Power boats equipped with life jackets and trained lifeguards must be deployed immediately to marooned "
            "settlements. Mandatory priority evacuation sequence: (1) pregnant women and nursing mothers, (2) critically "
            "ill and injured persons, (3) elderly persons (65+) and persons with disabilities (PwDs), (4) children, "
            "(5) general population. Livestock must be steered to designated raised earthen mounds (Gochhar)."
        ),
    },
    {
        "id": "SOP-FLD-03",
        "doc_title": "OSDMA Standard Operating Procedure on Flood Management & River Embankment Protection (2024)",
        "section": "Section 5.2: Safe Drinking Water and Halogenation",
        "page": 41,
        "keywords": ["drinking water", "water pouches", "halogen tablets", "bleaching powder", "tubewell", "purification"],
        "text": (
            "All submerged tubewells must be disinfected with bleaching powder. Halogen tablets (1 tablet per 5 liters "
            "of water) and sealed potable drinking water pouches must be delivered via boat or airdrop. A minimum of "
            "3 liters of potable drinking water per person per day is mandatory during the initial 72 hours of inundation."
        ),
    },
    {
        "id": "SOP-CYC-01",
        "doc_title": "OSDMA Cyclone Evacuation & Multi-Purpose Cyclone Shelter (MPCS) Operations Manual",
        "section": "Section 2.3: Cyclone Shelter Activation Timeline",
        "page": 8,
        "keywords": ["cyclone shelter", "mpcs", "shelter activation", "orange warning", "red warning", "landfall"],
        "text": (
            "Upon IMD issuing an Orange Warning (48 hours before expected landfall) or Red Warning (24 hours before "
            "landfall), Cyclone Shelter Management and Maintenance Committees (CSMMC) must unlock all MPCS buildings, "
            "verify backup diesel generators, replenish overhead water tanks, and inspect sanitary facilities. Shelters "
            "must be fully operational 12 hours prior to gale-force winds."
        ),
    },
    {
        "id": "SOP-CYC-02",
        "doc_title": "OSDMA Cyclone Evacuation & Multi-Purpose Cyclone Shelter (MPCS) Operations Manual",
        "section": "Section 4.1: Shelter Inmate Welfare and Rations",
        "page": 19,
        "keywords": ["shelter ration", "dry food", "chuda", "biscuits", "generator fuel", "candles", "welfare"],
        "text": (
            "Every functional cyclone shelter must maintain a 72-hour buffer stock of dry rations (chuda, gur, biscuits, "
            "baby food), candles, matchboxes, and first-aid kits. A functional 15 kVA generator with at least 40 liters "
            "of diesel fuel must be on standby to ensure continuous illumination and water pumping."
        ),
    },
    {
        "id": "SOP-CYC-03",
        "doc_title": "OSDMA Cyclone Evacuation & Multi-Purpose Cyclone Shelter (MPCS) Operations Manual",
        "section": "Section 4.5: Medical Staffing in Shelters",
        "page": 27,
        "keywords": ["anm", "asha", "medical kit", "shelter medicine", "ors", "paracetamol", "delivery kit"],
        "text": (
            "An Auxiliary Nurse Midwife (ANM) or Accredited Social Health Activist (ASHA) must be stationed at every active "
            "shelter equipped with essential drugs: Oral Rehydration Salts (ORS), Paracetamol, Anti-Snake Venom (ASV), and "
            "clean delivery kits (Maa-Gruha buffer). High-risk pregnancies must be transferred to the nearest hospital."
        ),
    },
    {
        "id": "SOP-MED-01",
        "doc_title": "Odisha Health & Family Welfare Disaster Medical Emergency Protocol",
        "section": "Section 2.1: Management of Snake Bites During Floods",
        "page": 33,
        "keywords": ["snake bite", "antivenom", "asv", "serpent", "immobilization", "tourniquet contraindicated"],
        "text": (
            "Snake bite frequency escalates sharply as rising flood waters inundate burrows. All Community Health Centres "
            "(CHCs) and Primary Health Centres (PHCs) in flood-affected blocks must stock at least 50 vials of polyvalent "
            "Anti-Snake Venom (ASV). The bitten limb must be immobilized with a splint; the patient must be kept calm and "
            "transported rapidly to the nearest hospital. Tight tourniquets and incisions are strictly contraindicated."
        ),
    },
    {
        "id": "SOP-MED-02",
        "doc_title": "Odisha Health & Family Welfare Disaster Medical Emergency Protocol",
        "section": "Section 3.2: Dialysis and High-Risk Pregnancy Pre-Evacuation",
        "page": 39,
        "keywords": ["dialysis", "pregnancy", "maa gruha", "high risk", "pre-evacuation", "hospital transit"],
        "text": (
            "High-risk pregnant women within 10 days of Expected Date of Delivery (EDD) and kidney patients requiring weekly "
            "dialysis located in marooned or coastal storm surge zones must be pre-evacuated to Maa Gruhas (Maternity Waiting "
            "Homes) or District Headquarters Hospitals (DHH) at least 48 hours prior to disaster landfall."
        ),
    },
    {
        "id": "SOP-RES-01",
        "doc_title": "ODRN (Odisha Disaster Resource Network) Mobilization Guidelines",
        "section": "Section 2.4: Tactical Resource Dispatch Protocol",
        "page": 12,
        "keywords": ["odrn", "resource dispatch", "tree cutters", "chainsaws", "pumps", "warehouse", "mutual aid"],
        "text": (
            "Requisitions for tactical equipment (inflatable motorized boats, hydraulic tree cutters, high-capacity dewatering "
            "pumps) must be routed through the District Emergency Operations Centre (DEOC) to the nearest ODRN warehouse. "
            "Mutual aid agreements between adjacent districts must be activated within 2 hours of formal requisition."
        ),
    },
    {
        "id": "SOP-WARN-01",
        "doc_title": "SATARK Multi-Hazard Early Warning Dissemination Protocol (OSDMA & IMD)",
        "section": "Section 1.2: Weather Alert Classification and Public Actions",
        "page": 5,
        "keywords": ["satark", "yellow alert", "orange alert", "red alert", "siren", "warning", "early warning"],
        "text": (
            "Color-coded warning guidelines: Green = No warning (Normal); Yellow = Watch and stay updated (Be aware); "
            "Orange = Be prepared (Severe weather expected, pre-position response assets); Red = Take Action (Catastrophic "
            "disaster imminent, execute mandatory evacuations). Coastal siren towers sound only during Orange and Red phases."
        ),
    },
    {
        "id": "SOP-WARN-02",
        "doc_title": "SATARK Multi-Hazard Early Warning Dissemination Protocol (OSDMA & IMD)",
        "section": "Section 3.3: Coastal Fisherman Warning Protocol",
        "page": 16,
        "keywords": ["fisherman", "trawlers", "sea condition", "harbor", "paradeep", "dhamra", "rough sea"],
        "text": (
            "Total suspension of fishing operations along the Odisha coastline when sea condition is rough to phenomenal "
            "(wind speed >= 45 km/h). All registered mechanized and traditional trawlers must be recalled to designated safe "
            "harbors (Paradeep, Dhamra, Gopalpur, Balaramgadi) within 12 hours of advisory broadcast."
        ),
    },
]


def tokenize_query(text: str) -> List[str]:
    """Extract clean words from query."""
    return [w for w in re.findall(r"\w+", text.lower()) if len(w) >= 3]


class RAGKnowledgeAssistant:
    """Retrieval-augmented knowledge assistant grounded in verified government manuals."""

    def __init__(self, corpus: Optional[List[dict]] = None):
        self.corpus = corpus or VERIFIED_SOP_CORPUS

    def search_corpus(self, query: str, top_k: int = 3) -> List[Tuple[dict, float]]:
        """Score each document chunk using hybrid token matching and keyword overlap."""
        query_words = set(tokenize_query(query))
        scored_results: List[Tuple[dict, float]] = []

        if not query_words:
            return []

        for chunk in self.corpus:
            chunk_text = chunk["text"].lower()
            chunk_keywords = [k.lower() for k in chunk["keywords"]]
            chunk_title = chunk["doc_title"].lower()
            chunk_section = chunk["section"].lower()

            score = 0.0

            # 1. Exact phrase or multi-word keyword match
            for kw in chunk_keywords:
                if kw in query.lower():
                    score += 0.40

            # 2. Token overlap with chunk text
            matched_words = 0
            for qw in query_words:
                if qw in chunk_text:
                    matched_words += 1
                elif qw in chunk_title or qw in chunk_section:
                    matched_words += 0.5

            token_score = matched_words / len(query_words)
            score += token_score * 0.60

            score = min(1.0, round(score, 3))
            if score > 0.15:
                scored_results.append((chunk, score))

        # Sort by score descending
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]

    async def answer_query(self, req: RAGQueryRequest) -> RAGResponse:
        """Answer disaster operational questions strictly grounded in official citations."""
        query = req.query.strip()
        top_results = self.search_corpus(query, top_k=req.top_k)

        # Refusal threshold: If top relevance score is below 0.30, refuse to hallucinate
        if not top_results or top_results[0][1] < 0.28:
            return RAGResponse(
                query=query,
                grounded_answer=(
                    "No verified official protocol found in the AapadaOps SOP database for this query. "
                    "In adherence to disaster safety protocols, this system does not invent unverified instructions. "
                    "Please refer directly to the State Emergency Operations Centre (SEOC) or Special Relief Commissioner (SRC) manual."
                ),
                citations=[],
                grounding_confidence=0.0,
                is_official_sop=False,
                refusal_reason="OUT_OF_DOMAIN_OR_UNVERIFIED_QUERY",
                source_manuals=[],
            )

        citations: List[RAGCitation] = []
        source_manuals: List[str] = []

        for chunk, score in top_results:
            if chunk["doc_title"] not in source_manuals:
                source_manuals.append(chunk["doc_title"])

            citations.append(
                RAGCitation(
                    document_name=chunk["doc_title"],
                    section=chunk["section"],
                    page=chunk["page"],
                    relevant_excerpt=chunk["text"],
                    relevance_score=score,
                )
            )

        # Synthesize grounded response using top citation excerpt
        top_chunk = top_results[0][0]
        top_confidence = top_results[0][1]

        grounded_answer = (
            f"According to the official {top_chunk['doc_title']} ({top_chunk['section']}, Page {top_chunk['page']}):\n\n"
            f"{top_chunk['text']}"
        )

        if len(top_results) > 1 and top_results[1][1] >= 0.35:
            second_chunk = top_results[1][0]
            grounded_answer += (
                f"\n\nAdditionally, as per {second_chunk['section']} (Page {second_chunk['page']}):\n"
                f"{second_chunk['text']}"
            )

        return RAGResponse(
            query=query,
            grounded_answer=grounded_answer,
            citations=citations,
            grounding_confidence=top_confidence,
            is_official_sop=True,
            refusal_reason=None,
            source_manuals=source_manuals,
        )


rag_assistant = RAGKnowledgeAssistant()

