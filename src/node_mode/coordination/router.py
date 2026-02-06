from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/coordination", tags=["coordination"])


@router.get("/")
def health_check():
    """Health check endpoint for the coordination API."""
    return {"status": "coordination-mode ok"}
