from fastapi import FastAPI

from src.fast_api import router
from src.fast_api.fastapi_settings import FastAPIAppSettings


def create_fastapi_app(fastapi_settings: FastAPIAppSettings) -> FastAPI:
    """Initializes FastAPI with mode-specific routing."""
    app = FastAPI(
        title=fastapi_settings.title,
        version=fastapi_settings.version,
        summary=fastapi_settings.summary,
        description=fastapi_settings.description,
        openapi_url=fastapi_settings.openapi_url,
        docs_url=fastapi_settings.docs_url,
        redoc_url=fastapi_settings.redoc_url,
        debug=fastapi_settings.debug,
        root_path=fastapi_settings.root_path,
        servers=fastapi_settings.servers
    )

    app.include_router(router.router)

    return app
