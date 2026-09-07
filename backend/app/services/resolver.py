import uuid
import re
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple, List, Dict, Any
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.business import Business, SourceRecord
from app.models.digital_presence import Website, Contact
from app.models.enums import LifecycleStatus, WebsiteStatus, ContactType
from app.sources.base import RawDiscoveryResult

logger = logging.getLogger(__name__)


class BusinessResolver:
    """
    Decoupled Business Identity Resolution & Deduplication Engine.
    Implements multi-tier matching confidence rules to eliminate duplicate lead records
    without corrupting distinct business entities.
    """

    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalizes business title by stripping punctuation and corporate suffixes."""
        if not name:
            return ""
        s = name.lower()
        # Remove non-alphanumeric chars
        s = re.sub(r"[^\w\s]", "", s)
        # Remove common corporate suffixes
        words = s.split()
        noise_words = {"llc", "inc", "corp", "co", "ltd", "pc", "group", "services", "company", "pllc"}
        filtered = [w for w in words if w not in noise_words]
        return " ".join(filtered) if filtered else s.strip()

    @staticmethod
    def normalize_phone(phone: Optional[str]) -> Optional[str]:
        """Normalizes phone numbers to clean digits / E.164 representation."""
        if not phone:
            return None
        digits = re.sub(r"\D", "", phone)
        if len(digits) == 10:
            return f"+1{digits}"
        elif len(digits) == 11 and digits.startswith("1"):
            return f"+{digits}"
        elif digits:
            return f"+{digits}"
        return None

    @staticmethod
    def normalize_domain(url_or_domain: Optional[str]) -> Optional[str]:
        """Extracts clean root domain from URLs or domain strings."""
        if not url_or_domain:
            return None
        u = url_or_domain.strip().lower()
        if not u.startswith("http://") and not u.startswith("https://"):
            u = "http://" + u
        try:
            parsed = urlparse(u)
            netloc = parsed.netloc or parsed.path
            netloc = re.sub(r"^www\.", "", netloc)
            return netloc.split(":")[0] if netloc else None
        except Exception:
            return None

    @classmethod
    def calculate_address_similarity(cls, addr1: Optional[str], addr2: Optional[str]) -> float:
        """Calculates Jaccard token similarity between two formatted street addresses."""
        if not addr1 or not addr2:
            return 0.0
        tokens1 = set(re.findall(r"\w+", addr1.lower()))
        tokens2 = set(re.findall(r"\w+", addr2.lower()))
        if not tokens1 or not tokens2:
            return 0.0
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        return len(intersection) / len(union)

    async def resolve_record(
        self,
        db: AsyncSession,
        raw_result: RawDiscoveryResult,
        target_run_id: Optional[uuid.UUID] = None,
    ) -> Tuple[Business, bool]:
        """
        Processes a RawDiscoveryResult object, runs multi-tier deduplication checks,
        and returns (Business, is_newly_created).
        """
        raw_data = raw_result.raw_data or {}
        place_id = raw_result.source_identifier
        name = raw_data.get("name") or "Unknown Business"
        address = raw_data.get("address")
        phone_raw = raw_data.get("phone")
        website_raw = raw_data.get("website")

        normalized_name = self.normalize_name(name)
        normalized_phone = self.normalize_phone(phone_raw)
        normalized_domain = self.normalize_domain(website_raw)

        # Parse city/state from address components or address string
        city = None
        state = None
        country = None
        postal_code = None

        address_components = raw_data.get("address_components", [])
        for comp in address_components:
            types = comp.get("types", [])
            if "locality" in types:
                city = comp.get("longText") or comp.get("shortText")
            elif "administrative_area_level_1" in types:
                state = comp.get("shortText") or comp.get("longText")
            elif "country" in types:
                country = comp.get("shortText")
            elif "postal_code" in types:
                postal_code = comp.get("longText")

        # Fallback city extraction from address string
        if not city and address:
            parts = address.split(",")
            if len(parts) >= 2:
                city = parts[-2].strip()

        # ---------------------------------------------------------------------
        # Tier 1: Deterministic High-Confidence Matches (place_id, domain, phone)
        # ---------------------------------------------------------------------
        matched_business: Optional[Business] = None

        # Tier 1A: Match by source place_id in existing SourceRecord
        if place_id and place_id != "unknown_place_id":
            stmt = select(SourceRecord).where(
                SourceRecord.source_name == raw_result.source_name,
                SourceRecord.source_identifier == place_id,
            ).options(selectinload(SourceRecord.business))
            res = await db.execute(stmt)
            existing_sr = res.scalars().first()
            if existing_sr and existing_sr.business:
                matched_business = existing_sr.business
                logger.info(f"[Tier 1 Match - Place ID] Merged record into Business ID {matched_business.id}")

        # Tier 1B: Match by exact normalized phone
        if not matched_business and normalized_phone:
            stmt = select(Business).where(Business.phone == normalized_phone)
            res = await db.execute(stmt)
            matched_business = res.scalars().first()
            if matched_business:
                logger.info(f"[Tier 1 Match - Phone] Merged record into Business ID {matched_business.id}")

        # Tier 1C: Match by exact root domain via Website relation
        if not matched_business and normalized_domain:
            stmt = select(Website).where(Website.domain == normalized_domain).options(selectinload(Website.business))
            res = await db.execute(stmt)
            existing_web = res.scalars().first()
            if existing_web and existing_web.business:
                matched_business = existing_web.business
                logger.info(f"[Tier 1 Match - Domain] Merged record into Business ID {matched_business.id}")

        # ---------------------------------------------------------------------
        # Tier 2: Strong Composite Match (Normalized Name + City + Address Similarity)
        # ---------------------------------------------------------------------
        if not matched_business and normalized_name and city:
            stmt = select(Business).where(
                Business.normalized_name == normalized_name,
                Business.city == city,
            )
            res = await db.execute(stmt)
            candidate_businesses = res.scalars().all()
            for cand in candidate_businesses:
                addr_sim = self.calculate_address_similarity(address, cand.address)
                if addr_sim >= 0.85:
                    matched_business = cand
                    logger.info(f"[Tier 2 Match - Composite] Merged into Business ID {matched_business.id} (Addr Sim: {addr_sim:.2f})")
                    break

        # ---------------------------------------------------------------------
        # Tier 3: Low Confidence / Isolation Check
        # If no Tier 1 or Tier 2 match found, DO NOT merge. Create new Business entity.
        # ---------------------------------------------------------------------
        is_new = False
        if matched_business:
            # Update timestamps and fill missing canonical attributes
            if not matched_business.phone and normalized_phone:
                matched_business.phone = normalized_phone
            if not matched_business.address and address:
                matched_business.address = address
            matched_business.updated_at = datetime.now(timezone.utc)
        else:
            is_new = True
            matched_business = Business(
                name=name,
                normalized_name=normalized_name,
                category=raw_data.get("primary_type") or "General Business",
                address=address,
                city=city,
                state=state,
                country=country,
                postal_code=postal_code,
                phone=normalized_phone,
                lifecycle_status=LifecycleStatus.DISCOVERED,
                business_confidence=0.85 if (normalized_phone or normalized_domain) else 0.65,
                contact_confidence=0.80 if normalized_phone else 0.0,
                opportunity_confidence=0.5,
                lead_score=0.0,
            )
            db.add(matched_business)
            await db.flush() # Populate matched_business.id

            # Create Website entity if domain is present
            if website_raw and normalized_domain:
                website_obj = Website(
                    business_id=matched_business.id,
                    url=website_raw,
                    domain=normalized_domain,
                    status=WebsiteStatus.OFFICIAL_WEBSITE,
                )
                db.add(website_obj)

            # Create Contact entity if phone is present
            if normalized_phone:
                contact_obj = Contact(
                    business_id=matched_business.id,
                    type=ContactType.PHONE,
                    value=phone_raw or normalized_phone,
                    normalized_value=normalized_phone,
                    validity_status="VALIDATED_FORMAT",
                    ownership_status="UNVERIFIED",
                    confidence=0.85,
                )
                db.add(contact_obj)

        # Always attach immutable SourceRecord for provenance tracking
        provenance_record = SourceRecord(
            business_id=matched_business.id,
            target_run_id=target_run_id,
            source_name=raw_result.source_name,
            source_identifier=place_id,
            raw_data=raw_data,
            observed_at=raw_result.observed_at,
        )
        db.add(provenance_record)

        return matched_business, is_new
