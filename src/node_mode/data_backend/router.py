from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["data"])


@router.get("/")
def health_check():
    """Health check endpoint for the data backend API."""
    return {"status": "data-mode ok"}
