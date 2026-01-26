import urllib.request

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
        logger.debug('GitHub token: {}', {github_token})
    return github_token


def get_trusted_roots(github_token: str) -> str:
    req = urllib.request.Request(config.trusted_roots_url)
    req.add_header("Authorization", f"token {github_token}")
    req.add_header("Accept", "application/vnd.github.v3.raw")

    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

def is_authorized_coordination_node():
    return True


if __name__ == '__main__':
    logger.info("Loading application configuration")

    env = config.env
    setup_logger(env)

    logger.debug(f'Environment: {env}')

    gh_token = get_github_token()
    try:
        logger.info(f'Downloading trusted roots from {config.trusted_roots_url}')
        trusted_roots = get_trusted_roots(gh_token)
    except Exception as e:
        logger.error("Failed to download trusted roots: {}", e)
        raise e

    logger.info('Starting application')

    logger.debug("Trusted root file: {}", trusted_roots)
