import logging

import uvicorn

from src.core.logger_config import setup_logger
from src.fast_api.fastapi_factory import create_fastapi_app
from src.core import config
from src.core.bootstrap_utils import get_app_version
from src.fast_api.fastapi_settings import FastAPIAppSettings

if __name__ == '__main__':
    # Initial setup
    logging.info("Loading application configuration")
    settings = config.settings
    state = config.state

    env = settings.ENVIRONMENT
    setup_logger(env)

    logging.debug(f'Using environment: {env}')

    # Load identity
    server_id = settings.SERVER_ID
    if server_id is None:
        logging.info("SERVER_ID not set. Requesting ID form DB.")
        # TODO: Add code to get server ID from DB

    config.state.load_identity(server_id=server_id, app_version=get_app_version(settings.paths.PROJECT_ROOT))

    logging.info("Starting the app")

    # Set FastAPI variables
    fastapi_settings = FastAPIAppSettings(
        title=f"Air info node: {settings.SERVER_ID}",
        version=state.app_version,
        summary=f"FastAPI module of node {settings.SERVER_ID}",
        description=f"This module provides an API for node {settings.SERVER_ID}."
                    f"Responsible handling incoming sensor data.",
        root_path=""
    )

    app = create_fastapi_app(fastapi_settings)

    # Start the FastAPI server using Uvicorn
    if app:
        logging.info("FastAPI server starting on port 8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        logging.error("Failed to initialize FastAPI application")
        exit(1)
