from loguru import logger

from src.core import config
from src.core.bootstrap_utils import get_trusted_roots, get_github_token, should_run_coordination_mode, setup_logger

if __name__ == '__main__':
    # Initial setup
    logger.info("Loading application configuration")
    settings = config.settings
    state = config.state

    env = settings.ENVIRONMENT
    setup_logger(env, settings.LOGS_DIR)

    logger.debug(f'Using environment: {env}')

    try:
        trusted_roots = get_trusted_roots(env, github_token=get_github_token())
        logger.debug("Trusted root file: {}", trusted_roots)
    except Exception as e:
        logger.error(f"Error while loading trusted roots: {e}")
        exit(-1)

    # Load identity
    server_id = settings.SERVER_ID
    if server_id is None:
        logger.info("SERVER_ID not set. Requesting ID form DB.")
        # TODO: Add code to get server ID from DB

    config.state.load_identity(server_id=server_id, secrets_dir=settings.SECRETS_DIR)

    # Run
    if should_run_coordination_mode(trusted_roots):
        state.coordination_mode = True
        logger.debug("Found trusted root entry matching this node's public key")
        logger.debug("Loaded configuration: {}", state.coordination_config)
        logger.info("Starting in coordination mode.")
        # TODO: Add code to start coordination server
    else:
        logger.info("Starting in backend mode")
        # TODO: Add code to start data backend server
