import json
import urllib.request
from http.client import HTTPException
from pathlib import Path

from contracts.data_models.trusted_roots import CoordinationRootV1
from loguru import logger

import config


def setup_logger(environment: config.Environment) -> None:
    if environment == config.Environment.development:
        config.load_dev_logger(logger)
    else:
        config.load_prod_logger(logger)


def get_github_token() -> str | None:
    github_token = config.github_token
    if github_token is None:
        logger.warning("GITHUB_TOKEN not set. If there is issue downloading trusted roots, this may be the reason.")
    else:
        logger.debug('GitHub token found')
    return github_token


def get_trusted_roots(environment: config.Environment, use_local: bool = None, github_token: str = ''):
    if use_local is None:
        if environment == config.Environment.development:
            use_local = True
        else:
            use_local = False

    if not use_local:
        return get_trusted_roots_github(github_token)
    else:
        return get_trusted_roots_local()


def get_trusted_roots_local() -> dict:
    trust_roots_file_path = Path.joinpath(config.project_root, 'trusted_roots.json')
    with open(trust_roots_file_path, "r") as f:
        trusted_roots = json.load(f)
        return trusted_roots


def get_trusted_roots_github(github_token: str) -> dict:
    logger.info(f'Downloading trusted roots from {config.trusted_roots_url}')
    req = urllib.request.Request(config.trusted_roots_url)
    req.add_header("Authorization", f"token {github_token}")
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
        for network in networks:
            for coordination_root in network["coordination_roots"]:
                if coordination_root['public_key'] == key:
                    network_id = network["network_id"]
                    return CoordinationRootV1(network_id=network_id, **coordination_root)
    return None


def should_run_coordination_mode(trusted_roots: dict) -> bool:
    if not config.pub_coord_key_path or not config.priv_coord_key_path:
        return False

    with open(config.pub_coord_key_path, "r") as f:
        pub_key = f.read().strip()

        config.coordination_config = get_root_by_key_v1(trusted_roots, pub_key)

        if config.coordination_config:
            return True
    return False


if __name__ == '__main__':
    logger.info("Loading application configuration")

    env = config.env
    setup_logger(env)

    logger.debug(f'Using environment: {env}')

    gh_token = get_github_token()
    trusted_roots = get_trusted_roots(env, github_token=gh_token)
    logger.debug("Trusted root file: {}", trusted_roots)

    if config.server_id is None:
        logger.info("SERVER_ID not set. Requesting ID form DB.")
        # TODO: Add code to get server ID from DB

    should_run_coordination_mode(trusted_roots)

    if should_run_coordination_mode(trusted_roots):
        config.coordination_mode = True
        logger.info("Starting in coordination mode.")
        logger.debug("Found trusted root entry matching this node's public key")
        logger.debug("Loaded configuration: {}", config.coordination_config)
        # TODO: Add code to start coordination server
    else:
        logger.info("Starting in backend mode")
        # TODO: Add code to start data backend server
