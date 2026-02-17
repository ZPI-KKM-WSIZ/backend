import typing
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Any

if typing.TYPE_CHECKING:
    from src.core.cassandra_config import CassandraConfig

# --- Root Calculation ---
CORE_DIR_DEFAULT = Path(__file__).resolve().parent
SRC_DIR_DEFAULT = CORE_DIR_DEFAULT.parent
FASTAPI_DIR_DEFAULT = SRC_DIR_DEFAULT / "fast_api"
PROJECT_ROOT_DEFAULT = SRC_DIR_DEFAULT.parent


# --- Enums ---

class Environment(Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TESTING = "testing"


# --- Settings Classes ---

class PathConfig(BaseSettings):
    """
    Groups all path-related configurations.
    """
    CORE_DIR: Path = Field(default=CORE_DIR_DEFAULT)
    SRC_DIR: Path = Field(default=SRC_DIR_DEFAULT)
    FASTAPI_DIR: Path = Field(default=FASTAPI_DIR_DEFAULT)
    PROJECT_ROOT: Path = Field(default=PROJECT_ROOT_DEFAULT)

    model_config = SettingsConfigDict(env_file=SRC_DIR_DEFAULT / ".env", extra="ignore")


class TailscaleSecrets(BaseSettings):
    """Groups Tailscale's secrets."""
    TAILSCALE_API_CLIENT_ID: SecretStr
    TAILSCALE_API_CLIENT_SECRET: SecretStr
    TAILNET_ID: SecretStr

    model_config = SettingsConfigDict(env_file=SRC_DIR_DEFAULT / ".env", extra="ignore")

class CassandraSettings(BaseSettings):
    """Groups Cassandra's settings."""
    USERNAME: str | None = None
    PASSWORD: SecretStr | None = None
    COMPRESSION: bool | str = False
    LOCAL_DATACENTER: str | None = None
    CONNECT_TIMEOUT: float = 5.0
    REQUEST_TIMEOUT: float = 10.0
    SSL_CONTEXT: str | None = None
    SSL_OPTIONS: dict[str, Any] | None = None
    PROTOCOL_VERSION: int = 66
    PORT: int | int = 9042
    KEYSPACE: str = "air_info"

    model_config = SettingsConfigDict(env_file=SRC_DIR_DEFAULT / ".env", extra="ignore")

class AppSettings(BaseSettings):
    """
    Immutable Configuration loaded from Env/Defaults.
    """
    # Identity
    APP_NAME: str = "Air info Node"
    ENVIRONMENT: Environment = Environment.PRODUCTION

    # Infrastructure
    API_BASE_URL: str
    API_PORT: int = 8000

    # Paths
    paths: PathConfig = Field(default_factory=PathConfig)
    tailscale_secrets: TailscaleSecrets = Field(default_factory=TailscaleSecrets)
    cassandra_settings: CassandraSettings = Field(default_factory=CassandraSettings)

    model_config = SettingsConfigDict(env_file=SRC_DIR_DEFAULT / ".env", extra="ignore")


@dataclass
class RuntimeState:
    """
    Mutable Application State (Changed during runtime).
    """
    server_id: str | None = None
    app_version: str | None = None
    cassandra_config: CassandraConfig | None = None

    def load_identity(self, server_id: str, app_version: str):
        """Explicitly load identity and compute paths"""
        self.server_id = server_id
        self.app_version = app_version

    def load_cassandra_config(self, cassandra_config: CassandraConfig):
        self.cassandra_config = cassandra_config


# --- Singletons ---
settings = AppSettings()
state = RuntimeState()
