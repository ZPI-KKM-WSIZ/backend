from fastapi import APIRouter

from fast_api.api.v1.endpoints import health

router = APIRouter()

# Top level API endpoints
@router.get("/")
def health_check():
    """Health check endpoint for the shared API."""
    return {"status": "ok"}

# Lower level API endpoints
router.include_router(health.router)