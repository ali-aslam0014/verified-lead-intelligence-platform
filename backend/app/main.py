from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.middleware import RequestContextMiddleware
from app.api.v1.router import api_router
from app.api.v1.endpoints.health import liveness_check

logger = logging.getLogger("lead_intel")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} in [{settings.ENVIRONMENT}] mode...")
    try:
        from app.core.database import engine
        from app.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema auto-initialized on startup.")
    except Exception as e:
        logger.warning(f"Database schema auto-initialization skipped: {str(e)}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")


class VercelPathFixMiddleware:
    """Middleware to strip '/api/index.py' prefix injected by Vercel rewrites."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            path = scope.get("path", "")
            if path.startswith("/api/index.py"):
                new_path = path[len("/api/index.py"):]
                scope["path"] = new_path if new_path else "/"
            elif path.startswith("/api/index"):
                new_path = path[len("/api/index"):]
                scope["path"] = new_path if new_path else "/"
        await self.app(scope, receive, send)


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Vercel internal path fix middleware
app.add_middleware(VercelPathFixMiddleware)

# Request context middleware (Request ID, execution time, error logging)
app.add_middleware(RequestContextMiddleware)

import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class UniversalCORSMiddleware(BaseHTTPMiddleware):
    """Guarantees CORS headers on all HTTP responses, preflights, and error tracebacks."""
    async def dispatch(self, request: Request, call_next) -> Response:
        origin = request.headers.get("origin") or "*"
        
        if request.method == "OPTIONS":
            response = Response(status_code=204)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(f"Unhandled endpoint exception: {str(exc)}", exc_info=True)
            response = Response(
                content=json.dumps({"detail": str(exc)}),
                status_code=500,
                media_type="application/json"
            )

        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response


# Universal CORS middleware
app.add_middleware(UniversalCORSMiddleware)

# CORS middleware
if settings.CORS_ORIGINS:
    cors_origins = [str(o) for o in settings.CORS_ORIGINS if o != "*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins if cors_origins else ["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_origin_regex=r"https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Root liveness probe
app.add_api_route("/healthz", liveness_check, methods=["GET"], tags=["Health"])

# API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }
