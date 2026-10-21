import logging
import time
import httpx
import json
from typing import Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup

from app.services.pagespeed_service import PageSpeedService
from app.services.website_analyzer import WebsiteAnalyzer
from app.services.seo_analyzer import SEOAnalyzer

logger = logging.getLogger(__name__)


class AuditEngine:
    """
    Phase 2B: Website Audit Engine
    
    Full pipeline:
    1. Fetch website HTML + measure response time
    2. Run WebsiteAnalyzer (technical signals)
    3. Run SEOAnalyzer (SEO signals)
    4. Call Google PageSpeed API (mobile + desktop)
    5. Calculate Redesign Score (0-16 points)
    6. Generate Sales Pitch summary
    7. Return structured audit result dict
    """

    def __init__(self):
        self.pagespeed = PageSpeedService()
        self.website_analyzer = WebsiteAnalyzer()
        self.seo_analyzer = SEOAnalyzer()

    async def run_audit(self, website_url: str, business_name: str, city: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a full website audit for the given URL.
        Returns a dict ready to persist into WebsiteAudit + SEOAudit tables.
        """
        logger.info(f"[AuditEngine] Starting audit for: {business_name} — {website_url}")

        # --- Step 1: Fetch HTML ---
        html_text, is_https, response_time_ms, final_url = await self._fetch_html(website_url)

        # --- Step 2: Technical Website Analysis ---
        tech_result = self.website_analyzer.analyze_website(
            html_text=html_text or "",
            final_url=final_url or website_url,
            is_https=is_https,
            latency_ms=response_time_ms,
        )

        # --- Step 3: SEO Analysis ---
        robots_found = await self._check_robots_txt(website_url)
        seo_result = self.seo_analyzer.analyze_seo(
            html_text=html_text or "",
            robots_found=robots_found,
        )

        # --- Step 4: Schema Markup check ---
        schema_present = self._detect_schema_markup(html_text or "")
        cta_visible = self._detect_cta(html_text or "")
        contact_visible = self._detect_contact_info(html_text or "")

        # --- Step 5: PageSpeed Scores ---
        pagespeed_data = await self.pagespeed.fetch_scores(final_url or website_url)
        mobile_ps = pagespeed_data.get("mobile") or {}
        desktop_ps = pagespeed_data.get("desktop") or {}

        mobile_score = mobile_ps.get("performance_score")
        desktop_score = desktop_ps.get("performance_score")

        # --- Step 6: Redesign Score Calculation ---
        redesign_score, issues = self._calculate_redesign_score(
            is_https=is_https,
            has_viewport=tech_result.get("has_viewport", False),
            mobile_score=mobile_score,
            response_time_ms=response_time_ms,
            schema_present=schema_present,
            cta_visible=cta_visible,
            seo_signals=seo_result.get("signals", []),
            tech_signals=tech_result.get("signals", []),
        )

        recommendation = self._get_recommendation(redesign_score)

        # --- Step 7: Generate Sales Pitch ---
        sales_pitch = self._generate_sales_pitch(
            business_name=business_name,
            city=city,
            mobile_score=mobile_score,
            desktop_score=desktop_score,
            redesign_score=redesign_score,
            recommendation=recommendation,
            issues=issues,
            is_https=is_https,
            has_viewport=tech_result.get("has_viewport", False),
            cta_visible=cta_visible,
        )

        return {
            # Audit status
            "audit_status": "COMPLETED",

            # Technical
            "https_enabled": is_https,
            "responsive_mobile": tech_result.get("has_viewport", False),
            "cta_visible": cta_visible,
            "contact_visible": contact_visible,
            "schema_markup_present": schema_present,
            "response_time_ms": response_time_ms,

            # PageSpeed
            "pagespeed_mobile_score": mobile_score,
            "pagespeed_desktop_score": desktop_score,
            "first_contentful_paint_ms": mobile_ps.get("first_contentful_paint_ms"),
            "largest_contentful_paint_ms": mobile_ps.get("largest_contentful_paint_ms"),
            "cumulative_layout_shift": mobile_ps.get("cumulative_layout_shift"),
            "total_blocking_time_ms": mobile_ps.get("total_blocking_time_ms"),
            "speed_index_ms": mobile_ps.get("speed_index_ms"),
            "raw_pagespeed_data": pagespeed_data,

            # Redesign Intelligence
            "redesign_score": redesign_score,
            "redesign_recommendation": recommendation,
            "issues": issues,
            "sales_pitch": sales_pitch,

            # SEO fields (for seo_audit table)
            "seo": {
                "title": seo_result.get("title", ""),
                "meta_description": seo_result.get("meta_description", ""),
                "h1_count": seo_result.get("h1_count", 0),
                "has_canonical": seo_result.get("has_canonical", False),
                "robots_present": robots_found,
                "issues": seo_result.get("signals", []),
            }
        }

    # ──────────────────────────────────────────────────────
    # Private Helpers
    # ──────────────────────────────────────────────────────

    async def _fetch_html(self, url: str) -> Tuple[Optional[str], bool, float, str]:
        """Fetch homepage HTML. Returns (html, is_https, latency_ms, final_url)."""
        try:
            start = time.monotonic()
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; LeadAuditBot/1.0)",
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            }
            async with httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=True,
                verify=False,
                headers=headers,
            ) as client:
                resp = await client.get(url)
                latency = (time.monotonic() - start) * 1000
                final_url = str(resp.url)
                is_https = final_url.startswith("https://")
                return resp.text, is_https, round(latency, 1), final_url
        except Exception as e:
            logger.warning(f"[AuditEngine] HTML fetch failed for {url}: {e}")
            return None, url.startswith("https://"), 0.0, url

    async def _check_robots_txt(self, url: str) -> bool:
        """Check if robots.txt exists on the domain root."""
        try:
            # Build domain root
            from urllib.parse import urlparse
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, verify=False) as client:
                resp = await client.get(robots_url)
                return resp.status_code == 200 and len(resp.text) > 10
        except Exception:
            return False

    def _detect_schema_markup(self, html_text: str) -> bool:
        """Check for JSON-LD or Microdata schema markup."""
        if not html_text:
            return False
        soup = BeautifulSoup(html_text, "html.parser")
        # JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if "@type" in str(data):
                    return True
            except Exception:
                pass
        # Microdata
        if soup.find(attrs={"itemtype": True}):
            return True
        return False

    def _detect_cta(self, html_text: str) -> bool:
        """Detect if page has a visible Call-to-Action (button/link with action text)."""
        if not html_text:
            return False
        cta_keywords = [
            "contact us", "get a quote", "call us", "book now", "get started",
            "free consultation", "request a quote", "schedule", "call now",
            "get in touch", "hire us", "enquire", "inquire", "buy now",
            "sign up", "try for free", "shop now"
        ]
        text_lower = html_text.lower()
        return any(kw in text_lower for kw in cta_keywords)

    def _detect_contact_info(self, html_text: str) -> bool:
        """Detect if phone number or email is visible on page."""
        if not html_text:
            return False
        import re
        phone_pattern = re.compile(r'(\+?\d[\d\s\-().]{7,}\d)')
        email_pattern = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
        text = BeautifulSoup(html_text, "html.parser").get_text()
        return bool(phone_pattern.search(text) or email_pattern.search(text))

    def _calculate_redesign_score(
        self,
        is_https: bool,
        has_viewport: bool,
        mobile_score: Optional[int],
        response_time_ms: float,
        schema_present: bool,
        cta_visible: bool,
        seo_signals: list,
        tech_signals: list,
    ) -> Tuple[int, list]:
        """
        Calculate Redesign Score (0-16 points).
        Higher score = more urgent redesign need.
        """
        score = 0
        issues = []

        # 1. Mobile PageSpeed Score
        if mobile_score is not None:
            if mobile_score < 50:
                score += 3
                issues.append({
                    "code": "CRITICAL_MOBILE_SPEED",
                    "severity": "HIGH",
                    "points": 3,
                    "description": f"Mobile PageSpeed score is critically low ({mobile_score}/100). Most visitors will leave before page loads.",
                })
            elif mobile_score < 70:
                score += 1
                issues.append({
                    "code": "POOR_MOBILE_SPEED",
                    "severity": "MEDIUM",
                    "points": 1,
                    "description": f"Mobile PageSpeed score is below average ({mobile_score}/100). Improvements needed.",
                })
        else:
            # Could not fetch PageSpeed — still add as minor issue
            issues.append({
                "code": "PAGESPEED_UNAVAILABLE",
                "severity": "LOW",
                "points": 0,
                "description": "Could not retrieve PageSpeed score. Site may be blocking crawlers.",
            })

        # 2. Mobile Responsive (Viewport)
        if not has_viewport:
            score += 3
            issues.append({
                "code": "NOT_MOBILE_RESPONSIVE",
                "severity": "HIGH",
                "points": 3,
                "description": "Website is not mobile-responsive. 60%+ of internet traffic is from mobile devices.",
            })

        # 3. HTTPS / SSL
        if not is_https:
            score += 2
            issues.append({
                "code": "NO_SSL_CERTIFICATE",
                "severity": "HIGH",
                "points": 2,
                "description": "Website does not use HTTPS. Google penalizes HTTP sites and browsers show 'Not Secure' warnings.",
            })

        # 4. Response Time
        if response_time_ms > 2000:
            score += 1
            issues.append({
                "code": "SLOW_PAGE_LOAD",
                "severity": "MEDIUM",
                "points": 1,
                "description": f"Page load response time is {response_time_ms:.0f}ms. Users expect pages to load under 2 seconds.",
            })

        # 5. Schema Markup
        if not schema_present:
            score += 1
            issues.append({
                "code": "NO_SCHEMA_MARKUP",
                "severity": "MEDIUM",
                "points": 1,
                "description": "No structured data (Schema.org) detected. Missing rich results in Google Search.",
            })

        # 6. CTA Missing
        if not cta_visible:
            score += 1
            issues.append({
                "code": "NO_CALL_TO_ACTION",
                "severity": "MEDIUM",
                "points": 1,
                "description": "No clear Call-to-Action (CTA) detected. Visitors don't know what to do next.",
            })

        # 7. SEO issues
        seo_issue_codes = {s.get("code") for s in seo_signals}
        if "MISSING_TITLE_TAG" in seo_issue_codes:
            score += 1
            issues.append({
                "code": "MISSING_TITLE_TAG",
                "severity": "HIGH",
                "points": 1,
                "description": "Page is missing an HTML title tag — critical for SEO and search click-through rates.",
            })
        if "MISSING_META_DESCRIPTION" in seo_issue_codes:
            score += 1
            issues.append({
                "code": "MISSING_META_DESCRIPTION",
                "severity": "MEDIUM",
                "points": 1,
                "description": "Missing meta description — the text that appears in Google search results under the title.",
            })
        if "MISSING_H1_TAG" in seo_issue_codes:
            score += 1
            issues.append({
                "code": "MISSING_H1_TAG",
                "severity": "MEDIUM",
                "points": 1,
                "description": "No H1 heading found. Search engines use H1 to understand what the page is about.",
            })
        if "MISSING_ROBOTS_TXT" in seo_issue_codes:
            score += 1
            issues.append({
                "code": "MISSING_ROBOTS_TXT",
                "severity": "LOW",
                "points": 1,
                "description": "No robots.txt file found. Search crawlers are working without guidance.",
            })

        return min(score, 16), issues

    def _get_recommendation(self, score: int) -> str:
        if score >= 10:
            return "URGENT"
        elif score >= 6:
            return "RECOMMENDED"
        elif score >= 1:
            return "SEO_ONLY"
        return "GOOD"

    def _generate_sales_pitch(
        self,
        business_name: str,
        city: Optional[str],
        mobile_score: Optional[int],
        desktop_score: Optional[int],
        redesign_score: int,
        recommendation: str,
        issues: list,
        is_https: bool,
        has_viewport: bool,
        cta_visible: bool,
    ) -> str:
        """Generate a compelling, personalized sales pitch for this business."""

        location_str = f" in {city}" if city else ""
        top_issues = [i["description"] for i in issues[:3] if i.get("points", 0) >= 1]

        if recommendation == "URGENT":
            pitch_intro = (
                f"Hi, I was looking at {business_name}'s{location_str} website and found some serious issues "
                f"that are likely costing you customers every day."
            )
        elif recommendation == "RECOMMENDED":
            pitch_intro = (
                f"Hi, I ran a quick audit on {business_name}'s{location_str} website and found several areas "
                f"where improvements could significantly boost your online results."
            )
        else:
            pitch_intro = (
                f"Hi, your website for {business_name}{location_str} has a solid foundation. "
                f"With a few targeted SEO improvements, you could get significantly more traffic from Google."
            )

        # Build issue summary
        issue_lines = ""
        if mobile_score is not None and mobile_score < 70:
            issue_lines += f"\n• Mobile Speed Score: {mobile_score}/100 — most visitors on phones may leave before it loads."
        if not has_viewport:
            issue_lines += "\n• Website is NOT mobile-friendly — 60%+ of your customers browse on phones."
        if not is_https:
            issue_lines += "\n• No SSL Certificate — browsers show 'Not Secure' warnings to visitors."
        if not cta_visible:
            issue_lines += "\n• No clear 'Contact Us' or 'Get a Quote' button visible — visitors don't know what to do next."
        for iss in top_issues:
            if iss not in issue_lines:
                issue_lines += f"\n• {iss}"

        pitch_body = f"Here's what we found:{issue_lines}" if issue_lines else ""

        if recommendation in ("URGENT", "RECOMMENDED"):
            pitch_cta = (
                f"\n\nI'd love to show you a free demo of what a redesigned site could look like for {business_name}. "
                f"We specialize in fast, mobile-friendly websites that help local businesses get more calls and customers. "
                f"Would you have 10 minutes for a quick chat?"
            )
        else:
            pitch_cta = (
                f"\n\nI'd love to help {business_name} rank higher on Google with targeted local SEO. "
                f"Would you be open to a free SEO report showing your current ranking opportunities?"
            )

        return f"{pitch_intro}\n\n{pitch_body}{pitch_cta}".strip()
