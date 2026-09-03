from datetime import datetime, timezone
from typing import List
from app.sources.base import BaseSourceAdapter, DiscoveryRequest, RawDiscoveryResult


class MockSourceAdapter(BaseSourceAdapter):
    """
    Mock Data Source Adapter for testing Phase 1 Target Runs & Discovery pipeline
    without hitting external live endpoints or scraping.
    """

    @property
    def source_name(self) -> str:
        return "mock_directory_adapter"

    @property
    def rate_limit_per_minute(self) -> int:
        return 120

    @property
    def timeout_seconds(self) -> float:
        return 10.0

    async def search(self, request: DiscoveryRequest) -> List[RawDiscoveryResult]:
        niche = request.niche
        geography = request.geography

        return [
            RawDiscoveryResult(
                source_name=self.source_name,
                source_identifier="mock_biz_101",
                raw_data={
                    "name": f"Apex {niche.capitalize()} Specialists",
                    "category": niche,
                    "address": f"100 Main St, {geography}",
                    "phone": "+1-512-555-0199",
                    "website": "https://apexspecialists.com",
                    "city": geography,
                },
                observed_at=datetime.now(timezone.utc),
                confidence_hint=0.85,
                licensing_notice="Public Directory License",
            ),
            RawDiscoveryResult(
                source_name=self.source_name,
                source_identifier="mock_biz_102",
                raw_data={
                    "name": f"Premier {niche.capitalize()} Clinic",
                    "category": niche,
                    "address": f"250 Park Ave, {geography}",
                    "phone": "+1-512-555-0244",
                    "website": None,
                    "city": geography,
                },
                observed_at=datetime.now(timezone.utc),
                confidence_hint=0.70,
                licensing_notice="Public Directory License",
            ),
        ]

    async def fetch_details(self, source_identifier: str) -> RawDiscoveryResult:
        return RawDiscoveryResult(
            source_name=self.source_name,
            source_identifier=source_identifier,
            raw_data={
                "name": "Apex Specialists",
                "source_id": source_identifier,
                "status": "active"
            },
            observed_at=datetime.now(timezone.utc),
            confidence_hint=0.90,
            licensing_notice="Public Directory License"
        )

    async def check_health(self) -> bool:
        return True
