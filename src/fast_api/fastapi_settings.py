from typing import Any

from pydantic import BaseModel


class FastAPIAppSettings(BaseModel):
    """
    Configuration for the FastAPI application instance.

    Attributes:
        title: Title of the API, shown in the auto-generated docs.
        version: Application version string.
        summary: Short summary shown in the API docs.
        description: Longer description shown in the API docs.
        openapi_url: URL path to the OpenAPI schema (default: "/openapi.json").
        docs_url: URL path to the Swagger UI (default: "/docs").
        redoc_url: URL path to the ReDoc UI (default: "/redoc").
        debug: Whether to enable debug mode (default: False).
        root_path: ASGI root path, useful behind a reverse proxy (default: "").
        servers: List of server objects for the OpenAPI schema (default: []).
    """

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
