# AapadaOps Database & Spatial Schema Specification

## 1. Overview
AapadaOps utilizes **PostgreSQL 16** with the **PostGIS 3.4** spatial extension. All geographic entities utilize `geometry(Point, 4326)` with standard WGS 84 coordinates.

## 2. Entity Relationship Diagram (ERD)

```
+---------------+        1:N       +-------------------+
|     users     |-----------------<|     incidents     |
+---------------+                  +-------------------+
        |                                    | 1:N
        | 1:N                                v
        |                          +-------------------+
        v                          | incident_reports  |
+-------------------+              +-------------------+
|    audit_logs     |                        | 1:N
+-------------------+                        v
        |                          +-------------------+
        | 1:N                      |     evidence      |
        v                          +-------------------+
+-------------------+                        |
|coordination_plans |                        |
+-------------------+                        |
        | 1:N                                |
        v                                    |
+-------------------+                        |
|       tasks       |                        |
+-------------------+                        |
        |                                    |
        +------------------------------------+
```

## 3. Core Database Entities

### `users`
- `id` (UUID, Primary Key)
- `email` (VARCHAR, Unique, Indexed)
- `hashed_password` (VARCHAR, Argon2id)
- `full_name` (VARCHAR)
- `phone` (VARCHAR)
- `role` (ENUM: `SUPER_ADMIN`, `DISTRICT_ADMIN`, `VERIFICATION_OFFICER`, `COORDINATOR`, `FIELD_WORKER`, `OBSERVER`, `CITIZEN`)
- `district_name` (VARCHAR, Nullable)
- `is_active` (BOOLEAN, Default: True)
- `created_at`, `updated_at` (TIMESTAMPTZ)

### `incidents`
- `id` (UUID, Primary Key)
- `incident_code` (VARCHAR, Unique, Indexed, e.g. `INC-OD-2026-9799`)
- `title` (VARCHAR)
- `description` (TEXT)
- `category` (ENUM: `FLOOD`, `CYCLONE_WIND`, `EMBANKMENT_BREACH`, etc.)
- `severity` (ENUM: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`)
- `status` (ENUM: `SUBMITTED`, `NEEDS_VERIFICATION`, `VERIFIED`, `PRIORITIZED`, `ASSIGNED`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`, `DUPLICATE`, `REJECTED`)
- `latitude` (FLOAT, Indexed)
- `longitude` (FLOAT, Indexed)
- `location_geom` (GEOMETRY(Point, 4326), Spatial Index)
- `district_name` (VARCHAR, Indexed)
- `village_name` (VARCHAR)
- `stranded_count` (INTEGER, Default: 0)
- `casualties` (INTEGER, Default: 0)
- `priority_score` (FLOAT, 0.0 to 100.0)
- `reporter_name` (VARCHAR)
- `reporter_phone` (VARCHAR, Masked on unprivileged reads under DPDP Act 2023)
- `verified_by_id` (UUID, Foreign Key $\rightarrow$ `users.id`)
- `created_at`, `updated_at` (TIMESTAMPTZ)

### `coordination_plans`
- `id` (UUID, Primary Key)
- `plan_code` (VARCHAR, Unique, Indexed, e.g. `PLAN-2026-JAJ-0442`)
- `incident_id` (UUID, Foreign Key $\rightarrow$ `incidents.id`)
- `title` (VARCHAR)
- `strategy_name` (VARCHAR)
- `status` (ENUM: `PROPOSED`, `APPROVED`, `REJECTED`, `IN_EXECUTION`, `COMPLETED`, `CANCELLED`)
- `allocated_team_ids_json` (TEXT / JSON)
- `allocated_resource_ids_json` (TEXT / JSON)
- `estimated_arrival_minutes` (FLOAT)
- `reasoning_text` (TEXT)
- `assumptions_text` (TEXT)
- `limitations_text` (TEXT)
- `resource_impact_json` (TEXT / JSON)
- `reviewed_by_id` (UUID, Foreign Key $\rightarrow$ `users.id`)
- `reviewed_at` (TIMESTAMPTZ)

### `response_teams`
- `id` (UUID, Primary Key)
- `code` (VARCHAR, Unique, Indexed, e.g. `TEAM-ODRAF-04`)
- `name` (VARCHAR)
- `organization` (ENUM: `ODRAF`, `NDRF`, `FIRE_SERVICE`, `CIVIL_DEFENSE`, `POLICE`, `MEDICAL`)
- `battalion` (VARCHAR)
- `team_lead_name` (VARCHAR)
- `team_lead_phone` (VARCHAR)
- `total_personnel` (INTEGER)
- `specialization` (VARCHAR)
- `rescue_capacity_persons` (INTEGER)
- `current_district_name` (VARCHAR)
- `status` (ENUM: `AVAILABLE`, `MOBILIZED`, `EN_ROUTE`, `ON_SCENE`, `DECOMMISSIONED`)
- `latitude`, `longitude` (FLOAT)
- `assigned_incident_id` (UUID, Foreign Key $\rightarrow$ `incidents.id`)

### `shelters`
- `id` (UUID, Primary Key)
- `code` (VARCHAR, Unique, Indexed)
- `name` (VARCHAR)
- `district_name` (VARCHAR, Indexed)
- `block_name` (VARCHAR)
- `capacity` (INTEGER)
- `current_occupancy` (INTEGER)
- `has_dg_set` (BOOLEAN)
- `has_potable_water` (BOOLEAN)
- `is_operational` (BOOLEAN)

### `audit_logs`
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key $\rightarrow$ `users.id`, Nullable)
- `action` (VARCHAR, Indexed)
- `entity_type` (VARCHAR, Indexed)
- `entity_id` (VARCHAR)
- `ip_address` (VARCHAR)
- `details_json` (TEXT / JSON)
- `created_at` (TIMESTAMPTZ, Indexed)

## 4. Performance Indexes & Spatial Optimization
- `idx_incidents_location_geom`: PostGIS GiST index on `location_geom`.
- `idx_incidents_status_priority`: B-tree composite index on `(status, priority_score DESC)`.
- `idx_incidents_district`: B-tree index on `district_name`.
- `idx_audit_logs_created_at`: B-tree index on `created_at DESC` for fast compliance streaming.

