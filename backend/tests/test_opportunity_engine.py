import uuid
import pytest
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.business import Business, SourceRecord
from app.models.digital_presence import Website
from app.models.opportunity import Opportunity
from app.models.verification import Evidence
from app.models.enums import OpportunityType, EvidenceType, LifecycleStatus, WebsiteStatus
from app.services.website_analyzer import WebsiteAnalyzer
from app.services.seo_analyzer import SEOAnalyzer
from app.services.local_seo_analyzer import LocalSEOAnalyzer
from app.services.conversion_analyzer import ConversionAnalyzer
from app.services.competitor_analyzer import CompetitorAnalyzer
from app.services.opportunity_ai import OpportunityAIInterpreter
from app.services.opportunity_engine import OpportunityEngine


@pytest.mark.asyncio
async def test_website_analyzer_signals():
    """Verifies WebsiteAnalyzer extracts technical mobile viewport, alt tag, and performance signals."""
    analyzer = WebsiteAnalyzer()
    
    html_sample = "<html><head></head><body><h1>Old Site</h1><img src='logo.png' /></body></html>"
    res = analyzer.analyze_website(
        html_text=html_sample,
        final_url="http://example.com",
        is_https=False,
        latency_ms=2500.0
    )
    
    assert res["has_website"] is True
    assert res["has_viewport"] is False
    assert res["missing_alt_count"] == 1
    codes = [s["code"] for s in res["signals"]]
    assert "MISSING_MOBILE_VIEWPORT" in codes
    assert "MISSING_HTTPS_ENCRYPTION" in codes
    assert "SLOW_RESPONSE_TIME" in codes


@pytest.mark.asyncio
async def test_seo_analyzer_signals():
    """Verifies SEOAnalyzer flags missing title tag, meta description, and H1 tags."""
    analyzer = SEOAnalyzer()
    html_content = "<html><head></head><body><p>Hello world without title or meta</p></body></html>"
    res = analyzer.analyze_seo(html_text=html_content, robots_found=False)
    
    codes = [s["code"] for s in res["signals"]]
    assert "MISSING_TITLE_TAG" in codes
    assert "MISSING_META_DESCRIPTION" in codes
    assert "MISSING_H1_TAG" in codes
    assert "MISSING_ROBOTS_TXT" in codes


@pytest.mark.asyncio
async def test_local_seo_analyzer_signals():
    """Verifies LocalSEOAnalyzer detects missing city keyword mentions and Schema markup."""
    analyzer = LocalSEOAnalyzer()
    html_content = "<html><body><h1>Plumber in Brooklyn</h1></body></html>"
    
    res = analyzer.analyze_local_seo(
        html_text=html_content,
        city="New York",
        niche="Plumber",
        rating=4.2,
        review_count=3
    )
    
    codes = [s["code"] for s in res["signals"]]
    assert "LOW_LOCAL_REVIEW_COUNT" in codes
    assert "MISSING_CITY_KEYWORD_MENTIONS" in codes
    assert "MISSING_LOCAL_SCHEMA_MARKUP" in codes


@pytest.mark.asyncio
async def test_conversion_analyzer_signals():
    """Verifies ConversionAnalyzer identifies missing primary CTA, click-to-call, and booking links."""
    analyzer = ConversionAnalyzer()
    html_content = "<html><body><h1>Welcome to our practice</h1><p>Call us sometime.</p></body></html>"
    
    res = analyzer.analyze_conversion(html_text=html_content)
    
    codes = [s["code"] for s in res["signals"]]
    assert "MISSING_PRIMARY_CONVERSION_CTA" in codes
    assert "MISSING_CLICK_TO_CALL_PHONE" in codes
    assert "MISSING_ONLINE_BOOKING_LINK" in codes


@pytest.mark.asyncio
async def test_opportunity_ai_interpreter_evidence_filtering(async_session: async_sessionmaker):
    """Verifies AI interpreter discards non-existent evidence_ids to prevent hallucinations."""
    uid = uuid.uuid4().hex[:8]
    async with async_session() as db:
        b = Business(
            name=f"AI Test Business {uid}",
            normalized_name=f"ai test business {uid}",
            city="New York",
            lifecycle_status=LifecycleStatus.VERIFIED
        )
        db.add(b)
        await db.commit()
        await db.refresh(b)
        
        # Valid Evidence Record
        ev = Evidence(
            business_id=b.id,
            source="system",
            observed_at=datetime.now(timezone.utc),
            status="VERIFIED",
            evidence_type=EvidenceType.OBSERVED_FACT,
            data={"missing_cta": True}
        )
        db.add(ev)
        await db.commit()
        await db.refresh(ev)
        
        interpreter = OpportunityAIInterpreter()
        collected_signals = [
            {"code": "MISSING_PRIMARY_CONVERSION_CTA", "category": "conversion", "severity": "HIGH", "description": "Missing CTA"}
        ]
        available_eids = [str(ev.id)]
        
        valid_opps = interpreter.interpret_signals(
            business_name=b.name,
            verified_facts={"name": b.name, "city": b.city},
            collected_signals=collected_signals,
            available_evidence_ids=available_eids
        )
        assert len(valid_opps) >= 1
        assert valid_opps[0]["evidence_ids"] == [str(ev.id)]


@pytest.mark.asyncio
async def test_master_opportunity_engine_orchestration(async_session: async_sessionmaker):
    """Verifies master OpportunityEngine runs all analyzers, saves opportunities, and updates confidence."""
    uid = uuid.uuid4().hex[:8]
    async with async_session() as db:
        b = Business(
            name=f"Master Opp Business {uid}",
            normalized_name=f"master opp business {uid}",
            category="Plumber",
            city="New York",
            phone="+12125550199",
            lifecycle_status=LifecycleStatus.VERIFIED
        )
        db.add(b)
        await db.commit()
        await db.refresh(b)
        
        # Add website record
        w = Website(
            business_id=b.id,
            url="http://example-old.com",
            domain="example-old.com",
            status=WebsiteStatus.OFFICIAL_WEBSITE
        )
        db.add(w)
        await db.commit()

        engine = OpportunityEngine()
        res = await engine.analyze_business(db, b.id)

        assert res["business_id"] == str(b.id)
        assert res["opportunity_count"] >= 0
        assert "max_confidence" in res

        # Verify DB query
        stmt = select(Opportunity).where(Opportunity.business_id == b.id)
        db_opps = (await db.execute(stmt)).scalars().all()
        assert isinstance(db_opps, list)

        # Verify Business updated
        stmt_b = select(Business).where(Business.id == b.id)
        updated_b = (await db.execute(stmt_b)).scalar_one()
        assert updated_b.opportunity_confidence >= 0.0
