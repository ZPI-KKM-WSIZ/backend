import ssl

from pydantic import SecretStr, BaseModel
from typing import Any

from core.env_configuration import CassandraSettings


class CassandraConfig(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    """Configuration for Cassandra database connection."""
    contact_points: list[str]
    username: str | None = None
    password: SecretStr | None = None
    compression: bool | str
    local_datacenter: str | None = None
    connect_timeout: float
    request_timeout: float
    ssl_context: ssl.SSLContext | None = None
    ssl_options: dict[str, Any] | None = None
    protocol_version: int
    port: int
    keyspace: str

    @classmethod
    def from_settings(cls, contact_points: list[str], settings: CassandraSettings) -> CassandraConfig:
        """Create CassandraConfig from CassandraSettings"""
        return cls(
            contact_points=contact_points,
            **{k.lower(): v for k, v in settings.model_dump().items()}
        )
