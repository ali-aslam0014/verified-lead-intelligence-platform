import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def migrate_opportunity_columns():
    async with AsyncSessionLocal() as db:
        print("Migrating opportunities table columns for Phase 4...")
        await db.execute(text("ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'CONFIRMED';"))
        await db.execute(text("ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'HIGH';"))
        await db.execute(text("ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS evidence_ids JSON DEFAULT '{}';"))
        await db.execute(text("ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS recommended_angle VARCHAR(1000);"))
        await db.commit()
        print("Opportunities table migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate_opportunity_columns())
