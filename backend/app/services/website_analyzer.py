import logging
import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebsiteAnalyzer:
    """
    Deterministic Technical Website Signal Analyzer.
    Extracts viewport tags, mobile responsiveness signals, image alt attributes,
    HTTPS availability, and response performance signals.
    """

    def analyze_website(self, html_text: str, final_url: str, is_https: bool = False, latency_ms: float = 0.0) -> Dict[str, Any]:
        signals: List[Dict[str, Any]] = []

        if not html_text:
            return {
                "has_website": False,
                "signals": [
                    {
                        "code": "NO_VERIFIED_WEBSITE",
                        "category": "technical",
                        "severity": "HIGH",
                        "description": "Business has no active verified website URL.",
                    }
                ]
            }

        soup = BeautifulSoup(html_text, "html.parser")

        # 1. Viewport / Mobile readiness check
        viewport_tag = soup.find("meta", attrs={"name": re.compile(r"viewport", re.I)})
        has_viewport = bool(viewport_tag)
        if not has_viewport:
            signals.append({
                "code": "MISSING_MOBILE_VIEWPORT",
                "category": "technical",
                "severity": "HIGH",
                "description": "Website is missing HTML viewport meta tag, causing mobile rendering friction.",
            })

        # 2. Image Alt Text Audit
        images = soup.find_all("img")
        missing_alt_count = sum(1 for img in images if not img.get("alt"))
        if missing_alt_count > 0:
            signals.append({
                "code": "MISSING_IMAGE_ALT_TAGS",
                "category": "technical",
                "severity": "MEDIUM",
                "description": f"Found {missing_alt_count} images missing alt text attributes.",
                "data": {"missing_alt_count": missing_alt_count, "total_images": len(images)}
            })

        # 3. HTTPS Availability
        if not is_https and not final_url.startswith("https://"):
            signals.append({
                "code": "MISSING_HTTPS_ENCRYPTION",
                "category": "technical",
                "severity": "HIGH",
                "description": "Website operates over insecure HTTP protocol without active SSL certificate.",
            })

        # 4. Latency / Response Speed
        if latency_ms > 1500:
            signals.append({
                "code": "SLOW_RESPONSE_TIME",
                "category": "performance",
                "severity": "MEDIUM",
                "description": f"Page load response time ({latency_ms:.0f}ms) exceeds recommended threshold.",
                "data": {"latency_ms": latency_ms}
            })

        return {
            "has_website": True,
            "has_viewport": has_viewport,
            "total_images": len(images),
            "missing_alt_count": missing_alt_count,
            "signals": signals,
        }
