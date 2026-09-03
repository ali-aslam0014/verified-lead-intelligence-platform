import time
import logging
from celery import Celery
import redis
from app.core.config import settings

logger = logging.getLogger("lead_intel")

celery_app = Celery(
    "lead_intelligence_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)


def check_redis_health() -> dict:
    start_time = time.perf_counter()
    try:
        r = redis.Redis.from_url(settings.REDIS_URL, socket_timeout=3.0)
        pong = r.ping()
        latency_ms = (time.perf_counter() - start_time) * 1000
        if pong:
            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2)
            }
        return {
            "status": "unhealthy",
            "error": "Redis PING did not return True",
            "latency_ms": round(latency_ms, 2)
        }
    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        logger.warning(f"Redis health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "latency_ms": round(latency_ms, 2)
        }
