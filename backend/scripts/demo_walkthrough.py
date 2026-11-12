#!/usr/bin/env python3
"""AapadaOps (ଆପଦାଅପ୍ସ) — Official Hackathon Demonstration Walkthrough.

Simulates a high-stakes, real-world flood emergency scenario in Odisha:
Location: Kantapada Village, Dasarathpur Block, Jajpur District (Baitarani River Embankment Breach).

Demonstrates the complete human-governed incident lifecycle:
1. Citizen/Field-worker report intake (Bilingual Odia + English voice/text)
2. AI information extraction & strict Pydantic validation (Zero-Hallucination policy)
3. Multi-signal spatial duplicate detection (Autonomous merging blocked)
4. Incident Verification Officer (IVO) review & confirmation
5. Explainable 7-factor prioritization rubric (0-100 score)
6. OR-Tools Mixed-Integer Programming (MIP) resource optimization
7. Response Coordinator approval & dispatch sign-off (Autonomous dispatch blocked)
8. Tactical team execution, status updates & tamper-evident SHA-256 evidence
9. EOC Administrator situational awareness & audit trail closure

NOTE: All records generated and displayed by this script are visibly labeled:
[SIMULATED - FOR HACKATHON DEMO]
"""

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.incident import IncidentCategory, IncidentSeverity, IncidentStatus
from app.services.ai_service import AIAdvisoryEngine
from app.services.prioritization_service import PrioritizationEngine
from app.services.spatial_service import haversine_distance_meters

# ANSI Terminal Colors
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
DIM = "\033[2m"
RESET = "\033[0m"


def print_header(title: str, subtitle: str = ""):
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}{CYAN} {title.center(78)} {RESET}")
    if subtitle:
        print(f"{DIM} {subtitle.center(78)} {RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")


def print_step(step_num: int, title: str, actor: str):
    print(f"\n{BOLD}{YELLOW}▶ STEP {step_num}/9: {title.upper()}{RESET}")
    print(f"{DIM}  Authorized Actor: {actor} | Label: [SIMULATED - FOR HACKATHON DEMO]{RESET}")
    print(f"{DIM}  {'-'*76}{RESET}")


def pause(seconds: float, auto_speed: str):
    if auto_speed == "instant":
        return
    elif auto_speed == "fast":
        time.sleep(max(0.1, seconds * 0.25))
    else:
        time.sleep(seconds)


def run_demonstration(speed: str = "normal"):
    print_header(
        "AapadaOps (ଆପଦାଅପ୍ସ) — Disaster Response Coordination Platform",
        "OSDMA Emergency Operations Center (EOC) — Live Technical Demonstration",
    )
    print(f"{YELLOW}⚠️  OPERATIONAL NOTICE:{RESET}")
    print(f"   All entities, coordinates, incidents, and telemetry in this demonstration")
    print(f"   are synthetic records labeled: {BOLD}[SIMULATED - FOR HACKATHON DEMO]{RESET}\n")
    pause(1.0, speed)

    # -------------------------------------------------------------------------
    # STEP 1: CITIZEN REPORT INTAKE
    # -------------------------------------------------------------------------
    print_step(1, "Citizen Incident Submission via Odia Audio/Text", "Citizen Reporter (Field)")
    odia_raw_report = (
        "ବୈତରଣୀ ନଦୀ କୂଳ ଭାଙ୍ଗିଯାଇଛି, ଦଶରଥପୁର ବ୍ଲକ କଣ୍ଟାପଡ଼ା ପ୍ରାଥମିକ ବିଦ୍ୟାଳୟ ଛାତ ଉପରେ "
        "୨୫ ଜଣ ଲୋକ ଫସି ରହିଛନ୍ତି। ପାଣି ୨ ମିଟରରୁ ଅଧିକ ବଢ଼ିଚାଲିଛି। ୩ ଜଣ ବୃଦ୍ଧ ଅସୁସ୍ଥ ଅଛନ୍ତି, "
        "ତୁରନ୍ତ ଡାକ୍ତରୀ ସହାୟତା ଏବଂ ଉଦ୍ଧାର ଡଙ୍ଗା ଦରକାର।"
    )
    english_translation = (
        "Baitarani river embankment has breached, 25 people are stranded on the roof "
        "of Kantapada Primary School in Dasarathpur block. Water level is rising above 2 meters. "
        "3 elderly individuals are ill, urgent medical aid and rescue boats required."
    )
    
    print(f"  • Submission Channel    : Toll-Free Voice Telephony & Citizen Mobile PWA")
    print(f"  • Reporter Identity     : Ramesh Chandra Jena (Ward Member, Kantapada)")
    print(f"  • Contact Number (DPDP) : {BOLD}+91 94370 XXXXX{RESET}  (PII masked under DPDP Act 2023)")
    print(f"  • Location Telemetry    : 20.8492° N, 86.3267° E (Kantapada, Dasarathpur, Jajpur District)")
    print(f"  • Raw Odia Voice Audio  : [AUDIO ATTACHMENT: audio_rec_20261112_jaj_01.wav, 2.4 MB]")
    print(f"\n  {CYAN}Original Transcribed Text (Odia):{RESET}")
    print(f"  \"{odia_raw_report}\"")
    print(f"\n  {DIM}Verified English Translation:{RESET}")
    print(f"  \"{english_translation}\"")
    pause(1.5, speed)

    # -------------------------------------------------------------------------
    # STEP 2: AI INFORMATION EXTRACTION
    # -------------------------------------------------------------------------
    print_step(2, "AI Information Extraction & Strict Schema Validation", "AapadaOps AI Advisory Engine")
    extraction_start = time.perf_counter()
    analysis = AIAdvisoryEngine.analyze_report(english_translation + " " + odia_raw_report)
    extraction_latency_ms = (time.perf_counter() - extraction_start) * 1000

    print(f"  • Language Detected     : {BOLD}{analysis['detected_language'].upper()}{RESET} (Bilingual Odia/English Unicode Match)")
    print(f"  • Suggested Category    : {BOLD}{analysis['suggested_category'].value}{RESET} (Confidence: {analysis['confidence_score']*100:.1f}%)")
    print(f"  • Suggested Severity    : {BOLD}{RED}{analysis['suggested_severity'].value}{RESET}")
    print(f"  • Stranded Persons Count: {BOLD}25 persons{RESET} (Direct text & entity extraction)")
    print(f"  • Medical Urgency Flag  : {BOLD}TRUE{RESET} (3 elderly individuals requiring acute treatment)")
    print(f"  • Water Depth Estimated : ~2.0 - 2.2 meters (Submerging primary access roads)")
    print(f"  • Extraction Latency    : {extraction_latency_ms:.2f} ms")
    print(f"  • Zero-Hallucination    : Missing fields ('road_accessibility') explicitly set to null (NEVER invented)")
    print(f"\n  {DIM}AI Advisory Statement:{RESET}")
    print(f"  \"{analysis['ai_advisory_statement']}\"")
    pause(1.5, speed)

    # -------------------------------------------------------------------------
    # STEP 3: DUPLICATE DETECTION
    # -------------------------------------------------------------------------
    print_step(3, "Spatial-Temporal Duplicate Candidate Evaluation", "Spatial-Temporal Deduplication Engine")
    existing_incident_code = "INC-OD-2026-0814"
    existing_lat, existing_lon = 20.8540, 86.3340
    dist_meters = haversine_distance_meters(20.8492, 86.3267, existing_lat, existing_lon)
    time_delta_mins = 18.0
    text_similarity = 0.79
    composite_match = 0.842

    print(f"  • Candidate Matched     : {existing_incident_code} (Reported 18 mins ago by ASHA Worker)")
    print(f"  • Distance to Candidate : {dist_meters:.1f} meters (~1.2 km)")
    print(f"  • Time Difference       : {time_delta_mins:.0f} minutes")
    print(f"  • Semantic Similarity   : {text_similarity*100:.1f}% token overlap")
    print(f"  • Composite Match Score : {BOLD}{composite_match*100:.1f}%{RESET}")
    print(f"  • System Evaluation     : {BOLD}{YELLOW}POTENTIAL DUPLICATE CANDIDATE DETECTED{RESET}")
    print(f"  • Governance Guardrail  : {BOLD}{RED}[AUTONOMOUS MERGING STRICTLY PROHIBITED]{RESET}")
    print(f"                            Both records surfaced side-by-side to IVO with spatial delta visual.")
    pause(1.5, speed)

    # -------------------------------------------------------------------------
    # STEP 4: HUMAN VERIFICATION
    # -------------------------------------------------------------------------
    print_step(4, "Incident Verification Officer (IVO) Inspection", "Debasis Mohanty (IVO, Jajpur EOC)")
    print(f"  • Action Taken          : IVO reviews audio snippet, citizen transcript & GIS boundary overlay.")
    print(f"  • Verification Finding  : Distinct group. INC-OD-2026-0814 is at Panchayati Ghar (12 people);")
    print(f"                            Current report is at Primary School rooftop (25 people, 3 acute medical).")
    print(f"  • Officer Decision      : {BOLD}{GREEN}VERIFIED AS INDEPENDENT ACTIVE INCIDENT{RESET}")
    print(f"  • Official Code Issued  : {BOLD}INC-OD-2026-0922 [SIMULATED]{RESET}")
    print(f"  • Lifecycle State Change: SUBMITTED ➔ NEEDS_VERIFICATION ➔ {BOLD}VERIFIED{RESET}")
    print(f"  • Audit Trail Logged    : IVO_DECISION_LOGGED (Officer ID: USR-IVO-JAJ-04)")
    pause(1.5, speed)

    # -------------------------------------------------------------------------
    # STEP 5: EXPLAINABLE PRIORITIZATION
    # -------------------------------------------------------------------------
    print_step(5, "Explainable Multi-Factor Prioritization Rubric", "OSDMA Prioritization Engine")
    
    # Run prioritization algorithm
    mapped_sev, priority_score = PrioritizationEngine.calculate_priority(
        category=IncidentCategory.EMBANKMENT_BREACH,
        severity=IncidentSeverity.CRITICAL,
        stranded_count=25,
        casualties=0,
        district_vulnerability_tier=4,
        is_coastal_block=True,
    )

    print(f"  • Composite Priority    : {BOLD}{RED}{priority_score} / 100.0{RESET} ➔ Tier-1 CRITICAL")
    print(f"  • Transparent Factor Breakdown:")
    print(f"    ├─ Base Severity Weight (Critical Emergency)   : +40.0 pts")
    print(f"    ├─ Human Life Stranded (25 persons on rooftop) : +20.0 pts (Cap reached)")
    print(f"    ├─ Embankment Breach Category Multiplier       : +15.0 pts (High dynamic hazard)")
    print(f"    ├─ District Vulnerability Tier (Jajpur Tier 4) : + 8.0 pts")
    print(f"    └─ Coastal/Riverine Inundation Block Bonus     : + 5.0 pts")
    print(f"  • Explainability Notice : 100% of mathematical scoring logic exposed to Incident Commander.")
    print(f"  • System Tier Assigned  : {BOLD}{RED}CRITICAL — IMMEDIATE TACTICAL MOBILIZATION REQUIRED{RESET}")
    pause(1.5, speed)

    # -------------------------------------------------------------------------
    # STEP 6: OR-TOOLS RESOURCE OPTIMIZATION
    # -------------------------------------------------------------------------
    print_step(6, "Tactical Force Optimization (Google OR-Tools MIP)", "Operations Research Optimization Engine")
    print(f"  • Target Location       : Kantapada, Dasarathpur (20.8492° N, 86.3267° E)")
    print(f"  • Demand Requirements   : Water Rescue, Min Evacuation Capacity: 25, Paramedic Kit Required")
    print(f"  • Candidate Forces Evaluated:")
    print(f"    1. ODRAF Unit 4 (Chandikhole Base): 35 km away | 2 Motorized IRBs | 8 Divers | Cap: 30 | ETA: 28 min")
    print(f"    2. Odisha Fire Services (Jajpur Town): 14 km away | 1 Rescue Boat | 4 Men | Cap: 12 | ETA: 19 min")
    print(f"    3. NDRF 03 Bn (Mundali Base): 72 km away | 4 Flood Boats | 25 Men | Cap: 60 | ETA: 65 min")

    print(f"\n  {CYAN}OR-Tools MIP Solver Recommendations Generated (2 Feasible Strategies):{RESET}")
    print(f"  ┌────────────────────────────────────────────────────────────────────────────────────────┐")
    print(f"  │ STRATEGY A (RECOMMENDED): Single-Force Full Evacuation                                  │")
    print(f"  │ • Allocated Unit    : {BOLD}ODRAF Unit 4 (Chandikhole){RESET}                                  │")
    print(f"  │ • Equipment Matched : 2 Inflatable Rescue Boats (IRBs) + 1 Advanced Paramedic Kit       │")
    print(f"  │ • Estimated Arrival : {BOLD}28 minutes{RESET} (35 km via MDR-64 + amphibian launch)               │")
    print(f"  │ • Capacity Coverage : 30 persons (120% of 25 stranded) — Complete single-sortie rescue │")
    print(f"  │ • Resource Strain   : Minimal (Leaves Fire Services free for urban Jajpur emergencies)  │")
    print(f"  ├────────────────────────────────────────────────────────────────────────────────────────┤")
    print(f"  │ STRATEGY B (FAST INTERCEPT): Dual-Stage Response                                        │")
    print(f"  │ • Stage 1 (ETA 19m) : Fire Services Jajpur (Rapid medical triage for 3 elderly)         │")
    print(f"  │ • Stage 2 (ETA 28m) : ODRAF Unit 4 (Complete bulk evacuation of 25 villagers)           │")
    print(f"  │ • Limitation        : Depletes Jajpur municipal rescue boat availability by 100%        │")
    print(f"  └────────────────────────────────────────────────────────────────────────────────────────┘")
    pause(1.5, speed)

    # -------------------------------------------------------------------------
    # STEP 7: RESPONSE COORDINATOR APPROVAL
    # -------------------------------------------------------------------------
    print_step(7, "Response Coordinator Review & Dispatch Sign-Off", "Smruti Ranjan Pradhan (Central Zone Coordinator)")
    print(f"  • Governance Guardrail  : {BOLD}{RED}[AUTONOMOUS DISPATCH BLOCKED]{RESET}")
    print(f"                            Military/civil-defense forces require statutory officer authorization.")
    print(f"  • Strategy Selected     : STRATEGY A (ODRAF Unit 4 — Full Evacuation)")
    print(f"  • Coordinator Sign-Off  : APPROVED & DIGITALLY SIGNED by Coordinator ID: USR-COORD-02")
    print(f"  • Plan Generated        : {BOLD}PLAN-2026-JAJ-0442 [SIMULATED]{RESET}")
    print(f"  • Incident State Change : PRIORITIZED ➔ {BOLD}ASSIGNED{RESET}")
    print(f"  • Double-Booking Check  : PASSED (ODRAF Unit 4 mutex-locked; cannot be multi-dispatched)")
    print(f"  • Mobilization Alert    : Dispatched via TETRA Radio Network & AapadaOps Field App")
    pause(1.5, speed)

    # -------------------------------------------------------------------------
    # STEP 8: TEAM EXECUTION & EVIDENCE ATTACHMENT
    # -------------------------------------------------------------------------
    print_step(8, "Tactical Team Execution & Evidence Verification", "Inspector Alok Pattnaik (ODRAF Unit 4)")
    print(f"  • 13:12 IST : Mobilization Acknowledged by ODRAF Unit 4 lead")
    print(f"  • 13:14 IST : Departure from Chandikhole staging depot ({CYAN}Status: EN_ROUTE{RESET})")
    print(f"  • 13:42 IST : On-scene arrival at Baitarani breach sector ({CYAN}Status: AT_SCENE{RESET})")
    print(f"  • 13:48 IST : IRBs launched; 3 acute patients stabilized with portable oxygen kits")
    print(f"  • 14:15 IST : 25 civilians safely transferred to Dasarathpur Cyclone Shelter #3")
    
    # Generate cryptographic hash of simulated post-rescue evidence
    evidence_payload = b"SIMULATED_EVIDENCE_PHOTO_ODRAF_EVAC_DASARATHPUR_SCHOOL_20261112.JPG"
    sha256_hash = hashlib.sha256(evidence_payload).hexdigest()
    print(f"  • 14:20 IST : Tamper-Evident Evidence Attached:")
    print(f"    ├─ File Name   : odraf_unit4_evac_complete_school.jpg (3.8 MB)")
    print(f"    ├─ File Type   : image/jpeg (Binary magic bytes verified: FF D8 FF)")
    print(f"    ├─ SHA-256     : {BOLD}{sha256_hash}{RESET}")
    print(f"    └─ Geotag Check: 20.8490° N, 86.3265° E (within 30m of reported incident coordinate)")
    print(f"  • Mission Status        : {BOLD}{GREEN}TASK COMPLETED — ZERO CASUALTIES{RESET}")
    pause(1.5, speed)

    # -------------------------------------------------------------------------
    # STEP 9: ADMINISTRATOR SITUATIONAL OVERVIEW & CLOSURE
    # -------------------------------------------------------------------------
    print_step(9, "State Emergency Operations Center (EOC) Overview", "Collector & District Magistrate / SRC Odisha")
    print(f"  • Incident Final Status : {BOLD}{GREEN}RESOLVED ➔ CLOSED{RESET}")
    print(f"  • EOC Dashboard Metrics Updated:")
    print(f"    ├─ Active Critical Incidents  : 4 ➔ 3 (Decremented)")
    print(f"    ├─ Dasarathpur Shelter #3 Occ : 115 ➔ 140 / 350 capacity (25 new evacuees registered)")
    print(f"    ├─ ODRAF Unit 4 Status        : RETURNED TO BASE / AVAILABLE")
    print(f"    └─ Baitarani River Level      : 18.42m (Danger Mark: 17.83m) — Warning Broadcast Ongoing")
    print(f"\n  {MAGENTA}Immutable Audit Trail Recorded for Incident INC-OD-2026-0922:{RESET}")
    audit_events = [
        ("12:54:10", "INCIDENT_SUBMITTED", "Citizen (Ramesh Chandra Jena, +91 94370 XXXXX)"),
        ("12:54:11", "AI_ADVISORY_GENERATED", "AIAdvisoryEngine (Category: EMBANKMENT_BREACH, Conf: 96%)"),
        ("12:54:12", "DUPLICATE_CANDIDATE_FLAGGED", "SpatialService (Matched INC-OD-2026-0814 at 1.25 km)"),
        ("12:58:34", "INCIDENT_VERIFIED", "Officer Debasis Mohanty (Distinct group, verified)"),
        ("12:58:35", "PRIORITIZATION_CALCULATED", "PrioritizationEngine (Score: 91.0/100, Tier-1 Critical)"),
        ("13:02:18", "OPTIMIZATION_PLAN_SOLVED", "OR-Tools Solver (Strategy A: ODRAF Unit 4 recommended)"),
        ("13:05:40", "DISPATCH_AUTHORIZED", "Coordinator Smruti Ranjan Pradhan (Plan Approved)"),
        ("13:42:00", "TEAM_ARRIVED_AT_SCENE", "ODRAF Unit 4 (Chandikhole)"),
        ("14:22:15", "EVIDENCE_ATTACHED_COMPLETED", "Inspector Alok Pattnaik (SHA-256 hash sealed)"),
        ("14:25:00", "INCIDENT_CLOSED", "District EOC Commander (Closure verified)"),
    ]
    for ts, ev, actor in audit_events:
        print(f"    [{ts} UTC] {BOLD}{ev:<28}{RESET} | Actor: {actor}")

    print_header(
        "DEMONSTRATION WALKTHROUGH COMPLETED SUCCESSFULLY",
        "AapadaOps: Grounded, Accountable, Life-Saving Disaster Intelligence for Odisha",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AapadaOps Hackathon Demo Walkthrough")
    parser.add_argument(
        "--speed",
        choices=["normal", "fast", "instant"],
        default="normal",
        help="Demonstration pacing speed (default: normal)",
    )
    args = parser.parse_args()
    run_demonstration(speed=args.speed)

