# AapadaOps (ଆପଦାଅପ୍ସ) — Production Deployment & Operations Manual

**Document Version:** 1.0.0-PROD  
**Target Platform:** Odisha State Disaster Management Authority (OSDMA) & State Emergency Operations Center (EOC)  
**Classification:** Official Disaster-Management Infrastructure Documentation  
**Primary Data Center:** Odisha State Data Centre (SDC), OCAC Building, Bhubaneswar  
**Disaster Recovery (DR) Site:** Sambalpur Secondary Data Centre (Western Odisha)

---

## 1. System Architecture Overview

AapadaOps is architected as an enterprise, containerized, multi-tiered disaster-response platform designed for high availability during severe natural hazards (Category 4/5 Bay of Bengal cyclones, Mahanadi basin floods, and storm surges):

```
                                  [ Citizen / Public / Field Workers / EOC Officers ]
                                                           │
                                                           ▼ (HTTPS / TLS 1.3)
                                            ┌───────────────────────────────┐
                                            │ Cloudflare Edge / NIC WAF     │
                                            │ DDoS Defense & Rate Limiting  │
                                            └──────────────┬────────────────┘
                                                           │
                                   ┌───────────────────────┴───────────────────────┐
                                   ▼                                               ▼
                    ┌───────────────────────────────┐               ┌───────────────────────────────┐
                    │ Nginx Frontend Reverse Proxy  │               │ Nginx Frontend Reverse Proxy  │
                    │ Node 1 (Bhubaneswar SDC)      │               │ Node 2 (Bhubaneswar SDC)      │
                    │ Port 80/443 (SPA Static Dist) │               │ Port 80/443 (SPA Static Dist) │
                    └──────────────┬────────────────┘               └───────────────┬───────────────┘
                                   │ (/api/ & /ws/ proxy pass)                      │
                                   └───────────────────────┬────────────────────────┘
                                                           │
                                                           ▼
                                            ┌───────────────────────────────┐
                                            │ FastAPI Async Backend Clustered│
                                            │ 4x Uvicorn Async Workers      │
                                            │ Port 8000 (Internal Bridge)   │
                                            └───────┬───────────────┬───────┘
                                                    │               │
                            ┌───────────────────────┘               └───────────────────────┐
                            ▼                                                               ▼
            ┌───────────────────────────────┐                               ┌───────────────────────────────┐
            │ PostgreSQL 16 + PostGIS 3.4   │◄──(Streaming Replication)───► │ Secondary Hot Standby DB      │
            │ Primary Master (Bhubaneswar)  │                               │ DR Site (Sambalpur)           │
            │ Port 5432 (NVMe, WAL Archive) │                               │ Port 5432 (Automatic Failover)│
            └───────────────┬───────────────┘                               └───────────────────────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │ Redis 7 Distributed Pub/Sub   │
            │ WebSocket State & Rate Limits │
            └───────────────────────────────┘
```

---

## 2. Infrastructure & Hosting Provider Analysis

### Tier 1: Government Sovereign Target (Recommended for Official State Operations)
- **Primary Hosting:** Odisha State Data Centre (SDC) / National Informatics Centre (NIC) MeghRaj Cloud.
- **Compute:** Dual active-passive bare-metal or KVM virtual machines running Red Hat Enterprise Linux 9 or Ubuntu 22.04 LTS.
- **Database:** Dedicated PostgreSQL 16 server with PostGIS 3.4, `postgis_topology`, and `fuzzystrmatch` extensions enabled on dedicated NVMe block storage with write-ahead log (WAL) archiving.
- **Storage:** S3-compatible on-premise MinIO storage cluster with server-side AES-256 encryption for incident evidence (photos, voice recordings, damage certificates).
- **Compliance:** 100% data residency within Odisha; compliant with Indian Digital Personal Data Protection (DPDP) Act 2023 and CERT-In National Cyber Security Guidelines.

### Tier 2: Managed Cloud PaaS (For Rapid Regional / Staging / Hybrid Deployments)
- **Frontend:** Vercel / Cloudflare Pages / AWS S3 + CloudFront (Edge global distribution, instant HTTPS, automatic Brotli compression).
- **Backend:** Google Cloud Run / Render / Railway container running `backend/Dockerfile` with horizontal auto-scaling (1 to 20 instances) triggered by request concurrency.
- **Database:** Supabase / Neon / AWS RDS for PostgreSQL with PostGIS extension enabled (`CREATE EXTENSION postgis;`).
- **Object Storage:** Cloudflare R2 (zero egress fees) or AWS S3 with pre-signed upload URLs.
- **Cache/Messaging:** Upstash Redis or AWS ElastiCache for Redis.

---

## 3. Environment Secrets & Configuration

All environment configurations are managed through `.env` (derived from [`.env.example`](file:///c:/Users/Pg706/OneDrive/Desktop/PROTOTYPE%20PROJECT/.env.example)).

> [!CAUTION]
> **CRITICAL SECURITY RULE:** Never commit the `.env` file, database passwords, or JWT secret keys to source control. In production, inject secrets exclusively through the cloud provider's encrypted environment variable store or HashiCorp Vault.

### Generating Production Cryptographic Keys
```bash
# Generate 64-character high-entropy secret key for JWT signing
openssl rand -hex 32

# Generate strong database password
openssl rand -base64 24
```

### Key Configuration Variables

| Variable | Production Recommendation | Description |
| :--- | :--- | :--- |
| `APP_ENV` | `production` | Enables production hardening and disables public Swagger docs |
| `SECRET_KEY` | 64-char random hex string | Used for HS256 JWT signature verification |
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@db:5432/aapadaops` | Async PostgreSQL + PostGIS connection string |
| `REDIS_URL` | `redis://:pass@redis:6379/0` | Distributed WebSocket broker & sliding-window rate limit store |
| `BACKEND_CORS_ORIGINS` | `["https://aapadaops.osdma.gov.in"]` | Whitelisted frontend domains |
| `UPLOAD_DIR` | `/app/uploads` | Isolated file directory for validated evidence files |
| `MAX_FILE_SIZE_BYTES` | `15728640` (15 MB) | Strict upper boundary on file uploads |
| `AI_CONFIDENCE_THRESHOLD` | `0.60` | Threshold below which reports trigger mandatory officer review |

---

## 4. Production Deployment Methods

### Method A: Single-Host Docker Compose (Turnkey VM Deployment)

1. **Clone repository and configure environment:**
   ```bash
   git clone https://github.com/osdma-odisha/aapadaops.git /opt/aapadaops
   cd /opt/aapadaops
   cp .env.example .env
   chmod 600 .env
   # Edit .env with secure production values
   nano .env
   ```

2. **Verify test suite passes before deployment:**
   ```bash
   pytest backend/tests/ -v
   ```

3. **Build and launch containerized services:**
   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

4. **Verify container health:**
   ```bash
   docker compose ps
   docker compose logs -f backend
   ```

5. **Execute post-deployment verification script:**
   ```bash
   python backend/scripts/verify_production_deployment.py
   ```

---

### Method B: Kubernetes / OpenShift (Multi-Node State Data Centre Cluster)

For high-availability clustered deployments at Bhubaneswar SDC:

1. **Deploy PostGIS Persistent Volume Claims & StatefulSet:**
   ```bash
   kubectl apply -f k8s/postgres-statefulset.yaml
   ```

2. **Deploy Redis Cluster:**
   ```bash
   kubectl apply -f k8s/redis-deployment.yaml
   ```

3. **Deploy Backend Deployment & Horizontal Pod Autoscaler (HPA):**
   ```bash
   kubectl apply -f k8s/backend-deployment.yaml
   kubectl apply -f k8s/backend-hpa.yaml
   ```

4. **Deploy Frontend Nginx Deployment & Ingress Controller:**
   ```bash
   kubectl apply -f k8s/frontend-deployment.yaml
   kubectl apply -f k8s/ingress-tls.yaml
   ```

---

## 5. Database Migrations & Reference Data

Alembic manages all schema revisions. Migrations are executed automatically upon container startup or via the CLI:

```bash
# Check current migration revision
alembic current

# Apply pending schema migrations
alembic upgrade head

# Verify PostGIS geometry columns and spatial indices
python backend/scripts/inspect_db.py
```

---

## 6. Automated Backup & Disaster Recovery (DR)

The platform provides [backend/scripts/backup_restore.py](file:///c:/Users/Pg706/OneDrive/Desktop/PROTOTYPE%20PROJECT/backend/scripts/backup_restore.py) for scheduled snapshots, cryptographic checksum validation, and test restoration.

### Automated Nightly Backup Cron
Add the following entry to `/etc/cron.d/aapadaops-backup`:
```cron
# Run daily database snapshot at 02:00 UTC
0 2 * * * root /opt/aapadaops/.venv/bin/python /opt/aapadaops/backend/scripts/backup_restore.py backup --db /opt/aapadaops/backend/aapadaops_dev.db --dir /var/backups/aapadaops >> /var/log/aapadaops_backup.log 2>&1
```

### Verifying a Backup Checksum
```bash
python backend/scripts/backup_restore.py verify /var/backups/aapadaops/aapadaops_backup_20261112_072111.db
```

### Emergency Database Restoration
```bash
python backend/scripts/backup_restore.py restore /var/backups/aapadaops/aapadaops_backup_20261112_072111.db --target /opt/aapadaops/backend/aapadaops_restored.db
```

---

## 7. Zero-Downtime Rolling Update & Rollback Runbook

### Rolling Update Procedure (Blue/Green or Rolling Container Replacement)

When publishing a new release:
1. GitHub Actions executes tests and builds new Docker images tagged with the commit SHA (`ghcr.io/osdma/backend:sha-XXXX`).
2. Pull new container images:
   ```bash
   docker compose pull backend frontend
   ```
3. Run Alembic migrations:
   ```bash
   docker compose run --rm backend alembic upgrade head
   ```
4. Restart services with zero downtime:
   ```bash
   docker compose up -d --no-deps --build backend frontend
   ```

### Emergency Rollback Instructions (< 60 Seconds)

If a critical fault or degradation is detected post-deployment:

#### 1. Container Rollback
```bash
# Option 1: Revert to previous Docker image tag in docker-compose.yml
sed -i 's/backend:latest/backend:v1.0.0-PREV/g' docker-compose.yml
docker compose up -d backend frontend

# Option 2: Git checkout previous known-good release commit
git checkout v1.0.0-STABLE
docker compose up -d --build
```

#### 2. Database Schema Rollback
```bash
# Downgrade schema by exactly 1 revision
docker compose exec backend alembic downgrade -1

# Or downgrade to specific known-good migration hash
docker compose exec backend alembic downgrade 49aad46cabbc
```

#### 3. Database Snapshot Restoration (Worst-Case Corruption)
```bash
# 1. Stop backend container to prevent incoming writes
docker compose stop backend

# 2. Restore verified snapshot
python backend/scripts/backup_restore.py restore /var/backups/aapadaops/LATEST_VERIFIED.db --target /opt/aapadaops/backend/aapadaops_dev.db

# 3. Restart backend
docker compose start backend
```

---

## 8. Monitoring, Logging & Observability

- **Liveness Probe:** `GET /health/live` (Checks if HTTP process is responsive)
- **Readiness Probe:** `GET /health/ready` (Validates database connection and operational state)
- **Structured JSON Logging:** Logs output to stdout in standardized format suitable for FluentBit / Promtail / CloudWatch / Vector ingestion.
- **Log Sanitation:** Sensitive headers (`Authorization: Bearer ...`) and reporter contact details are masked in standard log outputs.

