from fastapi import APIRouter
from app.api.v1.endpoints import health, targets, businesses

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(targets.router, prefix="/targets", tags=["Targets"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["Businesses"])
