import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

print("Importing app.core.database...", flush=True)
from app.core.database import AsyncSessionLocal, engine
print("Importing app.db.init_db...", flush=True)
from app.db.init_db import seed_database

async def main():
    print(f"Connecting to database via engine {engine.url}...", flush=True)
    async with AsyncSessionLocal() as session:
        print("Starting seed_database(session)...", flush=True)
        await seed_database(session)
        print("seed_database returned!", flush=True)
    print("Disposing engine...", flush=True)
    await engine.dispose()
    print("All done!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
