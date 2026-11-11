"""AapadaOps Comprehensive AI Services Test Suite.

Tests:
1. Service A: Information Extraction (Multilingual, strict missing fields, zero hallucinations)
2. Service B: Odia Voice Processing (Acoustic analysis, provenance, low-confidence flags, human corrections)
3. Service C: Duplicate Detection (Embeddings, geo, time, category, explanation, no auto-merge)
4. Service D: Explainable Prioritization (7-factor scoring, breakdown, deterministic SLA)
5. Service E: RAG Knowledge Assistant (Official SOP retrieval, citations, out-of-domain refusal)
6. Service F: AI Safety Guardrails (Blocks autonomous high-consequence operations)
7. Service G: Empirical Benchmarks (Runs evaluation suite and asserts measured performance)
"""

import pytest
from app.ai.duplicate_detector import duplicate_detector
from app.ai.evaluator import evaluator
from app.ai.extractor import extraction_engine
from app.ai.prioritizer import prioritizer_engine
from app.ai.rag_assistant import rag_assistant
from app.ai.safety import safety_enforcer
from app.ai.schemas import (
    CandidateIncidentInput,
    ExtractionRequest,
    PrioritizationRequest,
    RAGQueryRequest,
    TranscriptCorrectionRequest,
    VoiceTranscriptionRequest,
)
from app.ai.voice_processor import voice_processor
from app.core.exceptions import AppException
from app.models.incident import IncidentCategory, IncidentSeverity


# ============================================================================
# Service A: Information Extraction Tests
# ============================================================================

@pytest.mark.asyncio
async def test_information_extraction_english_complete():
    """Test full extraction from an English disaster dispatch."""
    text = (
        "Mahanadi river embankment breached at Banki in Cuttack district. "
        "Around 45 villagers stranded on top of school roof. Severe flood water rising rapidly. "
        "1 pregnant woman needs emergency hospital transport. Send motor boats immediately."
    )
    req = ExtractionRequest(text=text, source="CALL_CENTER")
    record = await extraction_engine.extract_structured_incident(req)

    assert record.incident_category == IncidentCategory.EMBANKMENT_BREACH
    assert record.district == "Cuttack"
    assert record.people_affected == 45
    assert "PREGNANT_WOMAN_CARE" in record.medical_needs
    assert "INFLATABLE_RESCUE_BOAT" in record.resource_requirements
    assert "EMBANKMENT_STRUCTURAL_FAILURE" in record.severity_indicators
    assert record.is_advisory is True
    assert record.requires_human_verification is True
    assert record.confidence >= 0.70


@pytest.mark.asyncio
async def test_information_extraction_odia_script():
    """Test extraction from native Odia script."""
    text = "ବାଲେଶ୍ୱର ଚାନ୍ଦିପୁରରେ ବଡ଼ ଗଛ ପଡ଼ି ରାସ୍ତା ବନ୍ଦ ହୋଇଯାଇଛି, ଜରୁରୀ କରତ ମେସିନ ଦରକାର।"
    req = ExtractionRequest(text=text, source="CITIZEN_ODIA_APP")
    record = await extraction_engine.extract_structured_incident(req)

    assert record.incident_category == IncidentCategory.TREE_FALL
    assert record.district == "Balasore"
    assert record.detected_language == "or"
    assert "POWER_CHAINSAW_TREE_CUTTER" in record.resource_requirements
    assert record.people_affected is None
    # Crucial requirement: missing fields must be explicitly catalogued
    assert "people_affected" in record.missing_fields
    assert "medical_needs" in record.missing_fields


@pytest.mark.asyncio
async def test_information_extraction_zero_hallucination():
    """Verify missing information is NEVER fabricated."""
    sparse_text = "Fallen tree blocking path somewhere."
    req = ExtractionRequest(text=sparse_text, source="CITIZEN_SMS")
    record = await extraction_engine.extract_structured_incident(req)

    assert record.incident_category == IncidentCategory.TREE_FALL
    assert record.district is None
    assert record.location is None
    assert record.people_affected is None
    assert "district" in record.missing_fields
    assert "location" in record.missing_fields
    assert "people_affected" in record.missing_fields


# ============================================================================
# Service B: Odia Voice Processing Tests
# ============================================================================

@pytest.mark.asyncio
async def test_voice_transcription_and_provenance():
    """Test voice processing with audio references and Odia recognition."""
    req = VoiceTranscriptionRequest(
        audio_file_id="audio-ref-001",
        original_filename="field_report_odia.wav",
        mime_type="audio/wav",
        simulated_audio_text="ବାତ୍ୟା ପବନରେ ପୁରୀ ଜିଲ୍ଲାରେ ଗଛ ପଡି ରାସ୍ତା ବନ୍ଦ ରହିଛି।",
    )
    res = await voice_processor.transcribe_audio(req)

    assert res.audio_file_id == "audio-ref-001"
    assert res.detected_language == "or"
    assert "ପୁରୀ" in res.raw_transcript
    assert res.duration_seconds > 0.0
    assert 0.0 <= res.confidence_score <= 1.0


@pytest.mark.asyncio
async def test_voice_transcription_low_confidence_flagging():
    """Verify that degraded audio under cyclone storm noise is flagged for human review."""
    req = VoiceTranscriptionRequest(
        audio_file_id="audio-noisy-002",
        original_filename="cyclone_gale_wind_noise.wav",
        simulated_audio_text="Water entering house fast...",
    )
    res = await voice_processor.transcribe_audio(req)

    # Filename triggers storm/noise acoustic penalty
    assert res.is_low_confidence is True
    assert "HIGH_BACKGROUND_GALE_NOISE" in res.confidence_flags
    assert res.requires_human_correction is True


@pytest.mark.asyncio
async def test_human_transcript_correction():
    """Test human-in-the-loop correction of speech transcripts."""
    req = VoiceTranscriptionRequest(
        audio_file_id="audio-003",
        original_filename="garbled_speech.wav",
        simulated_audio_text="Some distorted speech words...",
    )
    res = await voice_processor.transcribe_audio(req)

    # Submit official human correction
    corr_req = TranscriptCorrectionRequest(
        transcript_id=res.audio_file_id,
        corrected_transcript="Baitarani dyke breached at Akhuapada, Bhadrak.",
        correction_notes="Verified by Verification Officer Das after listening to original audio.",
        verified_by_user_id="user-officer-01",
    )
    corr_res = await voice_processor.correct_transcript(corr_req)

    assert corr_res.is_human_verified is True
    assert corr_res.corrected_transcript == "Baitarani dyke breached at Akhuapada, Bhadrak."
    assert corr_res.verified_by_user_id == "user-officer-01"


# ============================================================================
# Service C: Duplicate Detection Tests
# ============================================================================

def test_duplicate_detection_pair_match():
    """Test multi-factor duplicate detection identifying close incident reports."""
    inc_a = CandidateIncidentInput(
        id="INC-001",
        incident_code="INC-KND-001",
        title="Flood water in Pattamundai",
        description="Brahmani river water entered houses in Pattamundai village, 20 people trapped on terrace.",
        category=IncidentCategory.FLOOD,
        latitude=20.5750,
        longitude=86.5650,
        district_name="Kendrapara",
        village_name="Pattamundai",
    )
    inc_b = CandidateIncidentInput(
        id="INC-002",
        incident_code="INC-KND-002",
        title="Pattamundai river embankment breach",
        description="Dyke broken near Pattamundai bridge. Water submerging residences, villagers marooned on roof.",
        category=IncidentCategory.EMBANKMENT_BREACH,
        latitude=20.5760,
        longitude=86.5658,
        district_name="Kendrapara",
        village_name="Pattamundai",
    )

    match = duplicate_detector.evaluate_pair(inc_b, inc_a)

    assert match.distance_meters < 300.0
    assert match.overall_score >= 0.65
    assert match.is_probable_duplicate is True
    assert "Potential duplicate" in match.plain_explanation
    # Check that individual factors are populated
    factor_names = [f.factor for f in match.factors]
    assert "GEOGRAPHIC_PROXIMITY" in factor_names
    assert "TEXT_SEMANTIC_SIMILARITY" in factor_names
    assert "CATEGORY_ALIGNMENT" in factor_names


def test_duplicate_detection_distinct_incidents():
    """Verify non-duplicates are cleanly separated."""
    inc_a = CandidateIncidentInput(
        id="INC-PURI",
        title="Cyclone winds in Puri beach",
        description="Gusty cyclonic winds blowing near Puri seashore.",
        category=IncidentCategory.CYCLONE_WIND,
        latitude=19.8135,
        longitude=85.8312,
        district_name="Puri",
    )
    inc_b = CandidateIncidentInput(
        id="INC-BALASORE",
        title="Tree fallen on road Balasore",
        description="Tree fallen on National Highway 16 near Balasore.",
        category=IncidentCategory.TREE_FALL,
        latitude=21.4934,
        longitude=86.9135,
        district_name="Balasore",
    )

    match = duplicate_detector.evaluate_pair(inc_b, inc_a)
    assert match.is_probable_duplicate is False
    assert match.overall_score < 0.40


# ============================================================================
# Service D: Explainable Prioritization Tests
# ============================================================================

def test_prioritization_critical_threat_to_life():
    """Verify multi-casualty embankment breach achieves CRITICAL tier with 2h SLA."""
    req = PrioritizationRequest(
        category=IncidentCategory.EMBANKMENT_BREACH,
        reported_severity=IncidentSeverity.CRITICAL,
        stranded_count=50,
        casualties=2,
        medical_needs=["PREGNANT_WOMAN_CARE"],
        access_cut_off=True,
        is_coastal_block=True,
        is_verified=True,
        report_freshness_hours=0.5,
    )
    res = prioritizer_engine.evaluate(req)

    assert res.priority_level == IncidentSeverity.CRITICAL
    assert res.composite_score >= 75.0
    assert res.recommended_sla_hours == 2
    assert len(res.factors) == 7
    # Check breakdown transparency
    factors_dict = {f.factor_name: f.points_awarded for f in res.factors}
    assert factors_dict["THREAT_TO_HUMAN_LIFE"] >= 30.0
    assert factors_dict["MEDICAL_URGENCY"] == 20.0
    assert "CRITICAL PRIORITY" in res.plain_language_summary


def test_prioritization_low_severity_routine():
    """Verify non-urgent tree fall without isolation receives LOW tier with 24h SLA."""
    req = PrioritizationRequest(
        category=IncidentCategory.TREE_FALL,
        reported_severity=IncidentSeverity.LOW,
        stranded_count=0,
        casualties=0,
        medical_needs=[],
        access_cut_off=False,
        is_coastal_block=False,
        is_verified=False,
        report_freshness_hours=12.0,
    )
    res = prioritizer_engine.evaluate(req)

    assert res.priority_level == IncidentSeverity.LOW
    assert res.composite_score < 25.0
    assert res.recommended_sla_hours == 24


# ============================================================================
# Service E: RAG Knowledge Assistant Tests
# ============================================================================

@pytest.mark.asyncio
async def test_rag_official_sop_query():
    """Verify retrieval of official OSDMA flood embankment breach procedure with citations."""
    req = RAGQueryRequest(query="What is the procedure when river embankment breach occurs and sandbagging?")
    res = await rag_assistant.answer_query(req)

    assert res.is_official_sop is True
    assert res.grounding_confidence >= 0.35
    assert len(res.citations) > 0
    top_citation = res.citations[0]
    assert "OSDMA" in top_citation.document_name
    assert top_citation.page > 0
    assert "sandbags" in top_citation.relevant_excerpt.lower()


@pytest.mark.asyncio
async def test_rag_snakebite_protocol():
    """Verify official medical protocol regarding snake bites and tourniquets."""
    req = RAGQueryRequest(query="What is the guideline for snake bite treatment in flood zones and tourniquets?")
    res = await rag_assistant.answer_query(req)

    assert res.is_official_sop is True
    assert any("Anti-Snake Venom" in c.relevant_excerpt or "tourniquet" in c.relevant_excerpt.lower() for c in res.citations)


@pytest.mark.asyncio
async def test_rag_hallucination_prevention_on_unrelated_query():
    """Verify assistant refuses to hallucinate when asked non-disaster questions."""
    req = RAGQueryRequest(query="Tell me about recipes for making chocolate cake in Italy.")
    res = await rag_assistant.answer_query(req)

    assert res.is_official_sop is False
    assert res.refusal_reason == "OUT_OF_DOMAIN_OR_UNVERIFIED_QUERY"
    assert "No verified official protocol found" in res.grounded_answer
    assert len(res.citations) == 0


# ============================================================================
# Service F: Safety Guardrails Tests
# ============================================================================

def test_safety_guardrail_blocks_autonomous_dispatch():
    """Verify AI cannot autonomously dispatch search & rescue teams."""
    with pytest.raises(AppException) as excinfo:
        safety_enforcer.assert_action_permitted("DISPATCH_RESPONSE_TEAM", is_ai_invoked=True)
    assert excinfo.value.code == "AUTONOMOUS_ACTION_PROHIBITED"
    assert "authorized human signature" in str(excinfo.value.message)


def test_safety_guardrail_blocks_autonomous_evacuation():
    """Verify AI cannot autonomously order village evacuations."""
    with pytest.raises(AppException) as excinfo:
        safety_enforcer.assert_action_permitted("AUTHORIZE_ZONE_EVACUATION", is_ai_invoked=True)
    assert excinfo.value.code == "AUTONOMOUS_ACTION_PROHIBITED"
    assert "District Magistrate" in str(excinfo.value.message)


# ============================================================================
# Service G: Empirical Evaluation Suite Test
# ============================================================================

@pytest.mark.asyncio
async def test_ai_benchmark_evaluation_suite():
    """Execute complete benchmark suite and assert measured accuracy and latency."""
    report = await evaluator.run_full_evaluation_suite()

    assert len(report.benchmarks) >= 4
    for b in report.benchmarks:
        assert b.accuracy >= 0.75, f"Subsystem {b.service_name} accuracy below target threshold"
        assert b.avg_latency_ms < 500.0, f"Subsystem {b.service_name} latency exceeds 500ms"

    assert report.safety_compliance["prohibit_autonomous_dispatch"] is True
    assert report.safety_compliance["prohibit_automatic_merge"] is True

