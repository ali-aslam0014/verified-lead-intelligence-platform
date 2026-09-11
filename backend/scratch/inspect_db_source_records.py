import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.target import TargetRun, Target
from app.models.business import Business, SourceRecord

async def main():
    async with AsyncSessionLocal() as db:
        # 1. Fetch Target runs
        target_id = "f8ced3c2-4afc-47a2-a395-ef8aafd3ebf2"
        stmt = select(TargetRun).where(TargetRun.target_id == target_id)
        runs = (await db.execute(stmt)).scalars().all()
        print(f"--- Target {target_id} Runs ---")
        run_ids = []
        for r in runs:
            print(f"Run ID: {r.id} | Status: {r.status} | Discovered: {r.total_discovered} | Verified: {r.total_verified} | Error Log: {r.error_log}")
            run_ids.append(r.id)

        # 2. Check SourceRecords
        sr_stmt = select(SourceRecord).where(SourceRecord.target_run_id.in_(run_ids))
        srs = (await db.execute(sr_stmt)).scalars().all()
        print(f"\n--- Source Records for Target Runs: {len(srs)} ---")
        for sr in srs:
            print(f"SR ID: {sr.id} | Business ID: {sr.business_id} | Source: {sr.source_name} | Name: {sr.raw_data.get('name')}")

        # 3. Check all SourceRecords in DB
        all_srs = (await db.execute(select(SourceRecord))).scalars().all()
        print(f"\n--- Total Source Records in DB: {len(all_srs)} ---")
        for sr in all_srs[:10]:
            print(f"SR ID: {sr.id} | TargetRunID: {sr.target_run_id} | Business ID: {sr.business_id} | Name: {sr.raw_data.get('name')}")

if __name__ == "__main__":
    asyncio.run(main())
