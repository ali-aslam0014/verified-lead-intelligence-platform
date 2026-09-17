import uuid
import pytest
from httpx import AsyncClient
from app.models.enums import OpportunityType, TargetStatus, TargetRunStatus
from app.sources.mock_adapter import MockSourceAdapter
from app.sources.base import DiscoveryRequest


@pytest.mark.asyncio
async def test_create_target_success(async_client: AsyncClient):
    payload = {
        "name": "Dental Clinics Austin",
        "niche": "dental",
        "sub_niche": "orthodontics",
        "geography": "Austin, TX",
        "filters": {
            "min_revenue": 100000.0,
            "max_revenue": 5000000.0,
            "min_employees": 5,
            "max_employees": 50,
            "technologies": ["WordPress", "Google Analytics"],
            "keywords": ["dentist", "braces"]
        },
        "opportunity_types": ["NEW_WEBSITE", "SEO"],
        "source_configuration": {
            "enabled_sources": ["google_places", "website_crawler"],
            "max_results_limit": 200
        }
    }

    response = await async_client.post("/api/v1/targets", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["niche"] == "dental"
    assert data["status"] == "ACTIVE"
    assert "id" in data
    assert len(data["opportunity_types"]) == 2


@pytest.mark.asyncio
async def test_create_target_validation_min_greater_than_max(async_client: AsyncClient):
    payload = {
        "name": "Invalid Target",
        "niche": "dental",
        "geography": "Austin, TX",
        "filters": {
            "min_revenue": 5000000.0,
            "max_revenue": 100000.0  # Invalid min > max
        },
        "opportunity_types": ["SEO"]
    }

    response = await async_client.post("/api/v1/targets", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_create_target_validation_empty_opportunity_types(async_client: AsyncClient):
    payload = {
        "name": "Invalid Target",
        "niche": "dental",
        "geography": "Austin, TX",
        "opportunity_types": []  # Invalid empty list
    }

    response = await async_client.post("/api/v1/targets", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_target_crud_lifecycle_and_soft_delete(async_client: AsyncClient):
    # 1. Create Target
    payload = {
        "name": "Plumbers Chicago",
        "niche": "plumbing",
        "geography": "Chicago, IL",
        "opportunity_types": ["LOCAL_SEO"]
    }
    create_res = await async_client.post("/api/v1/targets", json=payload)
    assert create_res.status_code == 201
    target_id = create_res.json()["id"]

    # 2. Get Target
    get_res = await async_client.get(f"/api/v1/targets/{target_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == payload["name"]

    # 3. Update Target
    update_res = await async_client.put(
        f"/api/v1/targets/{target_id}",
        json={"name": "Plumbers Greater Chicago"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Plumbers Greater Chicago"

    # 4. Soft Delete Target
    del_res = await async_client.delete(f"/api/v1/targets/{target_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "CANCELLED"

    # 5. List targets excludes soft deleted by default
    list_res = await async_client.get("/api/v1/targets")
    assert list_res.status_code == 200
    ids = [t["id"] for t in list_res.json()]
    assert target_id not in ids


@pytest.mark.asyncio
async def test_target_run_trigger_and_cancelled_restriction(async_client: AsyncClient):
    # 1. Create Active Target
    create_res = await async_client.post("/api/v1/targets", json={
        "name": "Lawyers Miami",
        "niche": "legal",
        "geography": "Miami, FL",
        "opportunity_types": ["SEO"]
    })
    target_id = create_res.json()["id"]

    # 2. Trigger Target Run
    run_res = await async_client.post(f"/api/v1/targets/{target_id}/runs")
    assert run_res.status_code == 201
    run_data = run_res.json()
    assert run_data["target_id"] == target_id
    assert run_data["status"] in ("QUEUED", "RUNNING", "COMPLETED")
    assert run_data["total_discovered"] >= 0

    # 3. Cancel/Soft Delete Target
    await async_client.delete(f"/api/v1/targets/{target_id}")

    # 4. Trigger Run on Cancelled Target fails with 400
    bad_run_res = await async_client.post(f"/api/v1/targets/{target_id}/runs")
    assert bad_run_res.status_code == 400


@pytest.mark.asyncio
async def test_nonexistent_target_404_responses(async_client: AsyncClient):
    fake_id = uuid.uuid4()
    assert (await async_client.get(f"/api/v1/targets/{fake_id}")).status_code == 404
    assert (await async_client.put(f"/api/v1/targets/{fake_id}", json={"name": "New"})).status_code == 404
    assert (await async_client.delete(f"/api/v1/targets/{fake_id}")).status_code == 404
    assert (await async_client.post(f"/api/v1/targets/{fake_id}/runs")).status_code == 404


@pytest.mark.asyncio
async def test_mock_source_adapter_contract():
    adapter = MockSourceAdapter()
    assert adapter.source_name == "mock_directory_adapter"
    assert adapter.rate_limit_per_minute == 120

    request = DiscoveryRequest(
        niche="dental",
        geography="Austin, TX",
        filters={"min_employees": 5}
    )

    results = await adapter.search(request)
    assert len(results) == 2
    assert results[0].source_name == "mock_directory_adapter"
    assert results[0].source_identifier == "mock_biz_101"
    assert "Apex Dental Specialists" in results[0].raw_data["name"]
    assert results[0].confidence_hint == 0.85
    assert results[0].licensing_notice == "Public Directory License"
