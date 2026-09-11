import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def migrate_columns():
    async with AsyncSessionLocal() as db:
        print("Migrating businesses table for Phase 3 columns...")
        await db.execute(text("ALTER TABLE businesses ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITH TIME ZONE;"))
        await db.execute(text("ALTER TABLE businesses ADD COLUMN IF NOT EXISTS verification_summary JSON;"))
        await db.commit()
        print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate_columns())
