from fastapi import APIRouter

from src.fast_api.api.v1.endpoints.readings import readings_router
from src.fast_api.api.v1.endpoints.health import health_router

router = APIRouter()

# Top level API endpoints
@router.get("/")
def health_check():
    """Health check endpoint for the shared API."""
    return {"status": "ok"}

# Lower level API endpoints
router.include_router(health_router)
router.include_router(readings_router)