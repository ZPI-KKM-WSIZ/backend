import os
import sys
from enum import Enum
from dotenv import load_dotenv

import loguru


class Environment(Enum):
    production = 0
    development = 1


# Dotenv configuration
load_dotenv()
github_token = os.getenv("GITHUB_TOKEN")

# Application configuration
env = Environment.development
logs_dir = os.path.join(os.getcwd(), 'logs')
trusted_roots_url = f"https://raw.githubusercontent.com/ZPI-KKM-WSIZ/backend/refs/heads/master/trusted_roots.json"



def load_dev_logger(logger: loguru.Logger) -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level="DEBUG",
        diagnose=True,
        colorize=True
    )


def load_prod_logger(logger: loguru.Logger) -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        diagnose=False,
        colorize=True
    )
    logger.add(os.path.join(logs_dir, "app.log"), level="INFO", rotation="1 day")
