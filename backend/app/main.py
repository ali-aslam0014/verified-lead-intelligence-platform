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
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Request context middleware (Request ID, execution time, error logging)
app.add_middleware(RequestContextMiddleware)

# CORS middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
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
