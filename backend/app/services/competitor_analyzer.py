import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class CompetitorAnalyzer:
    """
    Deterministic Competitor Gap Signal Analyzer.
    Compares verified businesses within the same campaign/niche to identify
    defensible feature gaps (e.g. online booking, review volume, HTTPS).
    Does NOT make inflated or unprovable claims.
    """

    def analyze_competitor_gap(
        self,
        target_business_data: Dict[str, Any],
        peer_businesses_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        signals: List[Dict[str, Any]] = []

        if not peer_businesses_data:
            return {"signals": []}

        total_peers = len(peer_businesses_data)
        
        # 1. Online Booking Feature Gap
        peers_with_booking = sum(1 for p in peer_businesses_data if p.get("has_booking"))
        target_has_booking = target_business_data.get("has_booking", False)

        if not target_has_booking and peers_with_booking >= 2:
            signals.append({
                "code": "COMPETITOR_ONLINE_BOOKING_GAP",
                "category": "competitor_gap",
                "severity": "HIGH",
                "description": f"Comparable businesses in this campaign ({peers_with_booking}/{total_peers}) commonly provide online booking, while this business does not show an equivalent feature.",
                "data": {"peers_with_booking": peers_with_booking, "total_peers": total_peers}
            })

        # 2. Review Volume Gap
        target_reviews = target_business_data.get("review_count") or 0
        peer_avg_reviews = sum((p.get("review_count") or 0) for p in peer_businesses_data) / total_peers if total_peers > 0 else 0

        if target_reviews < (peer_avg_reviews / 2) and peer_avg_reviews > 30:
            signals.append({
                "code": "COMPETITOR_REVIEW_VOLUME_GAP",
                "category": "competitor_gap",
                "severity": "MEDIUM",
                "description": f"This business has {target_reviews} reviews compared to campaign peer average of {peer_avg_reviews:.0f} reviews.",
                "data": {"target_reviews": target_reviews, "peer_avg_reviews": peer_avg_reviews}
            })

        return {"signals": signals}
