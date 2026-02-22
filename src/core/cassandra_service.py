import asyncio
import ssl
from typing import Any

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT, Session
from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy
from cassandra.policies import LoadBalancingPolicy
from pydantic import SecretStr, BaseModel

from core.basic_configuration import CassandraSettings
from core.network_utils import retry_with_delay_async


class CassandraConfig(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    """
    Configuration for Cassandra database connection.
    
    Attributes:
        contact_points: List of Cassandra node IP addresses or hostnames.
        username: Username for authentication (default: "cassandra").
        password: Password for authentication (default: "cassandra").
        compression: Whether to enable protocol compression.
        load_balancing_policy: Primary load balancing policy class.
        load_balancing_child_policy: Child policy for load balancing.
        local_datacenter: Name of the local datacenter for query routing.
        connect_timeout: Maximum time in seconds to wait for connection.
        request_timeout: Maximum time in seconds to wait for query execution.
        ssl_context: Optional SSL context for secure connections.
        ssl_options: Optional SSL configuration dictionary.
        protocol_version: Cassandra protocol version to use.
        port: Port number for Cassandra connections (default: 9042).
        keyspace: Default keyspace to connect to.
    """
    contact_points: list[str]
    username: str = "cassandra"
    password: SecretStr = SecretStr("cassandra")
    compression: bool | str
    load_balancing_policy: LoadBalancingPolicy = TokenAwarePolicy
    load_balancing_child_policy: LoadBalancingPolicy = DCAwareRoundRobinPolicy
    local_datacenter: str
    connect_timeout: float
    request_timeout: float
    ssl_context: ssl.SSLContext | None = None
    ssl_options: dict[str, Any] | None = None
    protocol_version: int | None = None
    port: int
    keyspace: str

    @classmethod
    def from_settings(cls, contact_points: list[str], settings: CassandraSettings) -> "CassandraConfig":
        """
        Create CassandraConfig from CassandraSettings.
        
        Args:
            contact_points: List of Cassandra node addresses.
            settings: CassandraSettings instance with configuration values.
            
        Returns:
            A new CassandraConfig instance with combined settings.
        """
        return cls(
            contact_points=contact_points,
            **{k.lower(): v for k, v in settings.model_dump().items()}
        )


class CassandraService:
    """
    Service for managing Cassandra database connections and sessions.
    
    This service handles the initialisation and lifecycle of Cassandra
    cluster connections with proper retry logic and configuration.
    
    Attributes:
        created_from: The configuration used to create this service.
        auth_provider: Authentication provider for Cassandra.
        exec_profile: Execution profile with connection policies.
        cluster: The Cassandra cluster instance.
        session: Active database session for query execution.
    """
    created_from: CassandraConfig
    auth_provider: PlainTextAuthProvider
    exec_profile: ExecutionProfile

    cluster: Cluster
    session: Session

    def __init__(self, config: CassandraConfig):
        """
        Initialise the service with configuration.
        
        Note: Use the `create()` factory method instead of direct instantiation.
        
        Args:
            config: CassandraConfig instance with connection settings.
        """
        self.created_from = config

    @classmethod
    async def create(cls, config: CassandraConfig) -> "CassandraService":
        """
        Async factory method for creating a CassandraService instance.
        
        Args:
            config: CassandraConfig instance with connection settings.
            
        Returns:
            Initialized CassandraService with active session.
            
        Raises:
            RuntimeError: If connection to Cassandra fails after retries.
        """
        instance = cls(config)
        await instance._create_session(config)
        return instance

    async def _create_session(self, config: CassandraConfig) -> None:
        """
        Creates a session using configured policies and parameters.
        
        Establishes connection to the Cassandra cluster with retry logic
        and configures load balancing, authentication, and execution profiles.
        
        Args:
            config: CassandraConfig instance with connection settings.
            
        Raises:
            RuntimeError: If connection fails after all retry attempts.
        """
        if config.username and config.password:
            self.auth_provider = PlainTextAuthProvider(
                username=config.username,
                password=config.password.get_secret_value()
            )

        profile = ExecutionProfile(request_timeout=config.request_timeout)
        main_policy = config.load_balancing_policy
        child_policy = config.load_balancing_child_policy
        if not child_policy:
            profile.load_balancing_policy = main_policy
        else:
            profile.load_balancing_policy = main_policy(child_policy(config.local_datacenter))
        self.exec_profile = profile

        cluster_kwargs = dict(
            contact_points=config.contact_points,
            port=config.port,
            auth_provider=self.auth_provider,
            compression=config.compression,
            protocol_version=config.protocol_version,
            connect_timeout=config.connect_timeout,
            ssl_context=config.ssl_context,
            ssl_options=config.ssl_options,
            execution_profiles={EXEC_PROFILE_DEFAULT: self.exec_profile},
        )
        self.cluster = Cluster(**cluster_kwargs)

        async def connect_cassandra():
            return await asyncio.to_thread(self.cluster.connect, config.keyspace)

        self.session = await retry_with_delay_async(async_func=connect_cassandra)
