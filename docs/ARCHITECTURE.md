# AapadaOps — Master System Architecture Specification

## 1. System Overview
**AapadaOps** is an end-to-end AI-powered disaster-response coordination platform purpose-built for the State of Odisha. Developed to support the **Odisha State Disaster Management Authority (OSDMA)**, the **Special Relief Commissioner (SRC)**, and District Emergency Operations Centers (DEOCs), it coordinates multi-hazard disaster preparedness, real-time response, resource dispatch, and post-disaster recovery across all 30 districts of Odisha.

---

## 2. High-Level Architecture (C4 Model)

```
+---------------------------------------------------------------------------------+
|                               PRESENTATION TIER                                 |
|                                                                                 |
|   +------------------------------------+   +--------------------------------+   |
|   |   State & District EOC Console     |   |    Field Responder PWA         |   |
|   |   (React 18 + TS + Tailwind + GIS) |   |    (Offline-First Sync, GPS)   |   |
|   +-----------------+------------------+   +---------------+----------------+   |
+---------------------|--------------------------------------|--------------------+
                      | HTTPS / WSS                          |
                      v                                      v
+---------------------------------------------------------------------------------+
|                             API & APPLICATION GATEWAY                           |
|                                                                                 |
|   FastAPI Core Engine (Python 3.11)                                             |
|   - OAuth2 / JWT Auth & RBAC (Role-Based Access Control)                         |
|   - GeoJSON REST Endpoints & Geospatial Spatial Filtering                      |
|   - Real-time Alert Broadcast & WebSockets Push                                 |
|   - Audit Logging & Compliance Trails                                           |
+---------------------+-----------------------------------------------------------+
                      |
        +-------------+-------------+---------------------+
        |                           |                     |
        v                           v                     v
+--------------------+    +--------------------+    +--------------------+
|   BUSINESS LOGIC   |    |  SPATIAL & AI/ML   |    | EXTERNAL SERVICES  |
|   SERVICES         |    |  INTELLIGENCE      |    | INTEGRATION        |
|                    |    |                    |    |                    |
| - Incident Intake  |    | - Flood Risk Index |    | - IMD Weather API  |
| - Shelter Logistics|    | - Cyclone Damage   |    | - CWC River Gauges |
| - Resource Dispatch|    | - Triage NLP (Odia)|    | - OSRM Routing     |
| - Task Board       |    | - Demand Forecast  |    | - SMS / CAP Alert  |
+---------+----------+    +---------+----------+    +---------+----------+
          |                         |                         |
          +-------------------------+-------------------------+
                                    |
                                    v
+---------------------------------------------------------------------------------+
|                              PERSISTENCE TIER                                   |
|                                                                                 |
|   +------------------------------------+   +--------------------------------+   |
|   | PostgreSQL 16 + PostGIS Spatial    |   | Redis 7 (Optional / Streaming) |   |
|   | - Incidents, Shelters, Geometries  |   | - Session Caching              |   |
|   | - Spatial indexes (GIST)           |   | - Broadcast Subscriptions      |   |
|   +------------------------------------+   +--------------------------------+   |
+---------------------------------------------------------------------------------+
```

---

## 3. Core Functional Modules

### Module 1: Unified Emergency Operations Center (EOC) Command Dashboard
- High-density operational overview tailored for state and district disaster commissioners.
- Real-time status gauges: Active Disasters, Evacuated Citizens, Open Shelters, Deployed ODRAF/NDRF Teams, Pending SOS Reports.
- Live incident telemetry and situation timeline.

### Module 2: Interactive Geospatial GIS Console
- PostGIS-powered multi-layer map:
  - Cyclone Track & Cone of Uncertainty (IMD format)
  - Flood Inundation Zones (Mahanadi, Brahmani, Baitarani basins)
  - Multi-Purpose Cyclone Shelters (MCS) with live occupancy metrics
  - Critical infrastructure overlays (Hospitals, power sub-stations, helipads, relief godowns)
  - Active rescue team locations and field incident pins.

### Module 3: Citizen SOS & Incident Intake Pipeline
- Multi-channel ingestion (Web, SMS, field surveys, emergency helpline 1070 / 1077).
- Verification & Deduplication: Automated spatial clustering of duplicate reports within 200m.
- Odia & English support for incident classification and automated severity triage.

### Module 4: Multi-Purpose Cyclone Shelter (MCS) & Relief Camp Manager
- Real-time tracking of Odisha's 800+ Cyclone and Flood Shelters.
- Capacity monitoring (Total, Occupied, Vacant, Critical threshold alerts).
- Essential inventory logistics: Dry rations (chuda/guda), drinking water (water pouches/tankers), baby food, halogen tablets, medical kits.
- Vulnerability flags: Pregnant women, lactating mothers, elderly, infants, persons with disabilities (PwD).

### Module 5: Strategic Resource Allocation & Logistics Dispatch
- Inventory depots: Central State Depot (Bhubaneswar), District Godowns, Block Points.
- Tactical assets: BAUTs (Boat Assault Universal Type) with OBMs, high-capacity dewatering pumps, inflatable lights, chainsaw tree-cutters, satellite phones.
- Unit dispatch tracking: ODRAF (Odisha Disaster Rapid Action Force), NDRF 03 Battalion Mundali, Odisha Fire & Emergency Services, Civil Defence.

### Module 6: Early Warning & Public Alert Broadcast (CAP Standard)
- Implementation of the Common Alerting Protocol (ITU-T X.1303).
- Multi-tiered alerting:
  - **Green**: Normal / Advisory
  - **Yellow**: Watch / Standby
  - **Orange**: Warning / Evacuation Preparedness
  - **Red**: Action Required / Mandatory Evacuation
- Target broadcast by administrative jurisdiction (District -> Block -> GP).

### Module 7: AI/ML Predictive Intelligence
- **Inundation Risk Model**: Topographical slope, historical flood baselines, and catchment precipitation.
- **Vulnerability & Damage Classifier**: Predictive risk based on rural housing type (kutcha vs. pucca) and wind-speed thresholds.
- **Demand Forecasting**: Machine learning projection of required food packets and water supplies for 72-hour camp isolation.

### Module 8: Audit, Compliance & Post-Disaster Loss Assessment (PDNA)
- Tamper-evident operational audit logs recording every dispatch, status change, and resource movement.
- Standardized damage assessment reporting conforming to Ministry of Home Affairs (MHA) and State Disaster Response Fund (SDRF) norms.

---

## 4. Role-Based Access Control (RBAC) Matrix

| Role | Scope | Key Permissions |
|------|-------|-----------------|
| `SUPER_ADMIN` | Statewide | System configuration, user management, audit review |
| `STATE_EOC_DIRECTOR` | Statewide | State alert broadcast, inter-district resource mobilization, ODRAF/NDRF dispatch |
| `DISTRICT_COLLECTOR` | District-wide | District declaration, evacuation orders, shelter activation, local resource allocation |
| `BLOCK_DEVELOPMENT_OFFICER` | Block-wide | GP level monitoring, relief camp logistics, field team assignment |
| `FIELD_RESPONDER` | Assigned Sector | Incident status updates, SOS verification, GPS check-in, shelter headcount |
| `CITIZEN` | Public | Submit SOS incident, view public warnings, locate nearest safe shelter |
