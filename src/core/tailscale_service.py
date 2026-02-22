import logging
import random

import httpx
from pydantic import SecretStr

from core.environment import Environment
from core.network_utils import retry_with_delay_async


class TailscaleService:
    """
    Service for discovering Cassandra contact points via the Tailscale API.

    Uses Tailscale's OAuth flow to authenticate and query devices on the
    tailnet, filtering for online Cassandra nodes tagged for the current
    deployment environment.

    Attributes:
        client_id: OAuth client ID for Tailscale API authentication.
        client_secret: OAuth client secret for Tailscale API authentication.
        tailnet_id: The tailnet identifier to query devices from.
        environment: Deployment environment used to filter relevant nodes.
    """

    def __init__(self, client_id: SecretStr, client_secret: SecretStr, tailnet_id: SecretStr, environment: Environment):
        """
        Initialise the Tailscale service.

        Args:
            client_id: OAuth client ID for Tailscale API authentication.
            client_secret: OAuth client secret for Tailscale API authentication.
            tailnet_id: The tailnet identifier to query devices from.
            environment: Deployment environment used to filter relevant nodes.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tailnet_id = tailnet_id
        self.environment = environment

    async def get_access_token_async(self) -> SecretStr:
        """
        Exchange OAuth credentials for a Tailscale API access token.

        Returns:
            A SecretStr containing the access token.

        Raises:
            RuntimeError: If the API response does not include an access token.
        """

        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.tailscale.com/api/v2/oauth/token',
                data={
                    'client_id': self.client_id.get_secret_value(),
                    'client_secret': self.client_secret.get_secret_value(),
                    'grant_type': 'client_credentials'
                },
                timeout=10,
            )
            result = response.json()
            if "access_token" not in result:
                raise RuntimeError(f"No access token found: {result}")
            return SecretStr(result['access_token'])

    async def get_devices_async(self, api_key: SecretStr) -> dict:
        """
        Fetch all devices registered on the tailnet.

        Args:
            api_key: A valid Tailscale API access token.

        Returns:
            Dict containing the API response with device data.

        Raises:
            RuntimeError: If no device data is returned.
        """

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'https://api.tailscale.com/api/v2/tailnet/{self.tailnet_id.get_secret_value()}/devices',
                headers={'Authorization': f'Bearer {api_key.get_secret_value()}'},
                timeout=10,
            )
            data = response.json()
            if not data:
                raise RuntimeError("No devices found")
            return data

    def _get_viable_ips(self, devices: list[dict]) -> list[str]:
        """
        Filter devices and extract IPv4 addresses of viable Cassandra nodes.

        A node is considered viable if it has the 'cassandra' tag, matches
        the current environment tag, has addresses, and is online.

        Args:
            devices: List of device dictionaries from the Tailscale API.

        Returns:
            List of IPv4 addresses of viable Cassandra nodes.

        Raises:
            RuntimeError: If no viable Cassandra nodes are found.
        """

        viable_nodes = []
        environment_str = "prod" if self.environment == Environment.PRODUCTION else "test"

        for device in devices:
            hostname = device.get('hostname', '')
            tags = device.get('tags', [])
            addresses = device.get('addresses', [])

            environment_match = any(environment_str in tag for tag in tags)
            has_cassandra_tag = any('cassandra' in tag for tag in tags)
            is_online = device.get('connectedToControl', False)

            logging.debug(f"{hostname}: tags={tags}, "
                          f"has_cassandra_tag={has_cassandra_tag}, "
                          f"environment_match={environment_match}, "
                          f"is_online={is_online}, "
                          f"addresses={addresses}")

            if has_cassandra_tag and environment_match and addresses and is_online:
                ipv4_addr = next((addr for addr in addresses if ':' not in addr), None)
                if ipv4_addr:
                    viable_nodes.append(ipv4_addr)
        if len(viable_nodes) == 0:
            raise RuntimeError("No viable Cassandra nodes found")
        return viable_nodes

    async def _get_viable_cassandra_nodes(self) -> list[str]:
        """
        Authenticate with Tailscale and retrieve viable Cassandra node IPs.

        Returns:
            List of IPv4 addresses for available Cassandra nodes.

        Raises:
            RuntimeError: If authentication fails, no devices are returned,
                          or no viable Cassandra nodes are found.
        """

        api_key = await self.get_access_token_async()

        data = await self.get_devices_async(api_key)
        if not data or 'devices' not in data:
            raise RuntimeError(f"No devices received from Tailscale API")

        devices = data.get('devices', [])

        logging.debug(f"Total devices found: {len(devices)}")
        logging.debug(f"All devices: {devices}")

        cassandra_nodes = self._get_viable_ips(devices)

        return cassandra_nodes

    async def get_cassandra_contact_points(self, max_retries: int = 5, base_delay: float = 2.0) -> list[
        str]:
        """
        Retrieve a randomised selection of Cassandra contact points with retry logic.

        Fetches viable Cassandra node addresses from Tailscale and randomly
        samples up to 3 of them. Logs a warning if fewer than 3 are available.

        Args:
            max_retries: Maximum number of retry attempts for node discovery (default: 5).
            base_delay: Base delay in seconds between retries (default: 2.0).

        Returns:
            List of up to 3 Cassandra node IPv4 addresses.

        Raises:
            RuntimeError: If node discovery fails after all retry attempts.
        """
        logging.info("Fetching Cassandra contact points from Tailscale API")

        viable_cassandra_nodes = await retry_with_delay_async(max_retries=max_retries, base_delay=base_delay,
                                                              async_func=self._get_viable_cassandra_nodes)

        recommended_contact_point_count = 3
        k = min(len(viable_cassandra_nodes), recommended_contact_point_count)
        res = random.sample(viable_cassandra_nodes, k)

        if len(res) < recommended_contact_point_count:
            logging.warning(f"Only {len(res)} Cassandra contact points selected, "
                            f"recommended amount: {recommended_contact_point_count}")
        else:
            logging.info(f"Found {len(viable_cassandra_nodes)} online Cassandra nodes")

        logging.debug(f"Selected contact points for Cassandra: {res}")
        return res
