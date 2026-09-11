import logging
import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ConversionAnalyzer:
    """
    Deterministic Conversion & Friction Signal Analyzer.
    Detects primary CTAs, click-to-call phone links, online booking forms,
    and trust elements (testimonials/reviews) on website.
    """

    CTA_PATTERNS = re.compile(r"(book|schedule|appointment|quote|get started|contact us|call now|request)", re.I)

    def analyze_conversion(self, html_text: str) -> Dict[str, Any]:
        signals: List[Dict[str, Any]] = []

        if not html_text:
            return {"signals": []}

        soup = BeautifulSoup(html_text, "html.parser")

        # 1. Primary Call to Action (CTA) Button Audit
        buttons_and_links = soup.find_all(["a", "button", "input"])
        cta_count = 0
        for el in buttons_and_links:
            txt = el.get_text(strip=True) or el.get("value", "")
            if self.CTA_PATTERNS.search(txt):
                cta_count += 1

        has_primary_cta = cta_count > 0
        if not has_primary_cta:
            signals.append({
                "code": "MISSING_PRIMARY_CONVERSION_CTA",
                "category": "conversion",
                "severity": "HIGH",
                "description": "Website homepage lacks a prominent primary Call-To-Action (CTA) button.",
            })

        # 2. Click-to-Call Phone Link Audit
        tel_links = soup.find_all("a", href=re.compile(r"^tel:", re.I))
        has_tel_link = len(tel_links) > 0
        if not has_tel_link:
            signals.append({
                "code": "MISSING_CLICK_TO_CALL_PHONE",
                "category": "conversion",
                "severity": "MEDIUM",
                "description": "Phone number is not formatted as a click-to-call HTML hyperlink ('tel:').",
            })

        # 3. Online Booking / Schedule Appointment Link Audit
        booking_links = soup.find_all("a", href=re.compile(r"(book|schedule|appointment|zocdoc)", re.I))
        has_booking = len(booking_links) > 0
        if not has_booking:
            signals.append({
                "code": "MISSING_ONLINE_BOOKING_LINK",
                "category": "conversion",
                "severity": "HIGH",
                "description": "No direct online appointment booking or scheduling link detected.",
            })

        # 4. Contact Form Audit
        forms = soup.find_all("form")
        has_contact_form = len(forms) > 0
        if not has_contact_form:
            signals.append({
                "code": "MISSING_HOMEPAGE_CONTACT_FORM",
                "category": "conversion",
                "severity": "MEDIUM",
                "description": "No inline lead capture or contact form detected on homepage.",
            })

        # 5. Trust Elements Audit (Testimonials/Reviews)
        full_text = soup.get_text(" ", strip=True).lower()
        has_trust_elements = any(kw in full_text for kw in ["testimonial", "review", "what our patients say", "what our clients say", "guarantee"])
        if not has_trust_elements:
            signals.append({
                "code": "MISSING_TRUST_TESTIMONIALS",
                "category": "conversion",
                "severity": "LOW",
                "description": "Homepage lacks visible customer reviews or testimonial trust signals.",
            })

        return {
            "has_primary_cta": has_primary_cta,
            "has_tel_link": has_tel_link,
            "has_booking": has_booking,
            "has_contact_form": has_contact_form,
            "has_trust_elements": has_trust_elements,
            "signals": signals,
        }
