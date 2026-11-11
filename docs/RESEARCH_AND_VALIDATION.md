# AapadaOps — Domain Research, Problem Validation & Requirements Specification

**Document Class**: Product Research & Domain Analysis  
**Context**: Odisha Disaster Management (OSDMA, SRC, District Collectorates, Grassroots Administration)  
**Author**: Principal Engineer & Disaster-Management Domain Analyst  
**Version**: 1.0.0 (Prompt 1 Phase)  

---

## 1. Problem Statement

### The Core Problem
During catastrophic weather events in Odisha (severe tropical cyclones like Fani/Yaas/Dana and seasonal riverine floods across the Mahanadi, Brahmani, and Baitarani basins), the operational bottleneck is **not** a lack of meteorological forecasting or physical rescue equipment. Rather, it is the **information chaos in transforming thousands of scattered, unstructured, frantic field reports into verified, deduplicated, and actionable administrative dispatch tasks**.

Currently, emergency distress reports enter the administrative machinery across fragmented, un-integrated channels:
1. Jammed voice helplines (**1070** at State EOC, **1077** at District EOCs, **112** ERSS).
2. Ad-hoc, unorganized **WhatsApp groups** established between BDOs, Tahasildars, Revenue Inspectors (RIs), and Sarpanchs.
3. Unverified social media posts and frantic citizen calls.
4. Informal word-of-mouth reports from coastal Multi-Purpose Cyclone Shelters (MCS) and field volunteers (Aapda Mitra).

### Resulting Operational Breakdown
- **Extreme Duplication**: Up to 40–60 calls or messages are generated for the exact same event (e.g., an embankment breach at Akhuapada or an uprooted tree blocking NH-16), drowning out isolated, life-critical SOS calls from vulnerable hamlets.
- **Verification Paralysis**: Grassroots officials (Revenue Inspectors, Village Agriculture Workers, Panchayat Executive Officers) are simultaneously tasked with managing relief camps, operating free kitchens, and physically verifying damage. Disparate reports cannot be easily cross-checked against satellite flood inundation models or cadastral boundaries.
- **Resource Misallocation**: District Collectors and BDOs lack a unified operational tactical picture that links verified distress incidents to the real-time availability of tactical resources (ODRAF teams, NDRF battalions, BAUT rescue boats, dewatering pumps, generator sets).
- **Post-Disaster Audit & Compensation Friction**: Manual, hurried paper/spreadsheet compilation creates discrepancies in damage assessments, leading to inclusion/exclusion errors, public grievances, and delayed State Disaster Response Fund (SDRF) disbursements.

---

## 2. Target Users

| User Persona | Role & Organizational Scope | Operational Environment | Primary Task within AapadaOps |
|---|---|---|---|
| **State EOC Director / SRC Operations Head** | Apex state-level command (Bhubaneswar EOC) | Multi-monitor command center; broadband; state video wall | Macro-level situational monitoring; inter-district asset mobilization (ODRAF / NDRF / helicopters); state CAP alerts |
| **District Collector / District Emergency Officer (DEO)** | District Magistrate heading DDMA (30 districts) | High-stress district control room; satellite comms + cellular | Declaring evacuation orders; activating MCS shelters; dispatching district tactical reserves; signing off SitReps |
| **Block Development Officer (BDO) / Tahasildar** | Block-level field command (314 blocks / ULBs) | Block office; intermittent power; desktop + mobile | Reviewing block-level incident feeds; verifying village reports; dispatching local line teams; managing camp supplies |
| **Field Responder / Revenue Inspector (RI) / Fire Station Officer** | Frontline execution (ODRAF, OFES, Police, RI) | Outdoor field conditions; rain/wind; smartphone/tablet | Receiving geocoded dispatch tasks; onsite photo/GPS verification; task status updating (En Route, On Scene, Resolved) |
| **Aapda Mitra / CSMMC Volunteer** | Grassroots community disaster volunteer (GP level) | Cyclone shelter / village hamlet; rugged mobile device | Conducting shelter headcount; reporting urgent camp shortages (water, food, medicine); flagging vulnerable citizens |
| **Citizen / Affected Resident** | General public in threat zones | Low-bandwidth mobile; Odia/English speaker | Submitting one-tap SOS distress reports; receiving verified localized evacuation advisories; locating open shelters |

---

## 3. Stakeholder Analysis

```
+---------------------------------------------------------------------------------+
|                                 STAKEHOLDER MAP                                 |
+---------------------------------------------------------------------------------+
|                                                                                 |
|   HIGH INFLUENCE                                                                |
|   ^                                                                             |
|   |  [Special Relief Commissioner (SRC)]     [District Collectors (DDMA)]       |
|   |  - Apex policy, funding, SDRF funds      - Ground operational command       |
|   |  - Zero-casualty accountability          - Resource requisition authority   |
|   |                                                                             |
|   |  [OSDMA Leadership]                      [ODRAF / NDRF / Fire Services]     |
|   |  - Institutional mandate                 - Tactical deployment              |
|   |  - System integration approval           - Life-safety search & rescue      |
|   |                                                                             |
|   |--------------------------------------------------------------------------   |
|   |                                                                             |
|   |  [Line Departments (WRD, Agri, PR&DW)]   [BDOs, Tahasildars, RIs]           |
|   |  - Dam releases, drinking water, roads   - Verification & relief logistics  |
|   |  - Sectoral damage assessments           - High-workload administrative hub |
|   |                                                                             |
|   |  [Telecom / Media / Civil Society]       [Aapda Mitra / Rural Citizens]     |
|   |  - Public information dissemination      - Direct beneficiaries             |
|   |  - External communication carriers       - Ground truth source              |
|   |                                                                             v
|   LOW INFLUENCE -------------------------------------------------> HIGH INTEREST|
+---------------------------------------------------------------------------------+
```

### Detailed Stakeholder Breakdown:
1. **OSDMA & SRC**: Demands compliance with the Odisha Relief Code, verifiable audit trails, zero casualties, and seamless SitRep (Situation Report) generation for the Chief Minister and NDMA.
2. **District Magistrates / Collectors**: Demand high-density, accurate geospatial situational awareness without being swamped by unverified noise or conflicting departmental claims.
3. **Block & Tehsil Functionaries (BDOs/Tahasildars)**: Demand rapid deduplication tools so they don't dispatch two rescue boats to the same flooded village while ignoring a neighboring un-reported hamlet.
4. **Field Units (ODRAF / Fire Services)**: Demand precise GPS pins, turn-by-turn flood-safe route info, nature of entrapment (e.g. infants, pregnant women), and direct contact numbers.
5. **CSMMC (Cyclone Shelter Management and Maintenance Committees)**: Demand timely replenishment of drinking water, halogen tablets, dry rations (chuda/guda), and baby food.
6. **Citizens**: Demand immediate confirmation that their SOS was received, is being acted upon, and what safe actions to take.

---

## 4. Existing Solution Comparison

To maintain architectural integrity, we must evaluate what existing platforms already provide and avoid claiming novelty where proven solutions exist.

| Platform / System | Managing Agency | Core Strengths (What it Already Does Well) | Critical Gaps & Operational Deficiencies |
|---|---|---|---|
| **SATARK** (*System for Assessing, Tracking and Alerting Disaster Risk Information*) | OSDMA + RIMES | • Excellent multi-hazard forecast modeling (lightning, cyclone, rain, heatwave)<br>• Web/mobile bilingual warning bulletins<br>• Automated block-level risk scoring | • **One-way broadcast only**: No citizen or volunteer incident intake<br>• No task assignment or dispatch management<br>• No shelter-level inventory or occupancy tracking |
| **ODRN** (*Odisha Disaster Resource Network*) | OSDMA + NIC | • Exhaustive GIS database of government and private assets (boats, JCBs, cranes, shelters)<br>• Granular state-to-GP asset directory | • **Static inventory ledger**: Lacks dynamic real-time operational status (e.g. which boat is currently out of fuel, broken, or deployed at an active incident)<br>• No operational dispatch workflows |
| **EWDS** (*Early Warning Dissemination System*) | OSDMA (NCRMP / World Bank) | • 122+ coastal high-decibel siren towers<br>• Direct button activation from SEOC/DEOC<br>• Redundant DMR and satellite links | • **Downstream broadcast only**: Pure alerting tool<br>• Cannot capture reverse telemetry, damage evidence, or rescue requests from communities |
| **Emergency Lines (1070, 1077, 112 ERSS)** | SEOC / DEOC / Home Dept | • Universally accessible via standard telephony<br>• Dedicated operators | • **Severe telephonic congestion** during peak landfall<br>• Audio calls lack automated GPS coordinates<br>• No automated spatial clustering (50 callers describing the same fallen tree generate 50 separate manual log sheets) |
| **Jana Sunani / Mo Sarkar** | General Administration Dept | • Robust citizen grievance tracking with ticket tracking IDs and CM Cell integration | • Built for **15–30 day routine administrative SLAs** (pensions, land mutation, civil issues)<br>• Completely unsuited for minute-by-minute life-saving disaster operations |
| **Informal WhatsApp Groups** | BDOs / Police / Line Depts | • Immediate media sharing (photos, voice notes)<br>• Universally adopted and familiar to all field staff | • **Zero structure**: Media is uncompressed, unindexed, and untracked<br>• High risk of viral fake/recycled flood videos causing panic<br>• No SLA tracking, no GIS mapping, and zero formal accountability |

---

## 5. Identified Opportunity

The distinct opportunity for **AapadaOps** is to serve as the **Operational Connective Tissue** bridging the gap between:
- **Top-down hazard warnings** (SATARK / EWDS / CAP), and
- **Bottom-up distress intake and field execution** (Citizen SOS, Aapda Mitra volunteers, ODRAF / Fire Services dispatches).

```
                      EXISTING GAP
                           |
 [Top-Down Warnings]       v      [Field Execution]
 (SATARK / EWDS / IMD) <=======> (ODRAF / OFES / BDOs)
                           ^
                           |
                      AAPADAOPS
        (Triage -> Verify -> Deduplicate -> Dispatch)
```

Specifically, AapadaOps fills the following systemic voids:
1. **Intelligent Ingestion & Geocoding**: Ingesting unstructured reports (voice transcripts, web SOS, SMS, field volunteer inputs) into structured GeoJSON records.
2. **Automated Spatial Clustering & Deduplication**: Algorithmic grouping of incoming distress calls within a dynamic geographical radius (e.g., 200m–500m) and temporal window (1–2 hours), preventing operator cognitive overload.
3. **Bilingual (Odia + English) AI Severity Triage**: Extracting critical entities (e.g. "pregnant woman", "infants", "water level 6ft", "roof collapse", "embankment breach") and scoring priority from Routine to Critical Life Threat.
4. **Closed-Loop Task Dispatch**: Turning an incident into an administrative dispatch order with explicit ownership (BDO $\to$ Fire Station Officer / ODRAF Team Leader) and real-time lifecycle tracking (Dispatched $\to$ On-Scene $\to$ Rescued $\to$ Verified $\to$ Closed).
5. **Dynamic Shelter Logistics Cockpit**: Moving beyond static shelter directories by tracking live headcounts, ration days remaining, drinking water liters, and diesel generator fuel hours.

---

## 6. User Pain Points (By Persona)

### A. District Collector / Additional District Magistrate (ADM)
- **Pain Point 1: Conflicting Data Streams**: During Cyclone Dana/Fani, the Collector receives one casualty/damage estimate from the Police, another from the Tahasildar, and a wildly different figure on Twitter/WhatsApp.
- **Pain Point 2: Blind Resource Deployment**: No real-time visibility into whether the 4 ODRAF boats sent to Rajnagar block are actively rescuing stranded villagers or stuck in traffic due to fallen trees on the access road.
- **Pain Point 3: Time-Consuming SitRep Preparation**: Spending hours compiling manual spreadsheets from 14 blocks to submit the mandatory 6:00 PM SitRep to the Special Relief Commissioner.

### B. Block Development Officer (BDO) & Tahasildar
- **Pain Point 1: Telephonic Swamping**: The BDO's phone rings continuously with repetitive complaints while they need to orchestrate food distribution.
- **Pain Point 2: Verification Bottleneck**: With only 3–5 Revenue Inspectors covering 25 Gram Panchayats, physical verification of every single damaged house report is impossible in the first 48 hours.
- **Pain Point 3: Ration Stockout Surprises**: Discovering that a cyclone shelter has run out of baby food or drinking water pouches only *after* the local Sarpanch calls in distress.

### C. Field Responder (ODRAF Team Lead / Fire Officer / Aapda Mitra)
- **Pain Point 1: Vague Incident Locations**: Receiving orders like "Go to village Belaspur near the temple and find Hari Jena" with no accurate GPS pin or impassable road warnings.
- **Pain Point 2: Connectivity Blackouts**: Inability to log completed rescue actions or request backup because mobile internet towers collapsed in the coastal surge.
- **Pain Point 3: Unacknowledged Action**: Field volunteers risk their lives but have no standardized digital medium to log their actions and get official confirmation.

### D. Citizen / Evacuee
- **Pain Point 1: The "Black Hole" of SOS Calls**: Dialing a helpline, waiting in queue, giving details, and then having zero visibility into whether rescue is coming.
- **Pain Point 2: Language & Literacy Barriers**: Complex text-heavy portals that are unreadable to rural elders who communicate best in spoken Odia.
- **Pain Point 3: Misinformation on Shelter Safety**: Not knowing which cyclone shelter is safe, which one is already packed to capacity, and whether dry rations are available.

---

## 7. Proposed Solution: The AapadaOps Operational Architecture

AapadaOps implements a **5-Stage Operational Pipeline**:

```
+---------------------------------------------------------------------------------+
|                        THE AAPADAOPS 5-STAGE PIPELINE                           |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  [STAGE 1: MULTI-CHANNEL INTAKE]                                                |
|  - Web SOS Portal (Odia / English) with GPS auto-detection                      |
|  - Field Officer Quick-Entry Form (Offline-capable)                             |
|  - DEOC Helpline (1077) Operator Rapid-Log Interface                            |
|                                                                                 |
|                                    v                                            |
|                                                                                 |
|  [STAGE 2: AI TRIAGE, EXTRACTION & DEDUPLICATION]                              |
|  - Entity Extraction: People stranded, water height, medical emergencies        |
|  - Severity Index Scoring (Priority 1: Life Threat to Priority 4: Advisory)     |
|  - Spatial-Temporal Clustering: Groups duplicate reports within 250m radius     |
|                                                                                 |
|                                    v                                            |
|                                                                                 |
|  [STAGE 3: VERIFICATION & ADMINISTRATIVE TASKING]                               |
|  - BDO / DEOC Dashboard presents deduplicated cluster with evidence             |
|  - Cross-verification against GIS flood layers & local Aapda Mitra check-in     |
|  - One-click transformation of verified incident into an Administrative Task    |
|                                                                                 |
|                                    v                                            |
|                                                                                 |
|  [STAGE 4: TACTICAL DISPATCH & RESOURCE TRACKING]                               |
|  - Matching task requirement to nearest available tactical unit (ODRAF/OFES)   |
|  - Turn-by-turn flood-safe dispatch route display                               |
|  - Real-time unit state updates: Dispatched -> On Scene -> Completed            |
|                                                                                 |
|                                    v                                            |
|                                                                                 |
|  [STAGE 5: RESOLUTION, CITIZEN FEEDBACK & AUDIT]                                |
|  - Automated SMS/Status update delivered to reporting citizen                   |
|  - Immutable tamper-evident audit record appended for SDRF compliance           |
|  - Auto-compiled district & state SitRep metrics updated instantly              |
+---------------------------------------------------------------------------------+
```

---

## 8. Functional Requirements (FR)

### Module 1: Ingestion & Incident Intake
- **FR-1.1**: The system shall provide a bilingual (Odia and English) citizen SOS reporting interface requiring minimal input (Location, Category, Severity, Stranded Count, Photo/Voice).
- **FR-1.2**: The system shall automatically capture browser/device GPS coordinates with user consent or allow manual map pin placement within Odisha state bounds.
- **FR-1.3**: The system shall provide an internal Operator Fast-Intake Form for 1077/1070 helpline personnel to log incoming telephone reports within 30 seconds.
- **FR-1.4**: The system shall support offline caching of field reports using local storage/IndexedDB, automatically syncing once network connectivity resumes.

### Module 2: AI Triage & Deduplication Engine
- **FR-2.1**: The system shall analyze incoming incident descriptions (Odia & English) and extract key distress entities: hazard type, stranded count, vulnerable individuals (infants, elderly, pregnant women), water height, and structural damage.
- **FR-2.2**: The system shall calculate an automated Urgency Score (Critical, High, Medium, Low) based on vulnerability markers and reported life-safety risk.
- **FR-2.3**: The system shall execute spatial-temporal clustering (DBSCAN / Haversine distance threshold $\le 250$m within a 2-hour window) to group redundant reports into a single Parent Incident with linked child submissions.

### Module 3: Verification & Administrative Task Dispatch
- **FR-3.1**: The system shall present block and district officers with a Verification Queue displaying unverified incident clusters alongside satellite/flood hazard map overlays.
- **FR-3.2**: The system shall allow authorized officials (BDO, Tahasildar, DEOC Operator) to verify, reject, or request field-volunteer re-check of an incident.
- **FR-3.3**: The system shall convert verified incidents into formal Actionable Tasks with assigned agency, priority, required equipment, and SLA deadline.
- **FR-3.4**: The system shall assign tasks to specific operational units (e.g. ODRAF Unit 04, Fire Station Nimapara) and provide automated status tracking (Assigned, Dispatched, On-Site, Resolved).

### Module 4: Cyclone Shelter & Relief Logistics
- **FR-4.1**: The system shall maintain real-time capacity and occupancy metrics for all registered Multi-Purpose Cyclone Shelters (MCS) and Flood Shelters.
- **FR-4.2**: The system shall monitor critical shelter lifelines: drinking water supply (liters), dry rations (days remaining), DG set diesel fuel (operating hours), and medical kit readiness.
- **FR-4.3**: The system shall trigger visual warnings when shelter capacity exceeds 90% or when water/ration supplies dip below a 48-hour threshold.

### Module 5: Early Warning & CAP Broadcast
- **FR-5.1**: The system shall ingest and display meteorological warning bulletins categorized into standard 4-tier alert levels (Green, Yellow, Orange, Red).
- **FR-5.2**: The system shall allow State/District EOC directors to compose and broadcast targeted evacuation notices to specific districts, blocks, or coastal kilometer buffer bands.

### Module 6: Executive Command & SitRep Compilation
- **FR-6.1**: The system shall render a high-density, real-time command dashboard showing total active incidents, verified tasks, deployed tactical units, evacuated population, and shelter occupancy.
- **FR-6.2**: The system shall generate one-click standardized Situation Reports (SitReps) in printable/exportable format compliant with OSDMA and NDMA reporting standards.

---

## 9. Non-Functional Requirements (NFR)

- **NFR-1 (Performance & Latency)**: REST API responses for geospatial queries and dashboard metrics shall return within $\le 300$ms under normal load; spatial clustering of 1,000 active reports shall complete in $\le 1.5$ seconds.
- **NFR-2 (Design Integrity & Usability)**: The UI must strictly follow government operations styling (sober neutral slate canvas, restrained governance green, standard alert tiers, practical tables). Zero purple gradients, zero glowing effects, zero glassmorphism, zero generic AI illustrations. System must meet WCAG 2.1 Level AA contrast guidelines.
- **NFR-3 (Offline Resilience)**: The field reporting module must function seamlessly without internet connectivity, storing queued reports securely in local browser storage and synchronizing automatically upon reconnection.
- **NFR-4 (Security & Privacy)**: Zero hardcoded credentials; strict JWT role-based access control; citizen telephone numbers and personal identifying information (PII) must be masked in public views and visible only to verified operational officers.
- **NFR-5 (Data Integrity & PostGIS Standard)**: All geospatial entities shall be stored using standard WGS 84 (SRID 4326) geometry types; coordinates outside the geographical bounding box of Odisha ($17.78^\circ\text{N} - 22.57^\circ\text{N}$, $81.37^\circ\text{E} - 87.53^\circ\text{E}$) shall be flagged or rejected.
- **NFR-6 (Auditability)**: All operational decisions, task dispatches, status changes, and shelter resource deductions shall be logged to an append-only audit table with UTC timestamp and operator ID.

---

## 10. Risks, Assumptions and Limitations

### Verified Findings (Grounded in Official Documentation & Reality)
1. **Verified**: OSDMA’s SATARK and EWDS systems are primarily top-down alert dissemination and scientific forecasting tools; they do not provide a bidirectional citizen incident-to-dispatch workflow.
2. **Verified**: ODRN provides a static directory of equipment, but lacks dynamic operational state tracking during an unfolding crisis.
3. **Verified**: During major cyclones, cell towers in coastal blocks fail, making offline-capable caching and low-bandwidth web architectures mandatory.
4. **Verified**: Over 800 Multi-Purpose Cyclone Shelters exist across coastal Odisha with established CSMMC local management structures.
5. **Verified**: The administrative command chain strictly follows State EOC (SRC/OSDMA) $\to$ District Collector (DDMA) $\to$ BDO/Tahasildar $\to$ Grassroots (RI, Sarpanch, Aapda Mitra).

### Assumptions Requiring Future User / Field Interviews
1. **Assumption A**: BDOs and DEOC operators are willing to use a web-based triage dashboard during active landfall rather than relying solely on telephone notes. *(Requires field interview with DEOC operators)*.
2. **Assumption B**: Aapda Mitra volunteers possess smartphones with updated browsers capable of running Progressive Web Apps in field conditions. *(Requires validation across varied Gram Panchayats)*.
3. **Assumption C**: Automated spatial clustering with a 250m radius is optimal across both dense coastal villages and sparse interior tribal hamlets. *(Requires empirical tuning)*.

### System Limitations & Edge Cases
- **Cell Tower Total Collapse**: In a Category 5 Super Cyclone where all terrestrial cellular infrastructure is wiped out (as occurred in 1999 and parts of Puri during Fani), AapadaOps web clients cannot transmit data until satellite terminals (SBMDV) or emergency DMR radio bridges are connected.
- **Geocoding Inaccuracies**: In rural hamlets, GPS errors on low-cost smartphones can drift up to 50–100 meters, requiring human-in-the-loop verification before heavy rescue machinery is dispatched.

---

## 11. Project Scope for Hackathon MVP

To deliver a genuinely functional, robust, and tested platform within the project timeframe, the scope is clearly delineated:

### In Scope for Hackathon MVP
1. **Core EOC Operations Dashboard**: High-density situational command overview with real-time KPI metrics, active alerts, and situation timeline.
2. **Interactive PostGIS Disaster Map**: Multi-layer GIS canvas with Odisha district boundaries, coastal flood zones, Multi-Purpose Cyclone Shelters, and live incident markers.
3. **Citizen SOS & Intake Module**: Bilingual (Odia + English) responsive reporting interface with auto-GPS capture and emergency category tagging.
4. **Automated Triage & Deduplication Engine**: Backend algorithmic clustering of duplicate reports within geographical proximity, with entity extraction and priority scoring.
5. **Administrative Verification & Task Dispatch Board**: BDO/Collector interface to verify incident clusters, assign tasks to tactical units (ODRAF/Fire Services), and track dispatch lifecycle.
6. **Cyclone Shelter & Logistics Manager**: Real-time capacity monitoring and lifeline supply tracking (water, food, fuel) for representative coastal shelters across Puri, Jagatsinghpur, and Kendrapara.
7. **Early Warning Alert Publisher**: CAP-compliant alert composer and multi-tier hazard broadcast view.
8. **Automated Situation Report (SitRep) Generator**: One-click exportable operational summary for state/district leadership.

### Out of Scope / Features to Postpone
- **Direct Telecom SMS Gateway Carrier Binding**: Real-world telecom DLT registration requires government nodal officer approvals; will use clearly identified simulated SMS dispatch logs.
- **Live IMD / CWC Radar API Ingestion**: Direct government API tokens require institutional MOUs; will use high-fidelity historical/synthetic cyclone track feeds based on actual Cyclone Fani/Dana trajectories.
- **Automated Drone Imagery Computer Vision**: Heavy deep learning processing of high-resolution aerial footage deferred to post-MVP roadmap.
- **Civilian Voluntary Blood Donor Matching**: Non-critical feature deferred to post-disaster recovery phase.

