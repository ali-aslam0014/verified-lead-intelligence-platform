import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness_probe(async_client: AsyncClient):
    response = await async_client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time" in response.headers


@pytest.mark.asyncio
async def test_detailed_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    # Response can be 200 or 503 depending on if DB/Redis are running during local unit tests
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]
    assert "status" in data["services"]["database"]
    assert "latency_ms" in data["services"]["database"]
    assert "status" in data["services"]["redis"]
    assert "latency_ms" in data["services"]["redis"]
