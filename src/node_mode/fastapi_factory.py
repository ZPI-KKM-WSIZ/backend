from fastapi import FastAPI
from typing import Callable

from src.core.config import OperatingMode
from src.node_mode.fastapi_settings import FastAPIAppSettings


def register_routes(app: FastAPI, mode: OperatingMode) -> None:
    """Conditionally register routes based on the operating mode."""

    if mode == OperatingMode.COORDINATION:
        from src.node_mode.coordination import router as coord_routers
        app.include_router(coord_routers.router)

    elif mode == OperatingMode.DATA:
        from src.node_mode.data_backend import router as data_routers
        app.include_router(data_routers.router)

    # Shared routes (health checks, metrics) can go here
    from src.node_mode.shared import router
    app.include_router(router.router)


def create_fastapi_app(
        fast_api_settings: FastAPIAppSettings,
        operating_mode: OperatingMode,
        register_routes: Callable[[FastAPI, OperatingMode], None]
) -> FastAPI:
    """Initializes FastAPI with mode-specific routing."""
    app = FastAPI(
        title=fast_api_settings.title,
        version=fast_api_settings.version,
        summary=fast_api_settings.summary,
        description=fast_api_settings.description,
        openapi_url=fast_api_settings.openapi_url,
        docs_url=fast_api_settings.docs_url,
        redoc_url=fast_api_settings.redoc_url,
        debug=fast_api_settings.debug,
        root_path=fast_api_settings.root_path,
        servers=fast_api_settings.servers
    )

    # Register mode-specific routes
    register_routes(app, operating_mode)

    return app
