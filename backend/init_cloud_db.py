import asyncio
from app.core.database import engine
from app.models.base import Base
import app.models  # Force registry of all SQLAlchemy models in Base.metadata

async def main():
    print("Creating all tables on Neon Cloud PostgreSQL...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created! Verified tables in metadata:", list(Base.metadata.tables.keys()))

if __name__ == "__main__":
    asyncio.run(main())
