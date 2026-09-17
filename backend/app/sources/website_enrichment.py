import logging
import httpx
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.sources.base import BaseSourceAdapter, DiscoveryRequest, RawDiscoveryResult

logger = logging.getLogger(__name__)


class WebsiteEnrichmentAdapter(BaseSourceAdapter):
    """
    Secondary Enrichment Adapter that probes official website domains of discovered business entities.
    Executes ONLY when a canonical Business has a valid domain/website URL.
    Extracts HTTP status, meta title, meta description, contact links, and tech stack signatures.
    """

    @property
    def source_name(self) -> str:
        return "website_enrichment"

    @property
    def rate_limit_per_minute(self) -> int:
        return 120

    @property
    def timeout_seconds(self) -> float:
        return 2.0

    async def search(self, request: DiscoveryRequest) -> List[RawDiscoveryResult]:
        # Search is not supported for enrichment adapter; domain enrichment runs on specific URL
        return []

    async def enrich_url(self, target_url: str) -> RawDiscoveryResult:
        """Probes a specific target website domain and extracts meta header signals."""
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            url_to_probe = f"https://{target_url}"
        else:
            url_to_probe = target_url

        logger.info(f"Enriching website domain: '{url_to_probe}'")
        raw_payload: Dict[str, Any] = {
            "target_url": target_url,
            "probed_url": url_to_probe,
            "is_reachable": False,
            "http_status": None,
            "title": None,
            "meta_description": None,
            "detected_tech": [],
            "has_contact_page": False,
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds, 
                follow_redirects=True, 
                headers={"User-Agent": "LeadIntelligenceBot/1.0 (+https://verifiedleadintel.local)"}
            ) as client:
                res = await client.get(url_to_probe)

            raw_payload["http_status"] = res.status_code
            raw_payload["is_reachable"] = (200 <= res.status_code < 400)

            if res.status_code == 200:
                html = res.text[:50000] # First 50KB

                # Extract Title
                title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
                if title_match:
                    raw_payload["title"] = title_match.group(1).strip()[:200]

                # Extract Meta Description
                meta_desc_match = re.search(
                    r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE | re.DOTALL
                )
                if meta_desc_match:
                    raw_payload["meta_description"] = meta_desc_match.group(1).strip()[:300]

                # Detect Tech Stack Signatures
                tech_signatures = []
                if "wp-content" in html or "wordpress" in html.lower():
                    tech_signatures.append("WordPress")
                if "shopify" in html.lower():
                    tech_signatures.append("Shopify")
                if "wix.com" in html.lower():
                    tech_signatures.append("Wix")
                if "squarespace" in html.lower():
                    tech_signatures.append("Squarespace")
                if "gtag" in html or "google-analytics" in html:
                    tech_signatures.append("Google Analytics")
                
                # Extract Social Media Profiles from HTML href links
                social_links = {}
                hrefs = re.findall(r'href=["\'](https?://[^\s"\']+)["\']', html, re.IGNORECASE)
                for h in hrefs:
                    h_lower = h.lower()
                    if "facebook.com" in h_lower and "facebook" not in social_links:
                        social_links["facebook"] = h
                    elif "linkedin.com" in h_lower and "linkedin" not in social_links:
                        social_links["linkedin"] = h
                    elif "instagram.com" in h_lower and "instagram" not in social_links:
                        social_links["instagram"] = h
                    elif ("twitter.com" in h_lower or "x.com" in h_lower) and "twitter" not in social_links:
                        social_links["twitter"] = h

                raw_payload["detected_tech"] = tech_signatures
                raw_payload["social_links"] = social_links
                raw_payload["has_contact_page"] = any(k in html.lower() for k in ["/contact", "contact us", "get in touch"])

        except Exception as exc:
            logger.warning(f"Website enrichment probe failed for {url_to_probe}: {exc}")
            raw_payload["error"] = str(exc)

        return RawDiscoveryResult(
            source_name=self.source_name,
            source_identifier=target_url,
            raw_data=raw_payload,
            observed_at=datetime.now(timezone.utc),
            confidence_hint=0.8,
            licensing_notice="Direct HTTP Domain Probe",
        )

    async def fetch_details(self, source_identifier: str) -> RawDiscoveryResult:
        return await self.enrich_url(source_identifier)

    async def check_health(self) -> bool:
        return True
