import ssl
from typing import Any

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT, Session
from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy
from cassandra.policies import LoadBalancingPolicy
from pydantic import SecretStr, BaseModel

from core.env_configuration import CassandraSettings


class CassandraConfig(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    """Configuration for Cassandra database connection."""
    contact_points: list[str]
    username: str | None = None
    password: SecretStr | None = None
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
        """Create CassandraConfig from CassandraSettings"""
        return cls(
            contact_points=contact_points,
            **{k.lower(): v for k, v in settings.model_dump().items()}
        )


class CassandraService:
    created_from: CassandraConfig
    auth_provider: PlainTextAuthProvider
    exec_profile: ExecutionProfile

    cluster: Cluster
    session: Session

    def __init__(self, config: CassandraConfig):
        self.created_from = config
        self._create_session(config)


    def _create_session(self, config: CassandraConfig) -> None:
        """Creates a session using configured policies and parameters"""
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
        self.session = self.cluster.connect(config.keyspace)
