import logging
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from cassandra import ProtocolVersion
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.environment import Environment

_env_file: str | None = os.environ.get("ENV_FILE", ".env") or None


# ---------------------------------------------------------------------------
# PathConfig
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PathConfig:
    root_dir: Path
    src_dir: Path = field(init=False)
    core_dir: Path = field(init=False)
    fastapi_dir: Path = field(init=False)
    env_file: Path = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "src_dir", self.root_dir / "src")
        object.__setattr__(self, "core_dir", self.root_dir / "src" / "core")
        object.__setattr__(self, "fastapi_dir", self.root_dir / "src" / "fast_api")
        object.__setattr__(self, "env_file", self.src_dir / ".env")

    @classmethod
    def build(cls, root_dir: Path | None = None) -> "PathConfig":
        return cls(root_dir=root_dir or cls._find_root())

    @staticmethod
    def _find_root() -> Path:
        for parent in Path(__file__).resolve().parents:
            try:
                entries = {f.lower() for f in os.listdir(parent)}
            except (OSError, PermissionError):
                logging.exception("Error accessing directory: %s", parent)
                continue
            if {"readme.md", "poetry.lock", "pyproject.toml"} & entries:
                return parent
        raise FileNotFoundError("No project root markers found")


# ---------------------------------------------------------------------------
# Env values
# ---------------------------------------------------------------------------

class TailscaleSecrets(BaseModel):
    """Tailscale OAuth credentials."""
    TAILSCALE_API_CLIENT_ID: SecretStr
    TAILSCALE_API_CLIENT_SECRET: SecretStr
    TAILNET_ID: SecretStr


class CassandraSettings(BaseModel):
    """Cassandra connection settings."""
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


class EnvConfig(BaseSettings):
    """
    Application configuration loaded from an environment / .env file.

    Nested groups are populated via double-underscore delimiter:
        TAILSCALE__TAILNET_ID=...
        CASSANDRA__PORT=9042
    """

    # Identity
    SERVER_ID: str
    APP_NAME: str = "Air info Node"
    ENVIRONMENT: Environment = Environment.PRODUCTION

    # Infrastructure
    API_BASE_URL: str
    API_PORT: int = 8000

    # Nested groups — populated via TAILSCALE__* and CASSANDRA__* env vars
    TAILSCALE: TailscaleSecrets
    CASSANDRA: CassandraSettings

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


# ---------------------------------------------------------------------------
# Getters
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_path_config() -> PathConfig:
    """
    Cached singleton PathConfig.
    Call clear_path_config_cache() to force a reload in tests.
    """
    return PathConfig.build()


def clear_path_config_cache() -> None:
    get_path_config.cache_clear()


# noinspection PyArgumentList
@lru_cache(maxsize=1)
def get_env_config() -> EnvConfig:
    """
    Cached singleton EnvConfig.

    Reads from environment variables and the .env file in the working
    directory (i.e. the project root when launched normally).
    Call clear_env_config_cache() to force a reload in tests.
    """
    return EnvConfig()


def clear_env_config_cache() -> None:
    """Reset configuration cache (for use in tests)."""
    get_env_config.cache_clear()
