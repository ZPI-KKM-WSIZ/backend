from pydantic import BaseModel
from typing import Any, Self


class FastAPIAppSettingsBuilder:
    """Fluent builder for FastAPIAppSettings.

    Useful when you want to assemble settings conditionally, while still ending up
    with a validated FastAPIAppSettings instance.
    """

    def __init__(self) -> None:
        # Metadata
        self._title: str | None = None
        self._version: str | None = None
        self._summary: str | None = None
        self._description: str | None = None

        # Documentation
        self._openapi_url: str | None = None
        self._docs_url: str | None = None
        self._redoc_url: str | None = None

        # Operational
        self._debug: bool | None = None
        self._root_path: str | None = None
        self._servers: list[dict[str, Any]] | None = None

    def add_title(self, title: str) -> Self:
        self._title = title
        return self

    def add_version(self, version: str) -> Self:
        self._version = version
        return self

    def add_summary(self, summary: str | None) -> Self:
        self._summary = summary
        return self

    def add_description(self, description: str | None) -> Self:
        self._description = description
        return self

    def add_openapi_url(self, openapi_url: str | None) -> Self:
        self._openapi_url = openapi_url
        return self

    def add_docs_url(self, docs_url: str | None) -> Self:
        self._docs_url = docs_url
        return self

    def add_redoc_url(self, redoc_url: str | None) -> Self:
        self._redoc_url = redoc_url
        return self

    def add_debug(self, debug: bool) -> Self:
        self._debug = debug
        return self

    def add_root_path(self, root_path: str) -> Self:
        self._root_path = root_path
        return self

    def add_servers(self, servers: list[dict[str, Any]]) -> Self:
        self._servers = servers
        return self

    def build(self) -> "FastAPIAppSettings":
        """Create a FastAPIAppSettings instance.

        Raises:
            ValueError: if required fields are missing.
        """
        if not self._title:
            raise ValueError("FastAPIAppSettingsBuilder: 'title' must be set")
        if not self._version:
            raise ValueError("FastAPIAppSettingsBuilder: 'version' must be set")

        data: dict[str, Any] = {
            "title": self._title,
            "version": self._version,
        }

        # Only pass optional values if explicitly set, so the model defaults apply.
        if self._summary is not None:
            data["summary"] = self._summary
        if self._description is not None:
            data["description"] = self._description
        if self._openapi_url is not None:
            data["openapi_url"] = self._openapi_url
        if self._docs_url is not None:
            data["docs_url"] = self._docs_url
        if self._redoc_url is not None:
            data["redoc_url"] = self._redoc_url
        if self._debug is not None:
            data["debug"] = self._debug
        if self._root_path is not None:
            data["root_path"] = self._root_path
        if self._servers is not None:
            data["servers"] = self._servers

        return FastAPIAppSettings(**data)


class FastAPIAppSettings(BaseModel):
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