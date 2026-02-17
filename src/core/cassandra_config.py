import json
import logging
import random
import ssl
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from pydantic import SecretStr
from pydantic_settings import BaseSettings
from typing_extensions import Any

from src.core import config
from src.core.tailscale import get_access_token


def get_cassandra_contact_points() -> list[str]:
    logging.info("Fetching Cassandra contact points from Tailscale API")
    settings = config.settings
    tailnet_id = settings.tailscale_secrets.TAILNET_ID
    client_id = settings.tailscale_secrets.TAILSCALE_API_CLIENT_ID
    client_secret = settings.tailscale_secrets.TAILSCALE_API_CLIENT_SECRET

    try:
        api_key = get_access_token(client_id, client_secret)
    except Exception as e:
        logging.error(f"Failed to get access token from Tailscale API: {e}")
        return []

    url = f'https://api.tailscale.com/api/v2/tailnet/{tailnet_id.get_secret_value()}/devices'

    req = Request(url)
    req.add_header('Authorization', f'Bearer {api_key.get_secret_value()}')

    try:
        with urlopen(req) as response:
            data = json.loads(response.read().decode())
    except HTTPError as e:
        logging.error(f"Error fetching devices: {e}")
        return []

    devices = data.get('devices', [])

    logging.debug(f"Total devices found: {len(devices)}")

    # Filter for online Cassandra nodes with tag:cassandra-node (or tag containing 'cassandra')
    cassandra_nodes = []
    for device in devices:
        hostname = device.get('hostname', '')
        tags = device.get('tags', [])
        addresses = device.get('addresses', [])

        has_cassandra_tag = any('cassandra' in tag for tag in tags)
        environment_match = any(settings.ENVIRONMENT in tag for tag in tags)

        logging.debug(f"{hostname}: tags={tags}, "
                      f"has_cassandra_tag={has_cassandra_tag}, "
                      f"operating_mode_match={environment_match}, "
                      f"addresses={addresses}")

        if has_cassandra_tag and environment_match and addresses:
            ipv4_addr = next((addr for addr in addresses if ':' not in addr), None)
            if ipv4_addr:
                cassandra_nodes.append(ipv4_addr)

    logging.info(f"Found {len(cassandra_nodes)} online Cassandra nodes")

    k = min(len(cassandra_nodes), 3)
    res = random.sample(cassandra_nodes, k)

    logging.debug(f"Selected contact points for Cassandra: {res}")
    return res


class CassandraConfig(BaseSettings):
    """Configuration for Cassandra database connection."""
    contact_points: list[str]
    username: str | None = None
    password: SecretStr | None = None
    compression: bool | str
    local_datacenter: str | None = None
    connect_timeout: float
    request_timeout: float
    ssl_context: ssl.SSLContext | None = None
    ssl_options: dict[str, Any] | None = None
    compression: bool | str
    protocol_version: int
    port: int
    keyspace: str
