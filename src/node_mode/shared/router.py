from fastapi import APIRouter, Depends

from src.node_mode.shared.dependencies import get_node_service
from src.node_mode.shared.services.operating_mode import SharedNodeService

router = APIRouter(prefix="/api/v1", tags=["shared"])


@router.get("/")
def health_check(service: SharedNodeService = Depends(get_node_service)):
    """Health check endpoint for the shared API."""
    return {"status": "ok", "version": service.get_app_version(), "mode": service.get_operating_mode()}
