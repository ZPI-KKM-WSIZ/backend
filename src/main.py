import logging
import uuid

import uvicorn

from src.core.cassandra_config import CassandraConfig
from src.core.tailscale_service import TailscaleService
from src.core.logger_config import setup_logger
from src.fast_api.fastapi_factory import create_fastapi_app
from src.core import env_config
from src.core.bootstrap_utils import get_app_version
from src.core.identity_config import IdentityConfig
from src.fast_api.fastapi_settings import FastAPIAppSettings

if __name__ == '__main__':
    # Initial setup
    env_config = env_config.get_env_config()

    working_env = env_config.ENVIRONMENT
    setup_logger(working_env)
    logging.info("Env configuration loaded")
    logging.debug(f'Using environment: {working_env}')

    # Load identity
    server_id = str(uuid.uuid4())
    identity = IdentityConfig(server_id=server_id,
                              app_version=get_app_version(env_config.paths.PROJECT_ROOT))
    logging.info(f"Server id set to {server_id}")
    logging.debug(f"Loaded node identity: {identity}")

    # Load Tailscale configuration
    tailscale_service = TailscaleService(client_id=env_config.tailscale_secrets.TAILSCALE_API_CLIENT_ID,
                                         client_secret=env_config.tailscale_secrets.TAILSCALE_API_CLIENT_SECRET,
                                         tailnet_id=env_config.tailscale_secrets.TAILNET_ID,
                                         environment=working_env)

    # Load Cassandra configuration
    cassandra_config = CassandraConfig.from_settings(
        contact_points=tailscale_service.get_cassandra_contact_points(),
        settings=env_config.cassandra_settings
    )

    logging.info("Starting the app")

    # Set FastAPI variables
    fastapi_settings = FastAPIAppSettings(
        title=f"Air info node: {server_id}",
        version=identity.app_version,
        summary=f"FastAPI module of node {server_id}",
        description=f"This module provides an API for node {server_id}."
                    f"Responsible handling incoming sensor data.",
        root_path=""
    )

    app = create_fastapi_app(fastapi_settings)

    # Add dependencies
    app.state.env_config = env_config
    app.state.identity = identity
    app.state.cassandra_config = cassandra_config

    # Start the FastAPI server using Uvicorn
    if app:
        logging.info("FastAPI server starting on port 8000")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
    else:
        logging.error("Failed to initialize FastAPI application")
        exit(1)
