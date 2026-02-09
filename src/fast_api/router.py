from fastapi import APIRouter, Depends

from fast_api.dependencies import get_node_service
from fast_api.services.info import InfoService

router = APIRouter(prefix="/api/v1", tags=["data"])


@router.get("/")
def health_check(info_service: InfoService = Depends(get_node_service)):
    """Health check endpoint for the shared API."""
    return {"status": "ok", "version": info_service.get_app_version()}
