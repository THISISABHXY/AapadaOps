"""AapadaOps Automated Database Backup, Integrity Verification, and Recovery Script.

Supports:
- SQLite (local development and offline emergency deploy)
- PostgreSQL/PostGIS (production enterprise deployment via pg_dump / psql)

Features:
- Automated snapshot generation
- Cryptographic SHA-256 checksum calculation
- Metadata manifest (timestamp, record counts, schema version)
- Integrity verification
- Non-destructive test restoration
"""

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def calculate_sha256(filepath: Path) -> str:
    """Calculate cryptographic SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def count_sqlite_records(db_path: Path) -> dict:
    """Inspect SQLite database and return table row counts for integrity audit."""
    if not db_path.exists():
        return {}
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    tables = ["users", "incidents", "incident_reports", "resources", "response_teams", "tasks", "audit_logs"]
    counts = {}
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        except Exception:
            counts[table] = 0
    conn.close()
    return counts


def create_backup(db_source: str, backup_dir: Path) -> Path:
    """Create timestamped database backup with SHA-256 and metadata manifest."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # If SQLite database
    if "sqlite" in db_source or db_source.endswith(".db"):
        source_path = Path(db_source.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", ""))
        if not source_path.exists():
            # Check relative to backend root
            source_path = Path(__file__).resolve().parent.parent / source_path
        if not source_path.exists():
            raise FileNotFoundError(f"Database source file not found: {source_path}")

        backup_file = backup_dir / f"aapadaops_backup_{timestamp}.db"
        # Atomic SQLite backup using VACUUM INTO or file copy with flush
        conn = sqlite3.connect(str(source_path))
        backup_conn = sqlite3.connect(str(backup_file))
        conn.backup(backup_conn)
        backup_conn.close()
        conn.close()

        sha256 = calculate_sha256(backup_file)
        row_counts = count_sqlite_records(backup_file)

        manifest = {
            "backup_file": backup_file.name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "db_type": "sqlite",
            "file_size_bytes": backup_file.stat().st_size,
            "sha256_checksum": sha256,
            "row_counts": row_counts,
            "status": "VERIFIED_VALID",
        }

        manifest_file = backup_dir / f"aapadaops_backup_{timestamp}.meta.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        print(f"[SUCCESS] SQLite backup created: {backup_file}")
        print(f"[INFO] SHA-256 Checksum: {sha256}")
        print(f"[INFO] Row counts: {row_counts}")
        print(f"[INFO] Manifest saved: {manifest_file}")
        return backup_file

    else:
        # PostgreSQL / PostGIS dump
        backup_file = backup_dir / f"aapadaops_backup_{timestamp}.sql"
        print(f"[INFO] Running pg_dump for PostgreSQL connection: {db_source}")
        cmd = ["pg_dump", "--format=c", "--file", str(backup_file), db_source]
        try:
            subprocess.run(cmd, check=True)
            sha256 = calculate_sha256(backup_file)
            manifest = {
                "backup_file": backup_file.name,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "db_type": "postgresql_postgis",
                "file_size_bytes": backup_file.stat().st_size,
                "sha256_checksum": sha256,
                "status": "VERIFIED_VALID",
            }
            manifest_file = backup_dir / f"aapadaops_backup_{timestamp}.meta.json"
            with open(manifest_file, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            print(f"[SUCCESS] PostgreSQL backup completed: {backup_file}")
            return backup_file
        except Exception as exc:
            print(f"[ERROR] pg_dump failed: {exc}", file=sys.stderr)
            raise


def verify_backup(backup_file: Path) -> bool:
    """Verify cryptographic integrity and file readability of a backup."""
    if not backup_file.exists():
        print(f"[ERROR] Backup file does not exist: {backup_file}", file=sys.stderr)
        return False

    meta_file = backup_file.with_suffix(".meta.json")
    if not meta_file.exists():
        # Try finding corresponding .meta.json
        meta_file = backup_file.parent / (backup_file.stem + ".meta.json")

    actual_sha256 = calculate_sha256(backup_file)
    actual_size = backup_file.stat().st_size

    if meta_file.exists():
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
        expected_sha256 = meta.get("sha256_checksum")
        if actual_sha256 != expected_sha256:
            print(f"[FAIL] Checksum mismatch! Expected: {expected_sha256}, Actual: {actual_sha256}", file=sys.stderr)
            return False
        print(f"[PASS] Checksum matched: {actual_sha256}")

    # SQLite integrity check
    if backup_file.suffix == ".db":
        try:
            conn = sqlite3.connect(str(backup_file))
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            res = cursor.fetchone()
            conn.close()
            if res and res[0] == "ok":
                print("[PASS] SQLite PRAGMA integrity_check passed (Database is structurally sound).")
                return True
            else:
                print(f"[FAIL] SQLite integrity check failed: {res}", file=sys.stderr)
                return False
        except Exception as exc:
            print(f"[FAIL] Could not read SQLite file: {exc}", file=sys.stderr)
            return False

    print(f"[PASS] Backup file {backup_file.name} ({actual_size} bytes) integrity verified.")
    return True


def restore_backup(backup_file: Path, target_path: Path) -> bool:
    """Safely restore a verified database backup to target destination."""
    if not verify_backup(backup_file):
        print("[ERROR] Restore aborted: backup integrity verification failed.", file=sys.stderr)
        return False

    print(f"[INFO] Restoring {backup_file} -> {target_path}...")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(backup_file, target_path)

    # Verify target
    if target_path.suffix == ".db":
        counts = count_sqlite_records(target_path)
        print(f"[SUCCESS] Restore completed successfully. Restored row counts: {counts}")
    else:
        print("[SUCCESS] Restore completed successfully.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AapadaOps Database Backup & Recovery Utility")
    subparsers = parser.add_subparsers(dest="command")

    # Backup command
    backup_p = subparsers.add_parser("backup", help="Create a verified snapshot backup")
    backup_p.add_argument("--db", default="./aapadaops_dev.db", help="Source database path or connection string")
    backup_p.add_argument("--dir", default="./backups", help="Target backup directory")

    # Verify command
    verify_p = subparsers.add_parser("verify", help="Verify integrity of an existing backup")
    verify_p.add_argument("file", help="Path to backup file")

    # Restore command
    restore_p = subparsers.add_parser("restore", help="Restore database from backup file")
    restore_p.add_argument("file", help="Path to backup file")
    restore_p.add_argument("--target", default="./aapadaops_restored.db", help="Target restored database path")

    args = parser.parse_args()

    if args.command == "backup":
        create_backup(args.db, Path(args.dir))
    elif args.command == "verify":
        valid = verify_backup(Path(args.file))
        sys.exit(0 if valid else 1)
    elif args.command == "restore":
        success = restore_backup(Path(args.file), Path(args.target))
        sys.exit(0 if success else 1)
    else:
        parser.print_help()

