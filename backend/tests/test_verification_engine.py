import uuid
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.models.business import Business, SourceRecord
from app.models.digital_presence import Website, Contact
from app.models.enums import LifecycleStatus, VerificationCheckType, VerificationResultStatus, EvidenceType
from app.models.verification import VerificationResult, Evidence
from app.services.website_verifier import WebsiteVerifier
from app.services.contact_verifier import ContactVerifier
from app.services.social_verifier import SocialVerifier
from app.services.verification_engine import VerificationEngine


@pytest.mark.asyncio
async def test_website_verifier_not_found():
    """Verifies WebsiteVerifier returns NOT_FOUND when website URL is missing."""
    verifier = WebsiteVerifier()
    res = await verifier.verify_website(None, "Test Business")
    assert res["reachable"] is False
    assert len(res["results"]) == 1
    assert res["results"][0]["check_type"] == VerificationCheckType.WEBSITE_REACHABILITY
    assert res["results"][0]["result"] == VerificationResultStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_contact_verifier_phone_and_email_validation():
    """Verifies ContactVerifier phone normalization, email domain matching, and missing contact handling."""
    verifier = ContactVerifier()
    
    # Valid phone & email with matching domain
    res = verifier.verify_contacts(
        phone="+1 (212) 555-0199",
        emails=["contact@acmedental.com"],
        source_records_data=[{"source_name": "google_places", "raw_data": {"phone": "+1 (212) 555-0199"}}],
        website_domain="acmedental.com"
    )
    
    assert res["has_conflicts"] is False
    assert any(r["check_type"] == VerificationCheckType.CONTACT_PHONE_VALIDITY and r["result"] == VerificationResultStatus.PASS for r in res["results"])
    assert any(r["check_type"] == VerificationCheckType.CONTACT_EMAIL_DOMAIN_MATCH and r["result"] == VerificationResultStatus.PASS for r in res["results"])


@pytest.mark.asyncio
async def test_contact_verifier_conflict_detection():
    """Verifies ContactVerifier flags CONFLICT status when sources disagree on phone numbers."""
    verifier = ContactVerifier()
    
    source_records = [
        {"source_name": "google_places", "raw_data": {"phone": "+1 (212) 555-0199"}},
        {"source_name": "yelp", "raw_data": {"phone": "+1 (212) 999-8877"}},
    ]
    
    res = verifier.verify_contacts(
        phone="+1 (212) 555-0199",
        emails=[],
        source_records_data=source_records,
        website_domain=None
    )
    
    assert res["has_conflicts"] is True
    assert len(res["conflicts"]) == 1
    assert any(r["result"] == VerificationResultStatus.CONFLICT for r in res["results"])


@pytest.mark.asyncio
async def test_social_verifier_not_found():
    """Verifies SocialVerifier returns NOT_FOUND when no social links exist."""
    verifier = SocialVerifier()
    res = await verifier.verify_social({}, "Test Business")
    assert res["social_count"] == 0
    assert res["results"][0]["result"] == VerificationResultStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_master_verification_engine_pass(async_session: async_sessionmaker):
    """Verifies master VerificationEngine runs check suites and updates Business lifecycle status."""
    uid = uuid.uuid4().hex[:8]
    async with async_session() as db:
        b = Business(
            name=f"Verified Dental Studio {uid}",
            normalized_name=f"verified dental studio {uid}",
            category="Dentist",
            address="100 Main St, New York, NY",
            city="New York",
            phone="+12125550199",
            lifecycle_status=LifecycleStatus.DISCOVERED,
        )
        db.add(b)
        await db.commit()
        await db.refresh(b)

        # Add SourceRecord
        sr = SourceRecord(
            business_id=b.id,
            source_name="google_places",
            source_identifier=f"place_{uid}",
            raw_data={"name": b.name, "address": b.address, "phone": b.phone},
            observed_at=datetime.now(timezone.utc),
        )
        db.add(sr)
        await db.commit()

        engine = VerificationEngine()
        res = await engine.verify_business(db, b.id)

        assert res["business_id"] == str(b.id)
        assert res["lifecycle_status"] in ["VERIFIED", "REVERIFY_REQUIRED", "HUMAN_REVIEW"]
        assert "summary" in res

        # Re-fetch from DB
        stmt = select(Business).where(Business.id == b.id)
        r = await db.execute(stmt)
        updated_b = r.scalar_one()
        assert updated_b.verified_at is not None
        assert updated_b.verification_summary is not None
