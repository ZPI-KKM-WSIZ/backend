import uvicorn
from fastapi import FastAPI
from loguru import logger

from src.core import config
from src.core.bootstrap_utils import get_trusted_roots, get_github_token, should_run_coordination_mode, setup_logger, \
    get_app_version
from src.core.config import OperatingMode
from src.node_mode.fastapi_factory import create_fastapi_app, register_routes
from src.node_mode.fastapi_settings import FastAPIAppSettings

if __name__ == '__main__':
    # Initial setup
    logger.info("Loading application configuration")
    settings = config.settings
    state = config.state

    env = settings.ENVIRONMENT
    setup_logger(env, settings.paths.LOGS_DIR)

    logger.debug(f'Using environment: {env}')

    # Fetch Trusted roots
    try:
        trusted_roots = get_trusted_roots(env, github_token=get_github_token())
        logger.debug("Trusted root file: {}", trusted_roots)
    except Exception as e:
        logger.error(f"Error while loading trusted roots: {e}")
        if env == config.Environment.PRODUCTION:
            exit(1)
        else:
            raise e

    # Load identity
    server_id = settings.SERVER_ID
    if server_id is None:
        logger.info("SERVER_ID not set. Requesting ID form DB.")
        # TODO: Add code to get server ID from DB

    config.state.load_identity(server_id=server_id, app_version=get_app_version(settings.paths.PROJECT_ROOT),
                               secrets_dir=settings.paths.SECRETS_DIR)

    # Initialize app variables
    app: FastAPI | None = None
    fastapi_settings: FastAPIAppSettings | None = None

    # Set FastAPI configuration
    if should_run_coordination_mode(trusted_roots):
        logger.debug("Found trusted root entry matching this node's public key")
        logger.debug("Loaded configuration: {}", state.coordination_config)
        logger.info("Starting in coordination mode.")

        # Set coordination mode variables
        state.operating_mode = OperatingMode.COORDINATION
        fastapi_settings = FastAPIAppSettings(
            title=f"Coordination Node {settings.SERVER_ID}",
            version=state.app_version,
            summary=f"Coordination FastAPI module of node {settings.SERVER_ID}",
            description=f"This module provides an API for node {settings.SERVER_ID}."
                        f"Responsible for registering new nodes into the system and routing.",
            root_path=str(settings.paths.NODE_MODE)
        )
    else:
        logger.info("Starting in data backend mode")

        # Set backend mode variables
        state.operating_mode = OperatingMode.DATA
        fastapi_settings = FastAPIAppSettings(
            title=f"Data Backend Node {settings.SERVER_ID}",
            version=state.app_version,
            summary=f"Data Backend FastAPI module of node {settings.SERVER_ID}",
            description=f"This module provides an API for node {settings.SERVER_ID}."
                        f"Responsible for handling data from sensors.",
            root_path=str(settings.paths.NODE_MODE)
        )

    app = create_fastapi_app(fast_api_settings=fastapi_settings,
                       operating_mode=state.operating_mode,
                       register_routes=register_routes)

    # Start the FastAPI server using Uvicorn
    if app:
        # You can make host/port configurable via settings if desired
        logger.info("FastAPI server starting on port 8000 in {} mode", state.operating_mode.value)
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        logger.error("Failed to initialize FastAPI application")
        exit(1)
