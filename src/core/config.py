from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Root Calculation ---
CORE_DIR_DEFAULT = Path(__file__).resolve().parent
SRC_DIR_DEFAULT = CORE_DIR_DEFAULT.parent
FASTAPI_DIR_DEFAULT = SRC_DIR_DEFAULT / "fast_api"
PROJECT_ROOT_DEFAULT = SRC_DIR_DEFAULT.parent


# --- Enums ---

class Environment(Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"


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
    """Groups Cassandra's secrets."""
    TAILSCALE_API_CLIENT_ID: SecretStr = Field('TAILSCALE_API_CLIENT_ID')
    TAILSCALE_API_CLIENT_SECRET: SecretStr = Field('TAILSCALE_API_CLIENT_SECRET')
    TAILNET_ID: SecretStr = Field('TAILNET')

    model_config = SettingsConfigDict(env_file=SRC_DIR_DEFAULT / ".env", extra="ignore")


class AppSettings(BaseSettings):
    """
    Immutable Configuration loaded from Env/Defaults.
    """
    # Identity
    SERVER_ID: str | None = None
    APP_NAME: str = "Air info Node"
    ENVIRONMENT: Environment = Environment.PRODUCTION

    # Infrastructure
    API_BASE_URL: str = "http://localhost"  # FIXME: Change to url once we have the endpoint.
    API_PORT: int = 8000

    # Paths
    paths: PathConfig = Field(default_factory=PathConfig)
    tailscale_secrets: TailscaleSecrets = Field(default_factory=TailscaleSecrets)

    model_config = SettingsConfigDict(env_file=SRC_DIR_DEFAULT / ".env", extra="ignore")


@dataclass
class RuntimeState:
    """
    Mutable Application State (Changed during runtime).
    """
    server_id: str | None = None
    app_version: str | None = None

    def load_identity(self, server_id: str, app_version: str):
        """Explicitly load identity and compute paths"""
        self.server_id = server_id
        self.app_version = app_version

        logging.debug("Loaded node identity: {}", dict({
            "id": server_id,
            "app-version": self.app_version
        }))


# --- Singletons ---
settings = AppSettings()
state = RuntimeState()
