# AapadaOps — REST API Specification (v1)

Base URL: `/api/v1`

All responses follow standard HTTP status conventions and return JSON. Authenticated endpoints require a `Bearer <token>` HTTP header.

---

## 1. Authentication & System (`/auth`, `/system`)

### `POST /auth/login`
- **Description**: Authenticate operations officer, district collector, or field responder.
- **Request Body**:
  ```json
  {
    "username": "officer@osdma.gov.in",
    "password": "SecurePassword123"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in_minutes": 120,
    "user": {
      "id": "usr_01",
      "username": "officer@osdma.gov.in",
      "name": "S. K. Mohapatra",
      "role": "STATE_EOC_DIRECTOR",
      "district": null
    }
  }
  ```

### `GET /auth/me`
- **Description**: Return current authenticated profile.

---

## 2. Emergency Alerts & Early Warnings (`/alerts`)

### `GET /alerts`
- **Query Params**: `severity` (GREEN|YELLOW|ORANGE|RED), `district`, `hazard_type` (CYCLONE|FLOOD|HEATWAVE|LANDSLIDE), `active_only` (bool)
- **Response (200 OK)**:
  ```json
  [
    {
      "id": "alt_fani_01",
      "hazard_type": "CYCLONE",
      "title": "Severe Cyclonic Storm Alert — Landfall Anticipated Near Puri",
      "severity": "RED",
      "affected_districts": ["Puri", "Jagatsinghpur", "Kendrapara", "Ganjam"],
      "effective_from": "2026-11-12T06:00:00Z",
      "expires_at": "2026-11-14T18:00:00Z",
      "wind_speed_kmph": 175,
      "rainfall_forecast_mm": 240,
      "instructions_en": "Mandatory evacuation of all kutcha houses within 5 km of coast to nearest MCS.",
      "instructions_or": "ଉପକୂଳର ୫ କିଲୋମିଟର ମଧ୍ୟରେ ଥିବା ସମସ୍ତ କଞ୍ଚା ଘରର ବାସିନ୍ଦା ନିକଟସ୍ଥ ବାତ୍ୟା ଆଶ୍ରୟସ୍ଥଳୀକୁ ଯାଆନ୍ତୁ ।",
      "created_at": "2026-11-11T20:00:00Z"
    }
  ]
  ```

### `POST /alerts`
- **Authorization**: `STATE_EOC_DIRECTOR` or `SUPER_ADMIN`
- **Description**: Broadcast new official CAP-compliant alert to field networks.

---

## 3. Incident Intake & Citizen SOS (`/incidents`)

### `GET /incidents`
- **Query Params**: `status` (REPORTED|VERIFIED|DISPATCHED|RESOLVED), `district`, `priority` (LOW|MEDIUM|HIGH|CRITICAL)
- **Response (200 OK)**: Paginated incident collection.

### `POST /incidents`
- **Description**: Submit citizen SOS or field incident report.
- **Request Body**:
  ```json
  {
    "caller_name": "Prakash Nayak",
    "caller_phone": "+919876543210",
    "district": "Puri",
    "block": "Krushnaprasad",
    "village": "Satapada",
    "latitude": 19.6754,
    "longitude": 85.4218,
    "incident_type": "FLOOD_TRAPPED",
    "urgency": "CRITICAL",
    "persons_stranded": 14,
    "has_elderly_or_infants": true,
    "water_level_feet": 5.5,
    "description": "Rising flood waters trapped 14 people on community hall roof. Need power boat."
  }
  ```

---

## 4. Multi-Purpose Shelters & Camps (`/shelters`)

### `GET /shelters`
- **Query Params**: `district`, `is_active`, `has_vacancy`
- **Response (200 OK)**:
  ```json
  [
    {
      "id": "mcs_puri_04",
      "name": "Arakhakuda Multi-Purpose Cyclone Shelter",
      "code": "MCS-PUR-042",
      "district": "Puri",
      "block": "Krushnaprasad",
      "latitude": 19.5512,
      "longitude": 85.3421,
      "total_capacity": 1200,
      "current_occupancy": 840,
      "available_capacity": 360,
      "occupancy_rate": 0.70,
      "status": "OPERATIONAL",
      "has_dg_set": true,
      "dg_fuel_hours": 36,
      "water_supply_litres": 8500,
      "dry_rations_days": 4,
      "contact_person": "Manoj Kumar Jena",
      "contact_phone": "+919437012345"
    }
  ]
  ```

---

## 5. Tactical Resources & Logistics (`/resources`)

### `GET /resources`
- **Query Params**: `category` (RESCUE_BOAT|DEWATERING_PUMP|TREE_CUTTER|DG_SET|RELIEF_KITS), `status` (AVAILABLE|DEPLOYED|MAINTENANCE), `location_district`

### `POST /resources/dispatch`
- **Authorization**: `STATE_EOC_DIRECTOR`, `DISTRICT_COLLECTOR`
- **Description**: Dispatch tactical rescue resources to an incident or activated shelter.

---

## 6. AI/ML Geospatial Risk & Analytics (`/analytics`)

### `GET /analytics/flood-risk-index`
- **Query Params**: `basin` (Mahanadi|Brahmani|Baitarani), `rainfall_scenario_mm`
- **Description**: Returns computed inundation susceptibility score and high-risk village list.

### `GET /analytics/cyclone-vulnerability`
- **Query Params**: `district`, `wind_speed_kmph`
- **Description**: Machine learning damage prediction categorized by housing vulnerability (kutcha vs pucca).

### `GET /analytics/eoc-summary`
- **Description**: Real-time aggregated KPI metrics for executive overview dashboard.

