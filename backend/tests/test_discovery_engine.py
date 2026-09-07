import uuid
import pytest
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.sources.base import DiscoveryRequest, RawDiscoveryResult
from app.sources.google_places import GooglePlacesAdapter, GooglePlacesAPIError
from app.sources.website_enrichment import WebsiteEnrichmentAdapter
from app.services.resolver import BusinessResolver
from app.models.business import Business, SourceRecord
from app.models.digital_presence import Website
from app.models.enums import LifecycleStatus, WebsiteStatus
from app.models.target import Target, TargetRun
from app.models.enums import TargetStatus, TargetRunStatus
from app.tasks.discovery import execute_discovery_run_async


@pytest.mark.asyncio
async def test_google_places_adapter_missing_key_raises_error():
    """Verifies strict real-data mandate: missing Google Maps API key raises GooglePlacesAPIError."""
    adapter = GooglePlacesAdapter()
    req = DiscoveryRequest(niche="Dental Clinics", geography="Austin, TX")
    
    # Executing without API key in settings raises error
    with pytest.raises(GooglePlacesAPIError) as exc_info:
        await adapter.search(req)
    assert "Google Places API Key is missing" in str(exc_info.value)


@pytest.mark.asyncio
async def test_business_resolver_normalization():
    """Verifies BusinessResolver title, phone, and domain normalization helper functions."""
    assert BusinessResolver.normalize_name("Austin Dental Clinic, LLC") == "austin dental clinic"
    assert BusinessResolver.normalize_name("Apex Solar Services Inc.") == "apex solar"
    assert BusinessResolver.normalize_phone("(512) 555-0199") == "+15125550199"
    assert BusinessResolver.normalize_domain("https://www.austindental.com/contact/") == "austindental.com"


@pytest.mark.asyncio
async def test_business_resolver_tier1_matching(async_session: async_sessionmaker):
    """Verifies Tier 1 deterministic matching (exact place_id, phone, or domain)."""
    resolver = BusinessResolver()
    uid = uuid.uuid4().hex[:8]
    test_phone = f"+1512{uuid.uuid4().int % 10000000:07d}"
    test_domain = f"austindentalcenter-{uid}.com"

    async with async_session() as db:
        # Raw discovery record 1
        raw_res_1 = RawDiscoveryResult(
            source_name="google_places",
            source_identifier=f"place_{uid}_1",
            raw_data={
                "name": f"Austin Dental Center {uid} LLC",
                "address": f"{uid} Main St, Austin, TX",
                "phone": test_phone,
                "website": f"https://www.{test_domain}",
                "primary_type": "Dental Clinic",
            },
            observed_at=datetime.now(timezone.utc),
        )

        b1, is_new_1 = await resolver.resolve_record(db, raw_res_1)
        await db.commit()

        assert is_new_1 is True
        assert b1.name == f"Austin Dental Center {uid} LLC"
        assert b1.lifecycle_status == LifecycleStatus.DISCOVERED
        assert b1.phone == test_phone

        # Raw discovery record 2 (Same domain & phone, different place_id)
        raw_res_2 = RawDiscoveryResult(
            source_name="google_places",
            source_identifier=f"place_{uid}_2",
            raw_data={
                "name": f"Austin Dental Center {uid}",
                "address": f"{uid} Main Street, Suite 5, Austin, TX",
                "phone": test_phone,
                "website": f"https://{test_domain}",
                "primary_type": "Dental Clinic",
            },
            observed_at=datetime.now(timezone.utc),
        )

        b2, is_new_2 = await resolver.resolve_record(db, raw_res_2)
        await db.commit()

        assert is_new_2 is False
        assert b2.id == b1.id # Merged into same canonical Business entity!


@pytest.mark.asyncio
async def test_business_resolver_tier3_isolation(async_session: async_sessionmaker):
    """Verifies Tier 3 isolation logic: ambiguous name+city without matching street/phone/domain creates separate entities."""
    resolver = BusinessResolver()
    uid1 = uuid.uuid4().hex[:8]
    uid2 = uuid.uuid4().hex[:8]
    city_name = f"City_{uid1}"

    async with async_session() as db:
        raw_res_1 = RawDiscoveryResult(
            source_name="google_places",
            source_identifier=f"place_{uid1}",
            raw_data={
                "name": f"ABC Dental {uid1}",
                "address": "10 Broadway",
                "city": city_name,
                "phone": f"+1212{uuid.uuid4().int % 10000000:07d}",
                "website": f"https://abcdentalny-{uid1}.com",
            },
            observed_at=datetime.now(timezone.utc),
        )
        b1, is_new_1 = await resolver.resolve_record(db, raw_res_1)
        await db.commit()
        assert is_new_1 is True

        # Different business with same generic name in same city but completely different address/phone/domain
        raw_res_2 = RawDiscoveryResult(
            source_name="google_places",
            source_identifier=f"place_{uid2}",
            raw_data={
                "name": f"ABC Dental {uid2}",
                "address": "900 5th Ave",
                "city": city_name,
                "phone": f"+1212{uuid.uuid4().int % 10000000:07d}",
                "website": f"https://abcdental5th-{uid2}.com",
            },
            observed_at=datetime.now(timezone.utc),
        )
        b2, is_new_2 = await resolver.resolve_record(db, raw_res_2)
        await db.commit()

        assert is_new_2 is True
        assert b2.id != b1.id # NOT merged automatically!


@pytest.mark.asyncio
async def test_discovery_run_worker_failed_state_when_no_api_key(async_session: async_sessionmaker):
    """Verifies discovery worker updates TargetRun to FAILED status when GOOGLE_MAPS_API_KEY is missing."""
    async with async_session() as db:
        target = Target(
            name="Test API Failure Campaign",
            niche="HVAC Services",
            geography="Denver, CO",
            status=TargetStatus.ACTIVE,
            filters={},
            opportunity_types=["NEW_WEBSITE"],
            source_configuration={"enabled_sources": ["google_places"]},
        )
        db.add(target)
        await db.commit()

        target_run = TargetRun(
            target_id=target.id,
            status=TargetRunStatus.QUEUED,
            total_discovered=0,
            total_verified=0,
            error_log={},
        )
        db.add(target_run)
        await db.commit()
        run_id = target_run.id

    # Execute discovery run worker
    res = await execute_discovery_run_async(run_id)

    assert res["status"] == "FAILED"
    assert "Google Places API Key is missing" in res["error"]

    async with async_session() as db:
        # Re-fetch target run from DB
        stmt = select(TargetRun).where(TargetRun.id == run_id)
        r = await db.execute(stmt)
        tr = r.scalar_one()
        assert tr.status == TargetRunStatus.FAILED
        assert tr.error_log["error_type"] == "GooglePlacesAPIError"
