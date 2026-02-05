import json
import sys
import urllib.request
from http.client import HTTPException
from pathlib import Path

from contracts.data_models.trusted_roots import CoordinationRootV1
from loguru import logger
from pydantic import SecretStr

from src.core.config import settings, Environment, state


def get_github_token() -> str | None:
    github_token = settings.GITHUB_TOKEN
    if github_token is None:
        logger.warning("GITHUB_TOKEN not set. If there is issue downloading trusted roots, this may be the reason.")
    else:
        logger.debug('GitHub token found')
    return github_token


def get_trusted_roots(environment: Environment, use_local: bool = None,
                      github_token: SecretStr | None = None) -> dict:
    if use_local is None:
        if environment == Environment.DEVELOPMENT:
            use_local = True
        else:
            use_local = False

    if not use_local:
        return get_trusted_roots_github(github_token)
    else:
        return get_trusted_roots_local()


def get_trusted_roots_local() -> dict:
    trust_roots_file_path = Path.joinpath(settings.PROJECT_ROOT, 'trusted_roots.json')
    logger.info("Fetching trusted roots from local file: {}", trust_roots_file_path)

    with open(trust_roots_file_path, "r") as f:
        trusted_roots = json.load(f)
        return trusted_roots


def get_trusted_roots_github(github_token: SecretStr | None = None) -> dict:
    trusted_roots_url = settings.TRUSTED_ROOTS_URL
    logger.info('Fetching trusted roots from url: {}', trusted_roots_url)

    req = urllib.request.Request(trusted_roots_url)
    if github_token:
        req.add_header("Authorization", f"token {github_token.get_secret_value()}")
    req.add_header("Accept", "application/vnd.github.v3.raw")

    try:
        with urllib.request.urlopen(req) as response:
            trusted_roots_str = response.read().decode('utf-8')
            trusted_roots = json.loads(trusted_roots_str)
            return trusted_roots
    except HTTPException as e:
        logger.error("Failed to download trusted roots: {}", e)
        raise e


def get_root_by_key_v1(trusted_root: dict, key: str) -> CoordinationRootV1 | None:
    for networks in trusted_root.values():
        if not isinstance(networks, list | tuple): continue
        for network in networks:
            if not isinstance(network, dict): continue
            for coordination_root in network["coordination_roots"]:
                if coordination_root['public_key'] == key:
                    network_id = network["network_id"]
                    return CoordinationRootV1(network_id=network_id, **coordination_root)
    return None


def should_run_coordination_mode(trusted_roots: dict) -> bool:
    if not state.public_key_path or not state.private_key_path:
        return False

    with open(state.public_key_path, "r") as f:
        pub_key = f.read().strip()

        state.coordination_config = get_root_by_key_v1(trusted_roots, pub_key)

        if state.coordination_config:
            return True
    return False


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
