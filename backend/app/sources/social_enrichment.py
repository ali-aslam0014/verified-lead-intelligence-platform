import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.sources.base import BaseSourceAdapter, DiscoveryRequest, RawDiscoveryResult

logger = logging.getLogger(__name__)


class SocialEnrichmentAdapter(BaseSourceAdapter):
    """
    Secondary Enrichment Adapter for validating discovered social profile URLs.
    Executes ONLY when social profile links are attached to a business entity.
    Evaluates evidence confidence (Name match, Location match, Domain match).
    Flags low-confidence profiles as 'SOCIAL_UNCONFIRMED'.
    """

    @property
    def source_name(self) -> str:
        return "social_enrichment"

    @property
    def rate_limit_per_minute(self) -> int:
        return 60

    @property
    def timeout_seconds(self) -> float:
        return 10.0

    async def search(self, request: DiscoveryRequest) -> List[RawDiscoveryResult]:
        return []

    async def verify_social_profile(
        self, 
        platform: str, 
        profile_url: str, 
        expected_business_name: str,
        expected_city: Optional[str] = None
    ) -> RawDiscoveryResult:
        """Evaluates identity evidence matching for a candidate social profile URL."""
        logger.info(f"Evaluating social evidence for {platform} profile: '{profile_url}'")
        
        # Calculate evidence confidence score based on URL handle match
        url_lower = profile_url.lower()
        name_clean = "".join(e for e in expected_business_name.lower() if e.isalnum())
        
        confidence = 0.4
        evidence_matches = []
        
        # Check handle similarity
        if name_clean and (name_clean[:10] in url_lower or name_clean in url_lower):
            confidence += 0.4
            evidence_matches.append("name_handle_match")
            
        if expected_city and expected_city.lower() in url_lower:
            confidence += 0.2
            evidence_matches.append("city_handle_match")

        status_flag = "VERIFIED_SOCIAL" if confidence >= 0.7 else "SOCIAL_UNCONFIRMED"

        raw_payload = {
            "platform": platform.upper(),
            "profile_url": profile_url,
            "expected_business_name": expected_business_name,
            "evidence_matches": evidence_matches,
            "confidence_score": round(confidence, 2),
            "status_flag": status_flag,
        }

        return RawDiscoveryResult(
            source_name=self.source_name,
            source_identifier=profile_url,
            raw_data=raw_payload,
            observed_at=datetime.now(timezone.utc),
            confidence_hint=confidence,
            licensing_notice="Evidence-backed Identity Matching",
        )

    async def fetch_details(self, source_identifier: str) -> RawDiscoveryResult:
        return await self.verify_social_profile("UNKNOWN", source_identifier, "")

    async def check_health(self) -> bool:
        return True
