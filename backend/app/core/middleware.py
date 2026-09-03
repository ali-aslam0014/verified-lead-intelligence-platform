import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("lead_intel")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Unhandled Exception: {str(exc)}",
                extra={"request_id": request_id, "path": request.url.path, "process_time_ms": round(process_time, 2)},
                exc_info=True
            )
            raise exc

        process_time = (time.perf_counter() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

        # Log request summary
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} ({process_time:.2f}ms)",
            extra={"request_id": request_id, "status_code": response.status_code}
        )

        return response
