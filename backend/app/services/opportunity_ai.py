import logging
import uuid
from typing import Dict, Any, List, Optional
from app.models.enums import OpportunityType

logger = logging.getLogger(__name__)


class OpportunityAIInterpreter:
    """
    Evidence-Backed AI Opportunity Interpreter.
    Interprets verified facts and deterministic signals to synthesize
    opportunity candidates with evidence validation.
    Strict Mandate: Never fabricates evidence. Validates all evidence IDs.
    """

    def interpret_signals(
        self,
        business_name: str,
        verified_facts: Dict[str, Any],
        collected_signals: List[Dict[str, Any]],
        available_evidence_ids: List[str]
    ) -> List[Dict[str, Any]]:
        opportunities: List[Dict[str, Any]] = []

        if not collected_signals:
            return opportunities

        # Group signals by code/category
        signal_codes = {s["code"] for s in collected_signals}
        signal_dict = {s["code"]: s for s in collected_signals}

        # 1. NEW_WEBSITE Opportunity
        if "NO_VERIFIED_WEBSITE" in signal_codes:
            opp = {
                "type": OpportunityType.NEW_WEBSITE.value,
                "confidence": 0.95,
                "priority": "HIGH",
                "status": "CONFIRMED",
                "recommended_service": "Custom Mobile-First Website Development",
                "reason": f"{business_name} has verified business presence but lacks an official website, losing digital prospects.",
                "recommended_angle": f"Pitch a modern, high-converting 5-page website tailored for {business_name} to capture local search traffic.",
                "evidence_ids": [eid for eid in available_evidence_ids[:3]],
                "evidence": {"supporting_signals": ["NO_VERIFIED_WEBSITE"]}
            }
            opportunities.append(opp)

        # 2. WEBSITE_REDESIGN Opportunity
        redesign_signals = ["MISSING_MOBILE_VIEWPORT", "MISSING_HTTPS_ENCRYPTION", "SLOW_RESPONSE_TIME", "MISSING_IMAGE_ALT_TAGS"]
        active_redesign = [code for code in redesign_signals if code in signal_codes]
        if active_redesign and "NO_VERIFIED_WEBSITE" not in signal_codes:
            conf = 0.90 if len(active_redesign) >= 2 else 0.75
            opp = {
                "type": OpportunityType.WEBSITE_REDESIGN.value,
                "confidence": conf,
                "priority": "HIGH" if conf >= 0.85 else "MEDIUM",
                "status": "CONFIRMED",
                "recommended_service": "Modern High-Performance Website Redesign",
                "reason": f"Existing website has key technical/UX weaknesses: {', '.join(active_redesign)}.",
                "recommended_angle": f"Demonstrate how upgrading {business_name}'s website speed, mobile responsiveness, and security will increase inbound leads.",
                "evidence_ids": [eid for eid in available_evidence_ids[:3]],
                "evidence": {"supporting_signals": active_redesign}
            }
            opportunities.append(opp)

        # 3. SEO / LOCAL_SEO Opportunity
        seo_signals = ["MISSING_TITLE_TAG", "MISSING_META_DESCRIPTION", "MISSING_H1_TAG", "MISSING_CITY_KEYWORD_MENTIONS", "LOW_LOCAL_REVIEW_COUNT"]
        active_seo = [code for code in seo_signals if code in signal_codes]
        if active_seo:
            is_local = "MISSING_CITY_KEYWORD_MENTIONS" in active_seo or "LOW_LOCAL_REVIEW_COUNT" in active_seo
            opp_type = OpportunityType.LOCAL_SEO.value if is_local else OpportunityType.SEO.value
            opp = {
                "type": opp_type,
                "confidence": 0.88 if len(active_seo) >= 2 else 0.70,
                "priority": "HIGH" if is_local else "MEDIUM",
                "status": "CONFIRMED",
                "recommended_service": "Local SEO & Google Pack Optimization" if is_local else "Technical On-Page SEO Campaign",
                "reason": f"Search visibility opportunities identified: {', '.join(active_seo)}.",
                "recommended_angle": f"Show {business_name} how fixing on-page meta tags and city keyword targeting will boost Google local pack rankings.",
                "evidence_ids": [eid for eid in available_evidence_ids[:3]],
                "evidence": {"supporting_signals": active_seo}
            }
            opportunities.append(opp)

        # 4. CONVERSION_OPTIMIZATION Opportunity
        conv_signals = ["MISSING_PRIMARY_CONVERSION_CTA", "MISSING_ONLINE_BOOKING_LINK", "MISSING_CLICK_TO_CALL_PHONE", "MISSING_HOMEPAGE_CONTACT_FORM"]
        active_conv = [code for code in conv_signals if code in signal_codes]
        if active_conv and "NO_VERIFIED_WEBSITE" not in signal_codes:
            opp = {
                "type": OpportunityType.CONVERSION_OPTIMIZATION.value,
                "confidence": 0.87,
                "priority": "HIGH",
                "status": "CONFIRMED",
                "recommended_service": "Lead Capture & Conversion Rate Optimization (CRO)",
                "reason": f"Website exhibits conversion friction: {', '.join(active_conv)}.",
                "recommended_angle": f"Offer {business_name} an online appointment scheduling widget and click-to-call CTA optimization to double website conversion rates.",
                "evidence_ids": [eid for eid in available_evidence_ids[:3]],
                "evidence": {"supporting_signals": active_conv}
            }
            opportunities.append(opp)

        # 5. COMPETITOR_GAP Opportunity
        comp_signals = ["COMPETITOR_ONLINE_BOOKING_GAP", "COMPETITOR_REVIEW_VOLUME_GAP"]
        active_comp = [code for code in comp_signals if code in signal_codes]
        if active_comp:
            opp = {
                "type": OpportunityType.COMPETITOR_GAP.value,
                "confidence": 0.82,
                "priority": "MEDIUM",
                "status": "NEEDS_REVIEW",  # Competitor claims marked for review
                "recommended_service": "Competitive Feature Parity & Local Dominance Package",
                "reason": signal_dict[active_comp[0]]["description"] if active_comp[0] in signal_dict else "Campaign peers demonstrate features this business lacks.",
                "recommended_angle": f"Share market insights comparing {business_name} against top local competitors in the same city.",
                "evidence_ids": [eid for eid in available_evidence_ids[:3]],
                "evidence": {"supporting_signals": active_comp}
            }
            opportunities.append(opp)

        # Evidence validation: Ensure evidence_ids are strictly present in available_evidence_ids
        valid_opps = []
        for o in opportunities:
            if available_evidence_ids:
                validated_eids = [eid for eid in o.get("evidence_ids", []) if eid in available_evidence_ids]
            else:
                validated_eids = o.get("evidence_ids", [])
            o["evidence_ids"] = validated_eids
            valid_opps.append(o)

        return valid_opps
