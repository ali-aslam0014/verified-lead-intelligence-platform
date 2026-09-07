import logging
import httpx
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.core.config import settings
from app.sources.base import BaseSourceAdapter, DiscoveryRequest, RawDiscoveryResult

logger = logging.getLogger(__name__)


class GooglePlacesAPIError(Exception):
    """Raised when Google Places API (New) returns an error or credentials are missing."""
    pass


class GooglePlacesAdapter(BaseSourceAdapter):
    """
    Production Primary Discovery Adapter using Google Places API (New) Text Search.
    Endpoint: https://places.googleapis.com/v1/places:searchText
    
    STRICT REAL-DATA MANDATE:
    This adapter ONLY returns actual API responses from Google. If credentials are
    missing or API returns an error, it raises GooglePlacesAPIError.
    NO fake/demo/mock businesses are generated.
    """

    TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

    @property
    def source_name(self) -> str:
        return "google_places"

    @property
    def rate_limit_per_minute(self) -> int:
        return 600

    @property
    def timeout_seconds(self) -> float:
        return 20.0

    async def search(self, request: DiscoveryRequest) -> List[RawDiscoveryResult]:
        api_key = settings.GOOGLE_MAPS_API_KEY
        enabled = settings.GOOGLE_PLACES_ENABLED

        if not enabled or not api_key or not api_key.strip():
            logger.error("Google Places API execution blocked: GOOGLE_MAPS_API_KEY is missing or disabled.")
            raise GooglePlacesAPIError(
                "Google Places API Key is missing or disabled. Set GOOGLE_MAPS_API_KEY in .env to execute real business discovery."
            )

        query_text = f"{request.niche} in {request.geography}"
        if request.sub_niche:
            query_text = f"{request.sub_niche} {request.niche} in {request.geography}"

        max_results = min(request.source_configuration.get("max_results_limit", 100), 50)

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key.strip(),
            "X-Goog-FieldMask": (
                "places.id,places.displayName,places.formattedAddress,"
                "places.nationalPhoneNumber,places.internationalPhoneNumber,"
                "places.rating,places.userRatingCount,places.websiteUri,"
                "places.businessStatus,places.primaryType,places.addressComponents"
            ),
        }

        payload = {
            "textQuery": query_text,
            "maxResultCount": max_results,
        }

        logger.info(f"Executing Google Places (New) Text Search for query: '{query_text}'")

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(self.TEXT_SEARCH_URL, headers=headers, json=payload)

            if response.status_code != 200:
                error_body = response.text
                logger.error(f"Google Places API returned HTTP {response.status_code}: {error_body}")
                raise GooglePlacesAPIError(
                    f"Google Places API error (HTTP {response.status_code}): {error_body[:300]}"
                )

            data = response.json()
            places = data.get("places", [])
            logger.info(f"Google Places API returned {len(places)} real business results for query '{query_text}'")

            results: List[RawDiscoveryResult] = []
            for place in places:
                place_id = place.get("id") or "unknown_place_id"
                display_name = place.get("displayName", {}).get("text", "")
                
                raw_payload = {
                    "place_id": place_id,
                    "name": display_name,
                    "address": place.get("formattedAddress"),
                    "phone": place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber"),
                    "website": place.get("websiteUri"),
                    "rating": place.get("rating"),
                    "user_rating_count": place.get("userRatingCount"),
                    "business_status": place.get("businessStatus"),
                    "primary_type": place.get("primaryType"),
                    "address_components": place.get("addressComponents", []),
                    "provider_source": "google_places_api_v1",
                }

                result = RawDiscoveryResult(
                    source_name=self.source_name,
                    source_identifier=place_id,
                    raw_data=raw_payload,
                    observed_at=datetime.now(timezone.utc),
                    confidence_hint=0.9,
                    licensing_notice="Google Places API Data",
                )
                results.append(result)

            return results

        except httpx.RequestError as exc:
            logger.error(f"Network transport error calling Google Places API: {exc}")
            raise GooglePlacesAPIError(f"Network connection failed calling Google Places API: {exc}")

    async def fetch_details(self, source_identifier: str) -> RawDiscoveryResult:
        # Details endpoint for Place ID
        api_key = settings.GOOGLE_MAPS_API_KEY
        if not api_key:
            raise GooglePlacesAPIError("GOOGLE_MAPS_API_KEY is missing.")

        url = f"https://places.googleapis.com/v1/places/{source_identifier}"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key.strip(),
            "X-Goog-FieldMask": "id,displayName,formattedAddress,nationalPhoneNumber,rating,userRatingCount,websiteUri,businessStatus",
        }

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise GooglePlacesAPIError(f"Failed to fetch place details for {source_identifier}")
            data = response.json()

        return RawDiscoveryResult(
            source_name=self.source_name,
            source_identifier=source_identifier,
            raw_data=data,
            observed_at=datetime.now(timezone.utc),
            confidence_hint=0.95,
        )

    async def check_health(self) -> bool:
        return bool(settings.GOOGLE_MAPS_API_KEY and settings.GOOGLE_PLACES_ENABLED)
