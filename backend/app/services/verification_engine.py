import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.business import Business, SourceRecord
from app.models.digital_presence import Website, Contact, SocialProfile
from app.models.verification import VerificationResult, Evidence
from app.models.enums import (
    LifecycleStatus,
    VerificationCheckType,
    VerificationResultStatus,
    EvidenceType,
)
from app.services.website_verifier import WebsiteVerifier
from app.services.contact_verifier import ContactVerifier
from app.services.social_verifier import SocialVerifier

logger = logging.getLogger(__name__)


class VerificationEngine:
    """
    Master Deterministic Verification Engine.
    Executes multi-layer verification check suites (Website, Contact, Social, Identity),
    aggregates Evidence, detects conflicts, tracks staleness, and assigns canonical
    LifecycleStatus (VERIFIED, REVERIFY_REQUIRED, HUMAN_REVIEW).
    """

    STALENESS_DAYS = 30

    def __init__(self):
        self.website_verifier = WebsiteVerifier()
        self.contact_verifier = ContactVerifier()
        self.social_verifier = SocialVerifier()

    async def verify_business(self, db: AsyncSession, business_id: uuid.UUID) -> Dict[str, Any]:
        """
        Performs full verification pass on a Business entity.
        Stores VerificationResult and Evidence rows and updates Business lifecycle status.
        """
        logger.info(f"Executing Master Verification Pass for Business ID: '{business_id}'")

        # Load Business entity with all relations
        stmt = (
            select(Business)
            .where(Business.id == business_id)
            .options(
                selectinload(Business.website),
                selectinload(Business.contacts),
                selectinload(Business.social_profiles),
                selectinload(Business.source_records),
            )
        )
        res = await db.execute(stmt)
        business = res.scalar_one_or_none()

        if not business:
            logger.error(f"Business ID '{business_id}' not found for verification.")
            return {"status": "FAILED", "error": "Business entity not found"}

        now = datetime.now(timezone.utc)
        source_records_data = [
            {
                "source_name": sr.source_name,
                "source_identifier": sr.source_identifier,
                "raw_data": sr.raw_data,
                "observed_at": sr.observed_at,
            }
            for sr in business.source_records
        ]

        latest_sr_data = business.source_records[0].raw_data if business.source_records else {}
        website_url = business.website.url if business.website else latest_sr_data.get("website")
        website_domain = business.website.domain if business.website else (latest_sr_data.get("website") or "").replace("https://", "").replace("http://", "").split("/")[0]

        # 1. Execute Website Verification
        w_ver = await self.website_verifier.verify_website(website_url, business.name)
        
        # 2. Execute Contact Verification
        email_list = [c.value for c in business.contacts if c.type.value == "EMAIL"]
        phone_val = business.phone or latest_sr_data.get("phone")
        c_ver = self.contact_verifier.verify_contacts(phone_val, email_list, source_records_data, website_domain)

        # 3. Execute Social Verification
        social_dict = latest_sr_data.get("social_links") or {}
        s_ver = await self.social_verifier.verify_social(social_dict, business.name)

        # 4. Identity Consistency Check across sources
        identity_results = self._verify_identity_consistency(business, source_records_data, now)

        # Combine all check results & evidence items
        all_check_results = w_ver["results"] + c_ver["results"] + s_ver["results"] + identity_results["results"]
        all_evidences = w_ver["evidences"] + c_ver["evidences"] + s_ver["evidences"]

        # Clear existing verification results & evidence for fresh pass
        await db.execute(delete(VerificationResult).where(VerificationResult.business_id == business_id))
        await db.execute(delete(Evidence).where(Evidence.business_id == business_id))

        # Store VerificationResults in DB
        ver_result_objs = []
        for r in all_check_results:
            vr = VerificationResult(
                business_id=business.id,
                check_type=r["check_type"],
                result=r["result"],
                confidence=r.get("confidence", 1.0),
                reason=r.get("reason"),
                evidence=r.get("evidence", {}),
                source=r.get("source", "verification_engine"),
                observed_at=r.get("observed_at", now),
            )
            db.add(vr)
            ver_result_objs.append(vr)

        # Store Evidences in DB
        for e in all_evidences:
            ev = Evidence(
                business_id=business.id,
                source=e["source"],
                source_url_or_id=e.get("source_url_or_id"),
                observed_at=e.get("observed_at", now),
                status=e["status"],
                evidence_type=e.get("evidence_type", EvidenceType.OBSERVED_FACT),
                data=e.get("data", {}),
            )
            db.add(ev)

        # 5. Deterministic Lifecycle Status Decision Matrix
        has_conflicts = c_ver["has_conflicts"] or identity_results["has_conflicts"]
        has_critical_fail = any(r["result"] == VerificationResultStatus.FAIL for r in w_ver["results"] if r["check_type"] == VerificationCheckType.WEBSITE_REACHABILITY and website_url)

        if has_conflicts:
            new_status = LifecycleStatus.HUMAN_REVIEW
        elif has_critical_fail:
            new_status = LifecycleStatus.REVERIFY_REQUIRED
        else:
            new_status = LifecycleStatus.VERIFIED

        business.lifecycle_status = new_status
        business.verified_at = now

        # Compile verification summary dict for fast JSON responses
        summary_counts = {
            "total_checks": len(all_check_results),
            "pass_count": sum(1 for r in all_check_results if r["result"] == VerificationResultStatus.PASS),
            "fail_count": sum(1 for r in all_check_results if r["result"] == VerificationResultStatus.FAIL),
            "conflict_count": sum(1 for r in all_check_results if r["result"] == VerificationResultStatus.CONFLICT),
            "not_found_count": sum(1 for r in all_check_results if r["result"] == VerificationResultStatus.NOT_FOUND),
            "website_reachable": w_ver["reachable"],
            "has_https": w_ver["has_https"],
            "has_conflicts": has_conflicts,
            "conflicts": c_ver["conflicts"] + identity_results["conflicts"],
            "verified_at": now.isoformat(),
        }

        business.verification_summary = summary_counts
        await db.commit()

        logger.info(
            f"Verification Pass Complete for '{business.name}' -> LifecycleStatus: {new_status.value} "
            f"(Passed: {summary_counts['pass_count']}/{summary_counts['total_checks']}, Conflicts: {summary_counts['conflict_count']})"
        )

        return {
            "business_id": str(business.id),
            "name": business.name,
            "lifecycle_status": new_status.value,
            "verified_at": now.isoformat(),
            "summary": summary_counts,
            "check_results": [
                {
                    "check_type": r["check_type"].value if hasattr(r["check_type"], "value") else r["check_type"],
                    "result": r["result"].value if hasattr(r["result"], "value") else r["result"],
                    "confidence": r["confidence"],
                    "reason": r["reason"],
                    "evidence": r["evidence"],
                }
                for r in all_check_results
            ]
        }

    def is_stale(self, business: Business) -> bool:
        """Checks if a Business verification timestamp is older than STALENESS_DAYS."""
        if not business.verified_at:
            return True
        stale_threshold = datetime.now(timezone.utc) - timedelta(days=self.STALENESS_DAYS)
        return business.verified_at < stale_threshold

    def _verify_identity_consistency(
        self,
        business: Business,
        source_records_data: List[Dict[str, Any]],
        now: datetime
    ) -> Dict[str, Any]:
        results = []
        conflicts = []

        names_by_source = {sr["source_name"]: sr["raw_data"].get("name") for sr in source_records_data if sr["raw_data"].get("name")}
        addresses_by_source = {sr["source_name"]: sr["raw_data"].get("address") for sr in source_records_data if sr["raw_data"].get("address")}

        # Name consistency check
        unique_names = list(set(names_by_source.values()))
        if len(unique_names) > 1:
            conflicts.append({
                "field": "name",
                "values": names_by_source,
                "message": f"Business name variations detected across sources: {names_by_source}"
            })
            results.append({
                "check_type": VerificationCheckType.IDENTITY_CONSISTENCY,
                "result": VerificationResultStatus.CONFLICT,
                "confidence": 0.85,
                "reason": "Name variations detected across sources",
                "evidence": {"names_by_source": names_by_source},
                "source": "verification_engine",
                "observed_at": now,
            })
        else:
            results.append({
                "check_type": VerificationCheckType.IDENTITY_CONSISTENCY,
                "result": VerificationResultStatus.PASS,
                "confidence": 0.98,
                "reason": "Identity name consistent across sources",
                "evidence": {"canonical_name": business.name, "sources": list(names_by_source.keys())},
                "source": "verification_engine",
                "observed_at": now,
            })

        return {
            "results": results,
            "conflicts": conflicts,
            "has_conflicts": bool(conflicts),
        }
