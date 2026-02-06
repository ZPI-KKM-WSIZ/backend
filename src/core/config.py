from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from contracts.data_models.trusted_roots import CoordinationRootV1
from loguru import logger
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Root Calculation ---
CORE_DIR_DEFAULT = Path(__file__).resolve().parent
SRC_DIR_DEFAULT = CORE_DIR_DEFAULT.parent
NODE_MODE_DEFAULT = CORE_DIR_DEFAULT / "node_mode"
COORDINATION_DEFAULT = NODE_MODE_DEFAULT / "coordination"
DATA_BACKEND_DEFAULT = NODE_MODE_DEFAULT / "data_backend"
SHARED_DEFAULT = NODE_MODE_DEFAULT / "shared"
PROJECT_ROOT_DEFAULT = SRC_DIR_DEFAULT.parent


# --- Enums ---

class Environment(Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"


class OperatingMode(Enum):
    DATA = "data"
    COORDINATION = "coordination"


# --- Settings Classes ---

class PathConfig(BaseSettings):
    """
    Groups all path-related configurations.
    """
    PROJECT_ROOT: Path = Field(default=PROJECT_ROOT_DEFAULT)
    CORE_DIR: Path = Field(default=CORE_DIR_DEFAULT)
    SRC_DIR: Path = Field(default=SRC_DIR_DEFAULT)
    NODE_MODE: Path = Field(default=NODE_MODE_DEFAULT)
    COORDINATION: Path = Field(default=COORDINATION_DEFAULT)
    DATA_BACKEND: Path = Field(default=DATA_BACKEND_DEFAULT)
    SHARED: Path = Field(default=SHARED_DEFAULT)

    LOGS_DIR: Path | None = None
    SECRETS_DIR: Path | None = None

    model_config = SettingsConfigDict(env_file=SRC_DIR_DEFAULT / ".env", extra="ignore")

    def model_post_init(self, __context):
        """Ensure dependent paths are set relative to PROJECT_ROOT and create dirs."""
        if self.LOGS_DIR is None:
            self.LOGS_DIR = self.PROJECT_ROOT / 'logs'
        if self.SECRETS_DIR is None:
            self.SECRETS_DIR = self.PROJECT_ROOT / 'secrets'

        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.SECRETS_DIR.mkdir(parents=True, exist_ok=True)


class AppSettings(BaseSettings):
    """
    Immutable Configuration loaded from Env/Defaults.
    """
    APP_NAME: str = "Sensor Coordination Node"
    ENVIRONMENT: Environment = Environment.PRODUCTION

    # Infrastructure
    TRUSTED_ROOTS_URL: str = "https://raw.githubusercontent.com/ZPI-KKM-WSIZ/backend/refs/heads/master/trusted_roots.json"
    # DATABASE_URL: str
    # REDIS_URL: str | None = None

    # Secrets
    GITHUB_TOKEN: SecretStr | None = None
    SERVER_ID: str | None = None
    COORD_PUB_KEY_PATH: Path | None = None
    COORD_PRIV_KEY_PATH: Path | None = None

    # Paths
    paths: PathConfig = Field(default_factory=PathConfig)

    model_config = SettingsConfigDict(env_file=SRC_DIR_DEFAULT / ".env", extra="ignore")


@dataclass
class RuntimeState:
    """
    Mutable Application State (Changed during runtime).
    """
    operating_mode: OperatingMode = OperatingMode.DATA
    coordination_config: CoordinationRootV1 | None = None
    server_id: str | None = None
    private_key_path: Path | None = None
    public_key_path: Path | None = None
    app_version: str | None = None

    def load_identity(self, server_id: str, app_version, secrets_dir: Path):
        """Explicitly load identity and compute paths"""
        self.server_id = server_id
        self.app_version = app_version
        private_key_path = secrets_dir / server_id
        public_key_path = secrets_dir / f"{server_id}.pub"

        if private_key_path.exists() and public_key_path.exists():
            self.private_key_path = private_key_path
            self.public_key_path = public_key_path
        else:
            logger.error("Missing keys:Expected private key at {} and public key at {}",
                         private_key_path,
                         public_key_path)
        logger.debug("Loaded node identity: {}", dict({
            "id": server_id,
            "public-key-path": str(public_key_path),
            "private-key-path": str(private_key_path),
            "app-version": self.app_version
        }))


# --- Singletons ---
settings = AppSettings()
state = RuntimeState()
