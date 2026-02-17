import logging
import sys

import colorlog

from src.core.config import Environment


def setup_logger(environment: Environment) -> None:
    """
    Accepts config arguments explicitly rather than relying on global state.
    """

    handler = colorlog.StreamHandler(sys.stderr)
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s.%(msecs)03d%(reset)s | '
        '%(log_color)s%(levelname)-8s%(reset)s | '
        '%(cyan)s%(name)s:%(funcName)s:%(lineno)d%(reset)s - '
        '%(log_color)s%(message)s%(reset)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'white',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    ))
    logger = logging.getLogger()
    logger.addHandler(handler)

    if environment == Environment.PRODUCTION:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)
