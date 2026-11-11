import asyncio
import sys
from pathlib import Path

# Fix Windows ProactorEventLoop hang with aiosqlite/threads
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import AsyncSessionLocal, engine
from sqlalchemy import select
from app.models.district import District

async def run():
    print("Opening session...", flush=True)
    async with AsyncSessionLocal() as session:
        print("Checking districts...", flush=True)
        dist_check = await session.execute(select(District).limit(1))
        print("District query result:", dist_check.scalar_one_or_none(), flush=True)
    print("Disposing engine...", flush=True)
    await engine.dispose()
    print("Done!", flush=True)

asyncio.run(run())
