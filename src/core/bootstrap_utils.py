import sys
import tomllib
from pathlib import Path

from loguru import logger

from src.core.config import Environment


def setup_logger(environment: Environment, logs_dir: Path) -> None:
    """
    Accepts config arguments explicitly rather than relying on global state.
    """
    logger.remove()

    if environment == Environment.DEVELOPMENT:
        logger.add(
            sys.stdout,
            level="DEBUG",
            diagnose=True,
            colorize=True
        )
    else:
        logger.add(
            sys.stdout,
            level="INFO",
            diagnose=False,
            colorize=True
        )
        # Use the passed logs_dir
        log_file = logs_dir / "app.log"
        logger.add(str(log_file), level="INFO", rotation="1 day")


def get_app_version(root_dir: Path) -> str:
    poetry_path = root_dir / "pyproject.toml"
    with poetry_path.open("rb") as f:
        data = tomllib.load(f)
        version = data["project"]["version"]
    return version
