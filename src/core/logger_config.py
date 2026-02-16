import logging
import sys

from src.core.config import Environment


def setup_logger(environment: Environment) -> None:
    """
    Accepts config arguments explicitly rather than relying on global state.
    """

    if environment == Environment.DEVELOPMENT:
        logging.basicConfig(
            level="DEBUG"
        )
    else:
        logging.basicConfig(
            level="INFO",
        )
