from fastapi import APIRouter, Depends

from fast_api.dependencies import get_identity_service
from fast_api.services.identity_service import IdentityService

health_router = APIRouter(prefix="/api/v1")


@health_router.get("/health")
def health_check(identity_service: IdentityService = Depends(get_identity_service)):
    """
    Health check endpoint returning service status and identity.
    
    Args:
        identity_service: Injected identity service providing server info.
        
    Returns:
        Dict containing status, version, and server identity.
    """
    return {"status": "ok",
            "version": identity_service.get_app_version(),
            "identity": identity_service.identity.server_id}
