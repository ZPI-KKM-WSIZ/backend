from functools import lru_cache
from pathlib import Path

from cassandra import ProtocolVersion
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any

from core.environment import Environment

# --- Root Calculation ---
CORE_DIR_DEFAULT = Path(__file__).resolve().parent
SRC_DIR_DEFAULT = CORE_DIR_DEFAULT.parent
FASTAPI_DIR_DEFAULT = SRC_DIR_DEFAULT / "fast_api"
PROJECT_ROOT_DEFAULT = SRC_DIR_DEFAULT.parent
ENV_FILE_PATH = SRC_DIR_DEFAULT / ".env"


# --- Settings Classes ---

class PathConfig(BaseSettings):
    """
    Groups all path-related configurations.
    """
    CORE_DIR: Path = Field(default=CORE_DIR_DEFAULT)
    SRC_DIR: Path = Field(default=SRC_DIR_DEFAULT)
    FASTAPI_DIR: Path = Field(default=FASTAPI_DIR_DEFAULT)
    PROJECT_ROOT: Path = Field(default=PROJECT_ROOT_DEFAULT)

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, extra="ignore")


class TailscaleSecrets(BaseSettings):
    """Groups Tailscale's secrets."""
    TAILSCALE_API_CLIENT_ID: SecretStr
    TAILSCALE_API_CLIENT_SECRET: SecretStr
    TAILNET_ID: SecretStr

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, extra="ignore")


class CassandraSettings(BaseSettings):
    """Groups Cassandra's settings."""
    USERNAME: str | None = None
    PASSWORD: SecretStr | None = None
    COMPRESSION: bool | str = False
    LOCAL_DATACENTER: str | None = "datacenter1"
    CONNECT_TIMEOUT: float = 5.0
    REQUEST_TIMEOUT: float = 10.0
    SSL_CONTEXT: str | None = None
    SSL_OPTIONS: dict[str, Any] | None = None
    PROTOCOL_VERSION: int = ProtocolVersion.V4
    PORT: int = 9042
    KEYSPACE: str = "air_info"

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, extra="ignore")


class EnvConfig(BaseSettings):
    """
    Immutable Configuration loaded from Env/Defaults.
    """
    # Identity
    SERVER_ID: str
    APP_NAME: str = "Air info Node"
    ENVIRONMENT: Environment = Environment.PRODUCTION

    # Infrastructure
    API_BASE_URL: str
    API_PORT: int = 8000

    # Paths
    paths: PathConfig = Field(default_factory=PathConfig)
    tailscale_secrets: TailscaleSecrets = Field(default_factory=TailscaleSecrets)
    cassandra_settings: CassandraSettings = Field(default_factory=CassandraSettings)

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, extra="ignore")


@lru_cache(maxsize=1)
def get_env_config() -> EnvConfig:
    """Returns a cached singleton instance of EnvConfig"""
    return EnvConfig()
