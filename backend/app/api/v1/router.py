from fastapi import APIRouter
from app.api.v1.endpoints import health, targets

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(targets.router, prefix="/targets", tags=["Targets"])
