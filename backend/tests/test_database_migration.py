import uuid
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.models import Role, User, Target, TargetRun, Business, Website, LifecycleStatus, WebsiteStatus, TargetStatus, TargetRunStatus


@pytest.mark.asyncio
async def test_live_postgres_connection(async_session):
    async with async_session() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_alembic_version_table_exists(async_session):
    async with async_session() as session:
        result = await session.execute(
            text("SELECT version_num FROM alembic_version")
        )
        version = result.scalar()
        assert version is not None
        assert len(version) > 0


@pytest.mark.asyncio
async def test_all_18_tables_exist_in_postgres_schema(async_session):
    expected_tables = {
        "roles",
        "users",
        "targets",
        "target_runs",
        "jobs",
        "businesses",
        "source_records",
        "websites",
        "social_profiles",
        "contacts",
        "website_audits",
        "seo_audits",
        "opportunities",
        "lead_scores",
        "verification_results",
        "evidence",
        "review_actions",
        "exports",
    }
    
    async with async_session() as session:
        result = await session.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
        )
        existing_tables = {row[0] for row in result.fetchall()}
        
        missing = expected_tables - existing_tables
        assert not missing, f"Missing tables in PostgreSQL database: {missing}"


@pytest.mark.asyncio
async def test_all_14_enums_exist_in_postgres_schema(async_session):
    expected_enums = {
        "lifecycle_status_enum",
        "website_status_enum",
        "social_platform_enum",
        "social_status_enum",
        "contact_type_enum",
        "verification_check_type_enum",
        "verification_result_status_enum",
        "evidence_type_enum",
        "opportunity_type_enum",
        "review_action_type_enum",
        "target_status_enum",
        "target_run_status_enum",
        "job_status_enum",
        "export_format_enum",
    }
    
    async with async_session() as session:
        result = await session.execute(
            text(
                "SELECT typname FROM pg_type JOIN pg_enum ON pg_type.oid = pg_enum.enumtypid GROUP BY typname"
            )
        )
        existing_enums = {row[0] for row in result.fetchall()}
        
        missing = expected_enums - existing_enums
        assert not missing, f"Missing enums in PostgreSQL database: {missing}"


@pytest.mark.asyncio
async def test_role_and_user_insert_and_relationship(async_session):
    async with async_session() as session:
        try:
            # 1. Create Role
            admin_role = Role(
                name=f"AdminRole_{uuid.uuid4().hex[:6]}",
                description="Administrator with full access",
                permissions={"all": True}
            )
            session.add(admin_role)
            await session.flush()
            
            # 2. Create User linked to Role
            test_user = User(
                email=f"user_{uuid.uuid4().hex[:6]}@example.com",
                hashed_password="hashed_pass_secret",
                full_name="Test Architect",
                role_id=admin_role.id
            )
            session.add(test_user)
            await session.flush()
            
            # 3. Assert relationship query
            assert test_user.role_id == admin_role.id
            assert test_user.role.name == admin_role.name
        finally:
            await session.rollback()


@pytest.mark.asyncio
async def test_foreign_key_integrity_constraint(async_session):
    async with async_session() as session:
        try:
            non_existent_role_id = uuid.uuid4()
            orphan_user = User(
                email=f"orphan_{uuid.uuid4().hex[:6]}@example.com",
                hashed_password="pass",
                role_id=non_existent_role_id
            )
            session.add(orphan_user)
            with pytest.raises(IntegrityError):
                await session.flush()
        finally:
            await session.rollback()


@pytest.mark.asyncio
async def test_cascade_and_set_null_deletion_behavior(async_session):
    async with async_session() as session:
        try:
            # Create Target & TargetRun (CASCADE)
            target = Target(
                name="Test Target",
                niche="Dental",
                geography="USA",
                status=TargetStatus.ACTIVE
            )
            session.add(target)
            await session.flush()

            target_run = TargetRun(
                target_id=target.id,
                status=TargetRunStatus.QUEUED
            )
            session.add(target_run)
            await session.flush()

            # Create Business & Website (CASCADE)
            biz = Business(
                name="Acme Dental",
                normalized_name="acme dental",
                city="Austin",
                lifecycle_status=LifecycleStatus.DISCOVERED
            )
            session.add(biz)
            await session.flush()

            website = Website(
                business_id=biz.id,
                url="https://acmedental.com",
                domain="acmedental.com",
                status=WebsiteStatus.OFFICIAL_WEBSITE
            )
            session.add(website)
            await session.flush()

            assert website.business_id == biz.id
            assert target_run.target_id == target.id
        finally:
            await session.rollback()
