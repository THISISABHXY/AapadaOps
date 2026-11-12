# AapadaOps REST API Specification

**Base URL:** `/api/v1`  
**Authentication:** HTTP Bearer JWT (`Authorization: Bearer <token>`)  
**Specification Standard:** OpenAPI 3.1.0 / JSON

---

## 1. Authentication & Users
- `POST /auth/login`: Form-encoded username/password login; returns JWT access token.
- `GET /auth/me`: Current authenticated user profile, assigned district, and statutory role permissions.
- `POST /users/`: Create user (SuperAdmin / DistrictAdmin only).
- `GET /users/`: List users with pagination and district filtering.

## 2. Incidents & SOS Intake
- `POST /incidents/`: Ingest new incident report. Automatically masks citizen phone number under DPDP Act 2023.
- `GET /incidents/`: List incidents with status, severity, district, and spatial bounding-box filters.
- `GET /incidents/{id}`: Detailed incident view including audio, reports, and evidence links.
- `PATCH /incidents/{id}/status`: Statutory state transition (`VERIFIED`, `PRIORITIZED`, `ASSIGNED`, `CLOSED`).

## 3. AI Advisory & Natural Language Processing
- `POST /ai/parse-report`: Sub-millisecond bilingual Odia and English report parser. Returns category, severity, stranded count, medical flags, and confidence.
- `POST /ai/transcribe-voice`: Bilingual speech-to-text transcription with low-confidence flagging.
- `POST /ai/detect-duplicates`: Combined Haversine and semantic text deduplication analysis.

## 4. Verification & Duplicate Management
- `GET /duplicates/candidates/{incident_id}`: Surfaces candidate duplicates within spatial-temporal radius.
- `POST /verification/verify`: Incident Verification Officer confirmation, marking genuine or duplicate.

## 5. Tactical Coordination & Resource Optimization
- `POST /coordination/optimize`: Mixed-Integer Linear Program (Google OR-Tools MIP). Generates multiple feasible tactical deployment strategies.
- `POST /coordination/approve`: Response Coordinator statutory sign-off. Locks resources and transitions plan to `APPROVED`.
- `POST /coordination/acknowledge`: Tactical unit acknowledgment of mobilization order.
- `POST /coordination/progress-update`: Unit status updates (`EN_ROUTE`, `AT_SCENE`).
- `POST /coordination/evidence`: Upload and seal post-mission verification proof (validates binary magic bytes and records SHA-256 hash).
- `POST /coordination/close`: Incident closure and resource release back to `AVAILABLE`.

## 6. Shelters & Logistics
- `GET /shelters/`: List operational cyclone shelters with occupancy, capacity, and supply status.
- `PATCH /shelters/{id}/occupancy`: Increment or decrement shelter occupancy during evacuations.

## 7. Common Alerting Protocol (CAP) & Broadcasts
- `GET /alerts/active`: Retrieve active multi-channel early warning alerts.
- `POST /alerts/broadcast`: Issue official Red/Orange/Yellow alert broadcast (District Admin / Super Admin only).

## 8. Audit & Legal Compliance
- `GET /audit-logs/`: Stream tamper-evident audit events with actor, timestamp, and HMAC metadata.

## 9. Real-Time WebSockets
- `WS /ws/incidents`: Real-time push updates for new incidents, priority recalculations, and status changes.
- `WS /ws/coordination`: Live tactical team location updates and plan progression.
