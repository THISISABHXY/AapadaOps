# AapadaOps Security, Privacy & Compliance Architecture

## 1. Compliance with Digital Personal Data Protection (DPDP) Act 2023

1. **Citizen PII Masking on Ingestion:**
   - Incoming citizen and field reporter telephone numbers are masked at the API boundary (e.g., `+91 94370 81234` is transformed to `+91 94370 XXXXX`).
   - Unprivileged users (including Public Observers, Field Workers, and unauthenticated clients) can only view the masked identifier.
   - Access to unmasked phone numbers is strictly limited to authorized Incident Verification Officers (IVOs) and District Administrators on duty, with each unmasking action generating an immutable audit log entry.
2. **Right to Correction & Data Minimization:**
   - Incident records collect strictly operational emergency data (location, number of stranded individuals, immediate medical requirements). No extraneous personal profiling attributes are requested or retained.

---

## 2. Cryptographic Authentication & RBAC

1. **Password Hashing:**
   - Uses **Argon2id** (`argon2_cffi`), following OWASP recommended memory and time cost parameters.
2. **Session Security:**
   - Stateless JWT tokens signed with SHA-256 HMAC (`HS256`).
   - Expiration strictly set to 60 minutes with sliding refresh.
3. **Role-Based Access Control (RBAC):**
   - 7 distinct roles with strict principle of least privilege:
     - `SUPER_ADMIN`: Cross-district policy and system administration.
     - `DISTRICT_ADMIN`: District-level command and resource requisition.
     - `VERIFICATION_OFFICER`: Incident verification and deduplication decisions.
     - `COORDINATOR`: Tactical force allocation and dispatch approval.
     - `FIELD_WORKER`: Mission acknowledgment, status progression, and evidence submission.
     - `OBSERVER`: Read-only situational monitoring with sanitized telemetry.
     - `CITIZEN`: SOS report submission and ticket status tracking.

---

## 3. Evidence Integrity & File Upload Hardening

1. **Binary Magic-Byte Inspection:**
   - Uploaded files are inspected for real binary header bytes rather than trusting MIME headers or extensions:
     - JPEG: `\xFF\xD8\xFF`
     - PNG: `\x89PNG\r\n\x1a\n`
     - PDF: `%PDF-`
     - WAV: `RIFF....WAVE`
     - WebP: `RIFF....WEBP`
2. **Prohibited File Types:**
   - Script files, binaries, and executables (`.exe`, `.sh`, `.py`, `.php`, `.bat`, `.cmd`, `.vbs`, `.js`) are rejected with an immediate 400 Bad Request.
3. **Path Traversal Sanitization:**
   - Filenames are strictly sanitized to prevent directory traversal attacks (`../` and null bytes).
4. **File Size Hard Limits:**
   - Hard capped at 15.0 MB per upload.
5. **SHA-256 Cryptographic Sealing:**
   - Every stored evidence asset generates an SHA-256 cryptographic digest that is stored in the database and audit ledger to guarantee tamper-evident integrity.

---

## 4. Network Hardening & HTTP Defensive Headers

Production deployments running behind Nginx enforce defensive HTTP security headers:
- `X-Content-Type-Options: nosniff` (Prevents MIME-sniffing)
- `X-Frame-Options: DENY` (Mitigates clickjacking)
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (Enforces HTTPS)
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'; img-src 'self' data: https://*.tile.openstreetmap.org; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self' ws: wss:;`

---

## 5. Rate Limiting & Denial-of-Service Defense

- Public SOS Intake: 60 requests per minute per IP.
- Authentication Endpoint (`/api/v1/auth/login`): 30 requests per minute per IP.
- Enforced via SlowAPI in-memory or Redis-backed token-bucket algorithms.

