import logging
import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SEOAnalyzer:
    """
    Deterministic Organic Search (SEO) Signal Analyzer.
    Evaluates title tag presence/length, meta descriptions, H1 hierarchy,
    canonical links, and sitemap/robots.txt presence.
    """

    def analyze_seo(self, html_text: str, robots_found: bool = False) -> Dict[str, Any]:
        signals: List[Dict[str, Any]] = []

        if not html_text:
            return {"signals": []}

        soup = BeautifulSoup(html_text, "html.parser")

        # 1. Title Tag Audit
        title_tag = soup.find("title")
        title_text = title_tag.get_text(strip=True) if title_tag else ""

        if not title_text:
            signals.append({
                "code": "MISSING_TITLE_TAG",
                "category": "seo",
                "severity": "HIGH",
                "description": "Homepage is missing an HTML <title> tag.",
            })
        elif len(title_text) < 20:
            signals.append({
                "code": "SHORT_TITLE_TAG",
                "category": "seo",
                "severity": "LOW",
                "description": f"Title tag ('{title_text}') is too short ({len(title_text)} chars). Recommended: 40-60 chars.",
            })

        # 2. Meta Description Audit
        meta_desc_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
        meta_desc = meta_desc_tag.get("content", "").strip() if meta_desc_tag else ""

        if not meta_desc:
            signals.append({
                "code": "MISSING_META_DESCRIPTION",
                "category": "seo",
                "severity": "HIGH",
                "description": "Homepage is missing meta description tag for search snippet optimization.",
            })

        # 3. Heading Structure Audit (H1)
        h1_tags = soup.find_all("h1")
        if not h1_tags:
            signals.append({
                "code": "MISSING_H1_TAG",
                "category": "seo",
                "severity": "HIGH",
                "description": "Page is missing an H1 heading tag for primary content hierarchy.",
            })
        elif len(h1_tags) > 2:
            signals.append({
                "code": "MULTIPLE_H1_TAGS",
                "category": "seo",
                "severity": "LOW",
                "description": f"Found {len(h1_tags)} H1 tags on page. Best practice is a single primary H1 tag.",
            })

        # 4. Canonical Tag Audit
        canonical_tag = soup.find("link", attrs={"rel": re.compile(r"canonical", re.I)})
        if not canonical_tag:
            signals.append({
                "code": "MISSING_CANONICAL_LINK",
                "category": "seo",
                "severity": "LOW",
                "description": "Missing canonical URL tag to prevent duplicate content indexing.",
            })

        # 5. Robots.txt Audit
        if not robots_found:
            signals.append({
                "code": "MISSING_ROBOTS_TXT",
                "category": "seo",
                "severity": "MEDIUM",
                "description": "robots.txt file was not detected, limiting search crawler guidance.",
            })

        return {
            "title": title_text,
            "meta_description": meta_desc,
            "h1_count": len(h1_tags),
            "has_canonical": bool(canonical_tag),
            "signals": signals,
        }
