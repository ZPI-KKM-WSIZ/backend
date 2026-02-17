import logging
import uuid

import uvicorn

from src.core.logger_config import setup_logger
from src.fast_api.fastapi_factory import create_fastapi_app
from src.core import config
from src.core.bootstrap_utils import get_app_version
from src.fast_api.fastapi_settings import FastAPIAppSettings

if __name__ == '__main__':
    # Initial setup
    settings = config.settings
    state = config.state

    env = settings.ENVIRONMENT
    setup_logger(env)
    logging.info("Application configuration loaded")

    logging.debug(f'Using environment: {env}')

    # Load identity
    server_id = uuid.uuid4()
    logging.info(f"Server id set to {server_id}")

    config.state.load_identity(server_id=server_id, app_version=get_app_version(settings.paths.PROJECT_ROOT))
    logging.debug(f"Loaded node identity: {{id: {state.server_id}, app-version: {state.app_version}}}")

    logging.info("Starting the app")

    # Set FastAPI variables
    fastapi_settings = FastAPIAppSettings(
        title=f"Air info node: {server_id}",
        version=state.app_version,
        summary=f"FastAPI module of node {server_id}",
        description=f"This module provides an API for node {server_id}."
                    f"Responsible handling incoming sensor data.",
        root_path=""
    )

    app = create_fastapi_app(fastapi_settings)

    # Start the FastAPI server using Uvicorn
    if app:
        logging.info("FastAPI server starting on port 8000")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
    else:
        logging.error("Failed to initialize FastAPI application")
        exit(1)
