import logging
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

PAGESPEED_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


class PageSpeedService:
    """
    Google PageSpeed Insights API (Free Tier).
    Fetches Performance score + Core Web Vitals for mobile and desktop.
    No billing required — up to 25,000 queries/day free.
    """

    async def fetch_scores(self, url: str) -> Dict[str, Any]:
        """Fetch both mobile and desktop PageSpeed scores for a given URL."""
        result = {
            "mobile": None,
            "desktop": None,
            "error": None,
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                mobile_data = await self._fetch_strategy(client, url, "mobile")
                desktop_data = await self._fetch_strategy(client, url, "desktop")
                result["mobile"] = mobile_data
                result["desktop"] = desktop_data
        except Exception as e:
            logger.warning(f"[PageSpeed] Failed to fetch scores for {url}: {e}")
            result["error"] = str(e)
        return result

    async def _fetch_strategy(self, client: httpx.AsyncClient, url: str, strategy: str) -> Optional[Dict[str, Any]]:
        params = {
            "url": url,
            "strategy": strategy,
            "category": "performance",
        }
        # Use API key if available (not required but increases quota)
        api_key = getattr(settings, "GOOGLE_PLACES_API_KEY", None)
        if api_key:
            params["key"] = api_key

        try:
            resp = await client.get(PAGESPEED_API_URL, params=params)
            if resp.status_code != 200:
                logger.warning(f"[PageSpeed] {strategy} returned {resp.status_code} for {url}")
                return None

            data = resp.json()
            return self._parse_pagespeed_response(data, strategy)
        except Exception as e:
            logger.warning(f"[PageSpeed] {strategy} fetch error for {url}: {e}")
            return None

    def _parse_pagespeed_response(self, data: Dict[str, Any], strategy: str) -> Dict[str, Any]:
        """Extract performance score and Core Web Vitals from API response."""
        try:
            categories = data.get("lighthouseResult", {}).get("categories", {})
            audits = data.get("lighthouseResult", {}).get("audits", {})

            performance_score = None
            perf_category = categories.get("performance", {})
            if perf_category and "score" in perf_category:
                performance_score = round(perf_category["score"] * 100)

            def _get_audit_value(audit_key: str) -> Optional[float]:
                audit = audits.get(audit_key, {})
                numeric_value = audit.get("numericValue")
                if numeric_value is not None:
                    return round(float(numeric_value), 2)
                return None

            fcp = _get_audit_value("first-contentful-paint")
            lcp = _get_audit_value("largest-contentful-paint")
            cls = _get_audit_value("cumulative-layout-shift")
            tbt = _get_audit_value("total-blocking-time")
            si = _get_audit_value("speed-index")

            return {
                "strategy": strategy,
                "performance_score": performance_score,
                "first_contentful_paint_ms": fcp,
                "largest_contentful_paint_ms": lcp,
                "cumulative_layout_shift": cls,
                "total_blocking_time_ms": tbt,
                "speed_index_ms": si,
            }
        except Exception as e:
            logger.warning(f"[PageSpeed] Parse error for {strategy}: {e}")
            return {"strategy": strategy, "performance_score": None, "error": str(e)}
