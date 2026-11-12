# AapadaOps System Architecture Documentation

## 1. Architectural Style & C4 Container Architecture

AapadaOps is structured as a resilient, modular, human-governed distributed system designed for zero-downtime operation during regional disaster crises.

### C4 Level 2 Container Diagram
```
+------------------------------------------------------------------------+
|                             CLIENT TIER                                |
|  - Citizen SOS Portal (React 18 PWA, Vernacular Odia/English)         |
|  - EOC Command Cockpit (React 18 + Leaflet GIS + Shadcn UI)            |
|  - Field Worker PWA (Offline-first local cache + High contrast)        |
+------------------------------------------------------------------------+
                                    | HTTPS / WSS
+------------------------------------------------------------------------+
|                          EDGE & GATEWAY TIER                           |
|  - Nginx 1.25 Alpine: SSL Termination, HTTP Security Headers, Reverse  |
|    Proxying (/api/v1, /ws), Rate Limiting, Static Asset Gzip Caching   |
+------------------------------------------------------------------------+
                                    |
+------------------------------------------------------------------------+
|                       APPLICATION & AI SERVICES TIER                   |
|  - FastAPI (Python 3.11): Async REST API, OpenAPI Schemas              |
|  - AI Advisory Engine: Bilingual Odia/En Parser (Sub-ms Latency)       |
|  - Deduplication Engine: Spatial Haversine + Token Overlap             |
|  - Prioritization Engine: OSDMA 7-Factor Rubric (0 to 100)             |
|  - Coordination Optimizer: Google OR-Tools CBC MIP Solver              |
|  - Audit Ledger: SHA-256 HMAC Signatures & Tamper-Evident History      |
+------------------------------------------------------------------------+
                                    |
+------------------------------------------------------------------------+
|                       DATA & PERSISTENCE TIER                          |
|  - PostgreSQL 16 + PostGIS 3.4: Spatial Indexing (GIST), GeoJSON       |
|  - Redis 7: Real-time Telemetry, WebSocket State, Rate-Limiting Cache  |
|  - Object Storage: Magic-byte Inspected SHA-256 Hashed Evidence Store  |
+------------------------------------------------------------------------+
```

## 2. Core Subsystems

### A. Bilingual Natural Language Understanding
- Parses Odia Unicode (`\u0b00-\u0b7f`) and English disaster reports in under 1 ms.
- Maps colloquial regional expressions to 10 standardized disaster categories (`EMBANKMENT_BREACH`, `FLOOD`, `CYCLONE_WIND`, `TREE_FALL`, `ROAD_BLOCK`, `STRANDED_PERSONS`, `POWER_FAILURE`, `SHELTER_DEMAND`, `MEDICAL_EMERGENCY`, `OTHER`).
- Enforces strict Pydantic schema validation. Unmentioned fields default to `None` without fabrication.

### B. Spatial-Temporal Deduplication
- Runs Haversine distance clustering ($\le 500\text{m}$ to $2000\text{m}$) within a 24-hour window.
- Computes token overlap and text similarity.
- Surfaces potential duplicates side-by-side with spatial delta maps to Incident Verification Officers (IVOs).
- **Hard Guardrail:** Autonomous merging is strictly forbidden.

### C. Explainable 7-Factor Prioritization Rubric
- Computes deterministic score (0–100) reflecting OSDMA operational doctrine:
  1. Base Severity Weight (up to 40 pts)
  2. Human Life Stranded Impact (up to 20 pts)
  3. Dynamic Hazard Multiplier (up to 15 pts)
  4. Medical Emergency Factor (up to 10 pts)
  5. District Riverine/Coastal Vulnerability Tier (up to 10 pts)
  6. Submerged Road Accessibility Bonus (up to 5 pts)
- 100% of mathematical points are auditable by Commanders.

### D. Operations-Research Resource Optimization
- Formulates a Mixed-Integer Linear Program (MIP) solved via Google OR-Tools.
- Evaluates approach road speeds, amphibious boat staging delays, troop capacities, and medical specializations.
- Prevents resource double-booking via atomic SQL transaction locks.

### E. Statutory Command Authority
- Military (NDRF), paramilitary, and civil-defense (ODRAF, Fire Services) mobilizations require digital authorization from a verified human Response Coordinator.
- AI is strictly advisory; automated dispatch is physically impossible within the API layer.
