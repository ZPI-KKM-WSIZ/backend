from fastapi import APIRouter, Depends

from src.fast_api.dependencies import get_info_service
from src.fast_api.services.info import InfoService

health_router = APIRouter(prefix="/api/v1")


@health_router.get("/health")
def health_check(info_service: InfoService = Depends(get_info_service)):
    """Health check endpoint for the shared API."""
    return {"status": "ok", "version": info_service.get_app_version()}
