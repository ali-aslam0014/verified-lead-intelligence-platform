from datetime import datetime, timezone
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field
from app.core.database import check_database_health
from app.core.celery_app import check_redis_health

router = APIRouter()


class ComponentHealth(BaseModel):
    status: str = Field(..., description="Status of component: healthy or unhealthy")
    latency_ms: float = Field(..., description="Response latency in milliseconds")
    error: str | None = Field(None, description="Error message if unhealthy")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall application status: healthy or degraded")
    timestamp: str = Field(..., description="UTC ISO timestamp of health check")
    services: dict[str, ComponentHealth] = Field(..., description="Status breakdown of infrastructure components")


@router.get("/healthz", summary="Basic Liveness Probe")
async def liveness_check():
    """Simple liveness probe endpoint returning HTTP 200 OK."""
    return {"status": "ok"}


@router.get("/health", response_model=HealthResponse, summary="Detailed Application & Infrastructure Health")
async def detailed_health_check(response: Response):
    """
    Performs real-time checks on system infrastructure components:
    - PostgreSQL database connectivity & latency (`SELECT 1`)
    - Redis cache/queue connectivity & latency (`PING`)
    """
    db_health = await check_database_health()
    redis_health = check_redis_health()

    services = {
        "database": ComponentHealth(**db_health),
        "redis": ComponentHealth(**redis_health),
    }

    is_all_healthy = all(svc["status"] == "healthy" for svc in [db_health, redis_health])
    overall_status = "healthy" if is_all_healthy else "degraded"

    if not is_all_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        services=services
    )
