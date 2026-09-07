import pytest
import uuid
from app.sources.base import DiscoveryRequest
from app.sources.live_google_places import LiveGooglePlacesAdapter
from app.services.resolver import BusinessResolver

@pytest.mark.asyncio
async def test_live_google_places_adapter_search():
    adapter = LiveGooglePlacesAdapter()
    req = DiscoveryRequest(
        niche="Dentist Practice",
        geography="New York, NY",
        source_configuration={"max_results_limit": 5}
    )
    
    results = await adapter.search(req)
    assert isinstance(results, list)
    assert len(results) > 0
    
    first = results[0]
    assert first.source_name == "live_google_places"
    assert "name" in first.raw_data
    assert "phone" in first.raw_data
    assert "has_website" in first.raw_data

@pytest.mark.asyncio
async def test_resolver_preserves_no_website_opportunity_signal(async_session):
    adapter = LiveGooglePlacesAdapter()
    results = adapter._generate_real_city_directory("Dental Clinic", "New York, NY")
    
    # Find item without website
    no_website_item = next(r for r in results if r.raw_data.get("has_website") is False)
    
    # Ensure unique place ID for test isolation
    no_website_item.source_identifier = f"test_no_web_{uuid.uuid4().hex}"
    
    resolver = BusinessResolver()
    async with async_session() as db:
        business, is_new = await resolver.resolve_record(
            db=db,
            raw_result=no_website_item
        )
        await db.commit()
    
        assert business is not None
        assert is_new is True
        assert business.name == no_website_item.raw_data["name"]
        assert business.phone is not None
