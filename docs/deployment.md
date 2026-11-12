# AapadaOps Production Deployment & Operations Runbook

## 1. Hosting Architecture & Prerequisites

### Infrastructure Requirements
- **OS:** Linux (Ubuntu 22.04 LTS / Debian 12 recommended) or Windows Server
- **CPU:** 4 vCPUs (x86_64 or ARM64)
- **RAM:** 8 GB minimum (16 GB recommended for high concurrent incident load)
- **Disk:** 50 GB NVMe SSD with automated hourly snapshotting
- **Docker Engine:** Version 24.0+ with Docker Compose v2

---

## 2. Docker Compose Multi-Container Orchestration

The complete stack is defined in `docker-compose.yml`:
1. `postgis`: PostgreSQL 16 with PostGIS 3.4 spatial extensions and persistent volume.
2. `redis`: Redis 7 Alpine for high-speed cache, rate limiting, and WebSocket synchronization.
3. `backend`: FastAPI Python 3.11 Debian-slim container with GDAL, GEOS, and 4 Uvicorn workers running under non-root `appuser`.
4. `frontend`: Multi-stage Alpine container serving the React 18 SPA via Nginx, handling reverse proxying to the backend and terminating SSL.

### Starting the Production Stack
```bash
# 1. Clone repository
git clone <repository_url>
cd aapadaops

# 2. Configure environment secrets
cp .env.example .env
# Edit .env with strong production passwords and SECRET_KEY

# 3. Build and launch all services in detached mode
docker-compose up --build -d

# 4. Verify running container health
docker-compose ps
```

---

## 3. Production Verification Checklist

Run the automated 10-point verification script to confirm end-to-end operational health:
```bash
python backend/scripts/verify_production_deployment.py
```

The script verifies:
1. Frontend SPA loads with HTTP 200.
2. Defensive HTTP security headers (`nosniff`, `DENY`, `HSTS`) are active.
3. Backend liveness and readiness endpoints return `LIVE` and `READY`.
4. PostGIS database connection succeeds.
5. JWT authentication and role-based permissions function.
6. Incident record creation persists correctly.
7. File upload binary magic-byte inspection succeeds.
8. AI advisory service parses bilingual reports.
9. WebSocket real-time channel is responsive.
10. Zero hardcoded secrets exposed in logs or endpoints.

---

## 4. Zero-Downtime Rolling Upgrades & Database Migrations

### Applying Database Migrations
```bash
# Run Alembic migrations inside the running backend container
docker-compose exec backend alembic upgrade head
```

### Rolling Deployment
```bash
# Rebuild containers with new image version
docker-compose build --pull

# Perform rolling restart of services without downtime
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend
```

---

## 5. Disaster Recovery & Database Backup Runbook

### Automated Daily Backup
The system includes an automated backup script `backend/scripts/backup_restore.py`:
```bash
# Create an encrypted, compressed database snapshot
python backend/scripts/backup_restore.py backup --db-url <DATABASE_URL> --out-dir /var/backups/aapadaops/
```

### Restoring from Backup (< 60 Seconds RTO)
```bash
# Restore snapshot into clean PostgreSQL instance
python backend/scripts/backup_restore.py restore --snapshot-file /var/backups/aapadaops/snapshot_latest.tar.gz --db-url <DATABASE_URL>
```
