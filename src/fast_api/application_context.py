from dataclasses import dataclass

from core.basic_configuration import EnvConfig
from core.cassandra_service import CassandraConfig
from core.database_repositories import Repositories
from core.identity_configuration import IdentityConfig


@dataclass
class ApplicationContext:
    """
    Holds all initialised application dependencies for the FastAPI lifespan.

    Created once during startup via `build_application_context` and attached
    to `app.state` for injection into request handlers.

    Attributes:
        repositories: Aggregated database repository instances.
        identity: Server identity and version information.
        env_config: Loaded environment configuration.
        cassandra_config: Active Cassandra connection configuration.
    """

    repositories: Repositories
    identity: IdentityConfig
    env_config: EnvConfig
    cassandra_config: CassandraConfig
