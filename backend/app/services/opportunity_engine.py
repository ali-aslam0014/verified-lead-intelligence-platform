import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.business import Business, SourceRecord
from app.models.digital_presence import Website, Contact
from app.models.verification import VerificationResult, Evidence
from app.models.opportunity import Opportunity
from app.models.enums import OpportunityType, LifecycleStatus

from app.services.website_analyzer import WebsiteAnalyzer
from app.services.seo_analyzer import SEOAnalyzer
from app.services.local_seo_analyzer import LocalSEOAnalyzer
from app.services.conversion_analyzer import ConversionAnalyzer
from app.services.competitor_analyzer import CompetitorAnalyzer
from app.services.opportunity_ai import OpportunityAIInterpreter

logger = logging.getLogger(__name__)


class OpportunityEngine:
    """
    Master Opportunity Intelligence Engine.
    Executes deterministic signal analyzers across Website, SEO, Local SEO,
    Conversion, and Competitor layers. Validates evidence and stores
    evidence-backed Opportunity records.
    """

    def __init__(self):
        self.website_analyzer = WebsiteAnalyzer()
        self.seo_analyzer = SEOAnalyzer()
        self.local_seo_analyzer = LocalSEOAnalyzer()
        self.conversion_analyzer = ConversionAnalyzer()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.ai_interpreter = OpportunityAIInterpreter()

    async def analyze_business(self, db: AsyncSession, business_id: uuid.UUID) -> Dict[str, Any]:
        logger.info(f"Executing Opportunity Intelligence Engine for Business ID: '{business_id}'")

        stmt = (
            select(Business)
            .where(Business.id == business_id)
            .options(
                selectinload(Business.website),
                selectinload(Business.contacts),
                selectinload(Business.verification_results),
                selectinload(Business.evidence),
                selectinload(Business.source_records),
            )
        )
        res = await db.execute(stmt)
        business = res.scalar_one_or_none()

        if not business:
            logger.error(f"Business ID '{business_id}' not found for opportunity analysis.")
            return {"status": "FAILED", "error": "Business entity not found"}

        now = datetime.now(timezone.utc)

        # Extract verified html / website data if available
        html_text = ""
        final_url = ""
        is_https = False
        robots_found = False

        if business.website:
            final_url = business.website.url
            is_https = final_url.startswith("https://")

        # Check verification results for website reachability & HTML evidence
        for vr in business.verification_results:
            if vr.check_type.value == "WEBSITE_REACHABILITY" and vr.evidence:
                final_url = vr.evidence.get("final_url", final_url)
            if vr.check_type.value == "ROBOTS_TXT_ACCESSIBLE":
                robots_found = vr.result.value == "PASS"

        # Check evidence for HTML body sample if stored
        for ev in business.evidence:
            if ev.data and "html_text" in ev.data:
                html_text = ev.data["html_text"]

        # Collect Signals from Deterministic Analyzers
        all_signals: List[Dict[str, Any]] = []

        # 1. Technical Website Analysis
        w_res = self.website_analyzer.analyze_website(html_text, final_url, is_https)
        all_signals.extend(w_res["signals"])

        # 2. SEO Analysis
        s_res = self.seo_analyzer.analyze_seo(html_text, robots_found)
        all_signals.extend(s_res["signals"])

        # 3. Local SEO Analysis
        latest_sr_data = business.source_records[0].raw_data if business.source_records else {}
        l_res = self.local_seo_analyzer.analyze_local_seo(
            html_text=html_text,
            city=business.city,
            niche=business.category or "Business",
            rating=latest_sr_data.get("rating"),
            review_count=latest_sr_data.get("review_count")
        )
        all_signals.extend(l_res["signals"])

        # 4. Conversion Analysis
        c_res = self.conversion_analyzer.analyze_conversion(html_text)
        all_signals.extend(c_res["signals"])

        # 5. Competitor Gap Analysis (fetch peer businesses in same city)
        peer_data = await self._fetch_peer_businesses(db, business.city, business.id)
        target_comp_data = {"has_booking": c_res.get("has_booking", False), "review_count": latest_sr_data.get("review_count")}
        comp_res = self.competitor_analyzer.analyze_competitor_gap(target_comp_data, peer_data)
        all_signals.extend(comp_res["signals"])

        # Available evidence IDs
        available_evidence_ids = [str(ev.id) for ev in business.evidence]

        # 6. AI Signal & Evidence Interpretation
        opp_candidates = self.ai_interpreter.interpret_signals(
            business_name=business.name,
            verified_facts={"name": business.name, "city": business.city, "phone": business.phone},
            collected_signals=all_signals,
            available_evidence_ids=available_evidence_ids
        )

        # Clear old opportunities & store new candidate records
        await db.execute(delete(Opportunity).where(Opportunity.business_id == business_id))

        opportunity_objs = []
        max_confidence = 0.0

        for candidate in opp_candidates:
            opp_type_enum = OpportunityType(candidate["type"])
            opp = Opportunity(
                business_id=business.id,
                type=opp_type_enum,
                status=candidate.get("status", "CONFIRMED"),
                priority=candidate.get("priority", "HIGH"),
                confidence=candidate.get("confidence", 0.8),
                evidence=candidate.get("evidence", {}),
                evidence_ids={"ids": candidate.get("evidence_ids", [])},
                recommended_service=candidate["recommended_service"],
                recommended_angle=candidate.get("recommended_angle"),
                reason=candidate["reason"],
            )
            db.add(opp)
            opportunity_objs.append(opp)
            if candidate.get("confidence", 0.0) > max_confidence:
                max_confidence = candidate.get("confidence", 0.0)

        # Update business opportunity confidence score
        business.opportunity_confidence = max_confidence
        if opportunity_objs and business.lifecycle_status == LifecycleStatus.VERIFIED:
            business.lifecycle_status = LifecycleStatus.QUALIFIED

        await db.commit()

        logger.info(f"Opportunity Analysis Complete for '{business.name}' -> Found {len(opportunity_objs)} opportunities.")

        return {
            "business_id": str(business.id),
            "name": business.name,
            "opportunity_count": len(opportunity_objs),
            "max_confidence": max_confidence,
            "opportunities": [
                {
                    "id": str(o.id) if hasattr(o, "id") and o.id else None,
                    "type": o.type.value,
                    "status": o.status,
                    "priority": o.priority,
                    "confidence": o.confidence,
                    "recommended_service": o.recommended_service,
                    "recommended_angle": o.recommended_angle,
                    "reason": o.reason,
                    "evidence_ids": o.evidence_ids.get("ids", []),
                }
                for o in opportunity_objs
            ]
        }

    async def _fetch_peer_businesses(self, db: AsyncSession, city: Optional[str], exclude_id: uuid.UUID) -> List[Dict[str, Any]]:
        if not city:
            return []
        clean_c = city.split(",")[0].strip()
        if not clean_c:
            return []

        stmt = (
            select(Business)
            .where(Business.city.ilike(f"%{clean_c}%"), Business.id != exclude_id)
            .options(selectinload(Business.source_records))
            .limit(10)
        )
        res = await db.execute(stmt)
        peers = res.scalars().all()

        peer_data = []
        for p in peers:
            latest = p.source_records[0].raw_data if p.source_records else {}
            peer_data.append({
                "name": p.name,
                "review_count": latest.get("review_count", 0),
                "has_booking": "book" in str(latest).lower() or "schedule" in str(latest).lower(),
            })

        return peer_data
