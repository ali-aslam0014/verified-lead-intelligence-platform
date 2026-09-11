import logging
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class LocalSEOAnalyzer:
    """
    Deterministic Local SEO Signal Analyzer.
    Evaluates city/service keyword mentions, local business schema markup,
    review volume, and local landing page targeting.
    """

    def analyze_local_seo(
        self,
        html_text: str,
        city: Optional[str],
        niche: str,
        rating: Optional[float] = None,
        review_count: Optional[int] = None
    ) -> Dict[str, Any]:
        signals: List[Dict[str, Any]] = []

        clean_city = (city or "").split(",")[0].strip()
        niche_clean = niche.lower().strip()

        # 1. Review Volume & Local Rating Signals
        if review_count is not None and review_count < 20:
            signals.append({
                "code": "LOW_LOCAL_REVIEW_COUNT",
                "category": "local_seo",
                "severity": "HIGH",
                "description": f"Business has only {review_count} local reviews, limiting local pack ranking visibility.",
                "data": {"review_count": review_count, "rating": rating}
            })

        if not html_text:
            return {"signals": signals}

        soup = BeautifulSoup(html_text, "html.parser")
        full_text = soup.get_text(" ", strip=True).lower()

        # 2. City & Location Keyword Targeting Audit
        city_mentioned = False
        if clean_city:
            clean_c = clean_city.lower()
            if clean_c in full_text:
                city_mentioned = True
            else:
                signals.append({
                    "code": "MISSING_CITY_KEYWORD_MENTIONS",
                    "category": "local_seo",
                    "severity": "HIGH",
                    "description": f"Target city '{clean_city}' is not prominently mentioned on website homepage.",
                })

        # 3. Local Business Schema Structured Data Audit
        schema_found = False
        scripts = soup.find_all("script", attrs={"type": re.compile(r"ld\+json", re.I)})
        for s in scripts:
            txt = s.string or ""
            if "schema.org" in txt and ("LocalBusiness" in txt or "Organization" in txt or "PostalAddress" in txt):
                schema_found = True
                break

        if not schema_found:
            signals.append({
                "code": "MISSING_LOCAL_SCHEMA_MARKUP",
                "category": "local_seo",
                "severity": "MEDIUM",
                "description": "Website lacks Schema.org JSON-LD LocalBusiness structured data markup.",
            })

        return {
            "city_mentioned": city_mentioned,
            "has_local_schema": schema_found,
            "review_count": review_count,
            "rating": rating,
            "signals": signals,
        }
