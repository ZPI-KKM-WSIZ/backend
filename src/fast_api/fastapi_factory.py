import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.env_configuration import get_env_config
from src.core.environment import Environment
from src.fast_api.fastapi_settings import FastAPIAppSettings
from src.core.bootstrap_utils import get_app_version
from src.core.cassandra_configuration import CassandraConfig
from src.core.identity_configuration import IdentityConfig
from src.core.logger_configuration import setup_logger
from src.core.tailscale_service import TailscaleService
from src.fast_api.router import router


def create_fastapi_app() -> FastAPI:
    """Initializes FastAPI with mode-specific routing."""
    env_values = get_env_config()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Initial setup
        working_env = env_values.ENVIRONMENT
        setup_logger(working_env)
        logging.info("Env configuration loaded")
        logging.debug(f'Using environment: {working_env}')

        # Load identity
        server_id = str(uuid.uuid4())
        identity = IdentityConfig(server_id=server_id,
                                  app_version=get_app_version(env_values.paths.PROJECT_ROOT))
        logging.info(f"Server id set to {server_id}")
        logging.debug(f"Loaded node identity: {identity}")

        # Load Tailscale configuration
        tailscale_service = TailscaleService(client_id=env_values.tailscale_secrets.TAILSCALE_API_CLIENT_ID,
                                             client_secret=env_values.tailscale_secrets.TAILSCALE_API_CLIENT_SECRET,
                                             tailnet_id=env_values.tailscale_secrets.TAILNET_ID,
                                             environment=working_env)
        logging.info(f"Tailscale service initialized")

        # Load Cassandra configuration
        cassandra_config = CassandraConfig.from_settings(
            contact_points=tailscale_service.get_cassandra_contact_points(),
            settings=env_values.cassandra_settings)
        logging.info(f"Cassandra config loaded")
        logging.debug(f"Cassandra config: {cassandra_config}")

        # FastAPI setup
        logging.info("Setting up FastAPI")
        fastai_settings = FastAPIAppSettings(
            title=f"Air info node: {server_id}",
            version=identity.app_version,
            summary=f"FastAPI module of node {server_id}",
            description=f"Responsible for handling incoming sensor data on node {server_id}.",
        )

        # Set fastapi settings
        app.title = fastai_settings.title
        app.version = fastai_settings.version
        app.summary = fastai_settings.summary
        app.description = fastai_settings.description

        # Set fastapi dependencies
        app.state.identity = identity
        app.state.env_config = env_values
        app.state.cassandra_config = cassandra_config

        logging.info("Starting the app")
        yield

    app = FastAPI(lifespan=lifespan, debug=(env_values.ENVIRONMENT == Environment.DEVELOPMENT))
    app.include_router(router)

    return app
