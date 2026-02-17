from fastapi import APIRouter, Depends

from src.fast_api.dependencies import get_info_service
from src.fast_api.services.identity import IdentityService

health_router = APIRouter(prefix="/api/v1")


@health_router.get("/health")
def health_check(identity_service: IdentityService = Depends(get_info_service)):
    """Health check endpoint for the shared API."""
    return {"status": "ok",
            "version": identity_service.get_app_version(),
            "identity": identity_service.identity.server_id}
