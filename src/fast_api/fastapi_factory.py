import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from federation_repository import FederationRepository
from location_repository import LocationRepository
from readings_repository import ReadingsRepository
from sensor_repository import SensorRepository
from token_repository import TokenRepository

from core.bootstrap_utils import get_app_version
from core.cassandra_service import CassandraConfig, CassandraService
from core.database_repositories import Repositories
from core.env_configuration import get_env_config
from core.environment import Environment
from core.identity_configuration import IdentityConfig
from core.logger_configuration import setup_logger
from core.tailscale_service import TailscaleService
from fast_api.exception_handler import add_exception_handlers
from fast_api.fastapi_settings import FastAPIAppSettings
from fast_api.router import router


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
        server_id = env_values.SERVER_ID
        identity = IdentityConfig(server_id=server_id,
                                  app_version=get_app_version(env_values.paths.PROJECT_ROOT))
        logging.info(f"Server id set to {server_id}")
        logging.debug(f"Loaded node identity: {identity}")

        tailscale_service = TailscaleService(client_id=env_values.tailscale_secrets.TAILSCALE_API_CLIENT_ID,
                                             client_secret=env_values.tailscale_secrets.TAILSCALE_API_CLIENT_SECRET,
                                             tailnet_id=env_values.tailscale_secrets.TAILNET_ID,
                                             environment=working_env)
        logging.info(f"Tailscale service initialized")

        # Load Cassandra configuration
        cassandra_config = CassandraConfig.from_settings(
            contact_points=await tailscale_service.get_cassandra_contact_points(),
            settings=env_values.cassandra_settings)
        logging.info(f"Cassandra config loaded")
        logging.debug(f"Cassandra config: {cassandra_config}")

        cassandra_service = CassandraService(cassandra_config)

        # Load Database repositories
        session = cassandra_service.session
        repositories = Repositories(
            federation_repository=FederationRepository(session),
            location_repository=LocationRepository(session),
            readings_repository=ReadingsRepository(session),
            sensor_repository=SensorRepository(session),
            token_repository=TokenRepository(session),
        )

        # Set fastapi dependency
        app.state.cassandra_config = cassandra_config

        logging.debug(f"Loaded database repos: {repositories}")

        # FastAPI setup
        logging.info("Setting up FastAPI")
        fastapi_settings = FastAPIAppSettings(
            title=f"Air info node: {server_id}",
            version=identity.app_version,
            summary=f"FastAPI module of node {server_id}",
            description=f"Responsible for handling incoming sensor data on node {server_id}.",
        )

        # Set fastapi settings
        app.title = fastapi_settings.title
        app.version = fastapi_settings.version
        app.summary = fastapi_settings.summary
        app.description = fastapi_settings.description

        # Set fastapi dependencies
        app.state.identity = identity
        app.state.env_config = env_values
        app.state.repositories = repositories

        logging.info("Starting the app")
        yield

    app = FastAPI(lifespan=lifespan, debug=(env_values.ENVIRONMENT == Environment.DEVELOPMENT))
    app.include_router(router)
    add_exception_handlers(app)

    return app
