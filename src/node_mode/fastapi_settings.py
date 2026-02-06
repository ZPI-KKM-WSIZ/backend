from pydantic_settings import BaseSettings
from typing_extensions import Any


class FastAPIAppSettings(BaseSettings):
    """Configuration for the FastAPI module instance."""
    # Metadata
    title: str
    version: str
    summary: str | None = None
    description: str | None = None

    # Documentation
    openapi_url: str = "/openapi.json"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"

    # Operational
    debug: bool = False
    root_path: str = ""
    servers: list[dict[str, Any]] = []
