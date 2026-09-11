import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def migrate_verification_schema():
    async with AsyncSessionLocal() as db:
        print("Migrating verification_results table & enums...")
        
        # 1. Add columns to verification_results
        await db.execute(text("ALTER TABLE verification_results ADD COLUMN IF NOT EXISTS confidence FLOAT DEFAULT 1.0;"))
        await db.execute(text("ALTER TABLE verification_results ADD COLUMN IF NOT EXISTS reason VARCHAR(500);"))
        
        # 2. Add enum values to verification_result_status_enum
        new_result_statuses = ["NOT_FOUND", "ERROR"]
        for status in new_result_statuses:
            try:
                await db.execute(text(f"ALTER TYPE verification_result_status_enum ADD VALUE IF NOT EXISTS '{status}';"))
            except Exception as e:
                print(f"Enum status {status} notice: {e}")

        # 3. Add enum values to verification_check_type_enum
        new_check_types = [
            "WEBSITE_REACHABILITY",
            "HTTPS_AVAILABILITY",
            "DOMAIN_RESOLVES",
            "ROBOTS_TXT_ACCESSIBLE",
            "SITEMAP_ACCESSIBLE",
            "CONTENT_IDENTITY_MATCH",
            "CONTACT_PHONE_VALIDITY",
            "CONTACT_EMAIL_SYNTAX",
            "CONTACT_EMAIL_DOMAIN_MATCH",
            "SOCIAL_REACHABILITY",
            "IDENTITY_CONSISTENCY",
        ]
        for ct in new_check_types:
            try:
                await db.execute(text(f"ALTER TYPE verification_check_type_enum ADD VALUE IF NOT EXISTS '{ct}';"))
            except Exception as e:
                print(f"Enum check_type {ct} notice: {e}")

        await db.commit()
        print("Verification schema migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate_verification_schema())
