import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent.parent / "aapadaops_dev.db"
print(f"Reading DB at: {db_path} (exists: {db_path.exists()})")

con = sqlite3.connect(db_path)
cur = con.cursor()
tables = [t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"Tables ({len(tables)}): {tables}")

for t in ["users", "districts", "incidents", "response_teams", "resources", "cyclone_shelters", "tasks", "duplicate_clusters"]:
    if t in tables:
        count = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f" - {t}: {count} rows")
