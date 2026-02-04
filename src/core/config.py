from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from contracts.data_models.trusted_roots import CoordinationRootV1
from loguru import logger
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Root Calculation ---
CORE_DIR = Path(__file__).resolve().parent
SRC_DIR = CORE_DIR.parent
PROJECT_ROOT_DEFAULT = SRC_DIR.parent


# --- Settings Classes ---

class Environment(Enum):
    production = "production"
    development = "development"


class AppSettings(BaseSettings):
    """
    Immutable Configuration loaded from Env/Defaults.
    """
    APP_NAME: str = "Sensor Coordination Node"
    ENVIRONMENT: Environment = Environment.production

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
    PROJECT_ROOT: Path = Field(default=PROJECT_ROOT_DEFAULT)

    LOGS_DIR: Path | None = None
    SECRETS_DIR: Path | None = None

    model_config = SettingsConfigDict(env_file=SRC_DIR / ".env", extra="ignore")

    def model_post_init(self, __context):
        """Ensure dependent paths are set correctly relative to the final PROJECT_ROOT"""
        if self.LOGS_DIR is None:
            self.LOGS_DIR = self.PROJECT_ROOT / 'logs'
        if self.SECRETS_DIR is None:
            self.SECRETS_DIR = self.PROJECT_ROOT / 'secrets'

        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.SECRETS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class RuntimeState:
    """
    Mutable Application State (Changed during runtime).
    """
    coordination_mode: bool = False
    coordination_config: CoordinationRootV1 | None = None
    server_id: str | None = None
    private_key_path: Path | None = None
    public_key_path: Path | None = None

    def load_identity(self, server_id: str, secrets_dir: Path):
        """Explicitly load identity and compute paths"""
        self.server_id = server_id
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
            "private-key-path": str(private_key_path)}))


# --- Singletons ---
settings = AppSettings()
state = RuntimeState()
