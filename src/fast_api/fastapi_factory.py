import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from federation_repository import FederationRepository
from location_repository import LocationRepository
from readings_repository import ReadingsRepository
from sensor_repository import SensorRepository
from token_repository import TokenRepository

from core.basic_configuration import get_env_config, EnvConfig, get_path_config
from core.bootstrap_utils import get_app_version
from core.cassandra_service import CassandraConfig, CassandraService
from core.database_repositories import Repositories
from core.environment import Environment
from core.identity_configuration import IdentityConfig
from core.logger_configuration import setup_logger
from core.tailscale_service import TailscaleService
from fast_api.application_context import ApplicationContext
from fast_api.exception_handler import add_exception_handlers
from fast_api.fastapi_settings import FastAPIAppSettings
from fast_api.router import router


async def build_application_context(env_config: EnvConfig,
                                    tailscale_service: TailscaleService = None,
                                    cassandra_service: CassandraService = None) -> ApplicationContext:
    """
    Initialises all core dependencies and return a populated ApplicationContext.

    Builds identity, Tailscale service, Cassandra connection, and all database
    repositories. Both `tailscale_service` and `cassandra_service` can be
    injected directly (e.g. in tests) to bypass their normal initialisation.

    Args:
        env_config: Loaded environment configuration.
        tailscale_service: Optional pre-built TailscaleService. If omitted,
            one is constructed from `env_config`.
        cassandra_service: Optional pre-built CassandraService. If omitted,
            contact points are fetched via Tailscale and a session is created.

    Returns:
        A fully populated ApplicationContext ready to attach to app state.

    Raises:
        RuntimeError: If Cassandra contact points cannot be retrieved or the
            database session cannot be established.
    """

    logging.debug(f"Building application context from environment: {env_config}")
    identity: IdentityConfig
    repositories: Repositories
    cassandra_config: CassandraConfig

    # ============================
    # Load identity
    # ============================
    server_id = env_config.SERVER_ID
    app_version = get_app_version(get_path_config().root_dir)
    identity = IdentityConfig(server_id=server_id, app_version=app_version)
    logging.info(f"Server id set to {server_id}")
    logging.debug(f"Loaded node identity: {identity}")

    # ============================
    # Build Tailscale service
    # ============================
    if not tailscale_service:
        working_env = env_config.ENVIRONMENT
        tailscale_service = TailscaleService(client_id=env_config.TAILSCALE.TAILSCALE_API_CLIENT_ID,
                                             client_secret=env_config.TAILSCALE.TAILSCALE_API_CLIENT_SECRET,
                                             tailnet_id=env_config.TAILSCALE.TAILNET_ID,
                                             environment=working_env)
        logging.info("Tailscale service initialized")
        logging.debug(f"TailscaleService: {TailscaleService}")

    # ============================
    # Load Cassandra configuration
    # ============================
    if not cassandra_service:
        cassandra_config = CassandraConfig.from_settings(
            contact_points=await tailscale_service.get_cassandra_contact_points(),
            settings=env_config.CASSANDRA)
        logging.info("Cassandra config loaded")
        logging.debug(f"Cassandra config: {cassandra_config}")

        cassandra_service = await CassandraService.create(cassandra_config)
        logging.info("CassandraService initialized")
        logging.debug(f"CassandraService: {CassandraService}")

    # ============================
    # Load Database repositories
    # ============================
    session = cassandra_service.session
    token_repo = TokenRepository(session)
    repositories = Repositories(
        federation_repository=FederationRepository(session, token_repo),
        location_repository=LocationRepository(session),
        readings_repository=ReadingsRepository(session),
        sensor_repository=SensorRepository(session),
        token_repository=token_repo,
    )
    logging.info("Repositories loaded")
    logging.debug(f"Loaded database repos: {repositories}")

    return ApplicationContext(
        repositories=repositories,
        identity=identity,
        env_config=env_config,
        cassandra_config=cassandra_service.created_from
    )


def create_fastapi_app(env_config: EnvConfig | None = None) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Registers the router, exception handlers, and an async lifespan that
    bootstraps all dependencies on startup and tears them down on shutdown.
    Debug mode is enabled automatically in the development environment.

    Args:
        env_config: Optional pre-loaded EnvConfig. If omitted, the cached
            singleton from `get_env_config()` is used.

    Returns:
        A fully configured FastAPI application instance ready to serve requests.
    """
    if not env_config:
        env_config = get_env_config()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # ============================
        # Initial setup
        # ============================
        working_env = env_config.ENVIRONMENT
        setup_logger(working_env)
        logging.info("Env configuration loaded")
        logging.debug(f'Using environment: {working_env}')

        app_context = await build_application_context(env_config)
        identity = app_context.identity
        repositories = app_context.repositories
        cassandra_config = app_context.cassandra_config

        # ============================
        # FastAPI setup
        # ============================
        logging.info("Setting up FastAPI")
        fastapi_settings = FastAPIAppSettings(
            title=f"Air info node: {identity.server_id}",
            version=identity.app_version,
            summary=f"FastAPI module of node {identity.server_id}",
            description=f"Responsible for handling incoming sensor data on node {identity.server_id}.",
        )

        # Set fastapi settings
        app.title = fastapi_settings.title
        app.version = fastapi_settings.version
        app.summary = fastapi_settings.summary
        app.description = fastapi_settings.description

        # Set fastapi dependencies
        app.state.identity = identity
        app.state.env_config = env_config
        app.state.repositories = repositories
        app.state.cassandra_config = cassandra_config

        logging.info("Starting the app")
        yield

    app = FastAPI(lifespan=lifespan, debug=(env_config.ENVIRONMENT == Environment.DEVELOPMENT))
    app.include_router(router)
    add_exception_handlers(app)

    return app
