import asyncio
import json
import logging
import random
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from pydantic import SecretStr

from core.environment import Environment
from core.network_utils import retry_with_delay


class TailscaleService:
    def __init__(self, client_id: SecretStr, client_secret: SecretStr, tailnet_id: SecretStr, environment: Environment):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tailnet_id = tailnet_id
        self.environment = environment

    def _get_access_token(self) -> SecretStr:
        """Exchange OAuth credentials for an access token"""

        url = 'https://api.tailscale.com/api/v2/oauth/token'
        data = urlencode({
            'client_id': self.client_id.get_secret_value(),
            'client_secret': self.client_secret.get_secret_value(),
            'grant_type': 'client_credentials'
        }).encode()

        req = Request(url, data=data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')

        with urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            if "access_token" not in result:
                raise RuntimeError(f"No access token found: {result}")
            return SecretStr(result['access_token'])

    async def get_access_token_async(self) -> SecretStr:
        return await asyncio.to_thread(self._get_access_token)

    def _get_devices(self, api_key: SecretStr) -> dict:
        """Fetch devices from Tailscale API"""
        url = f'https://api.tailscale.com/api/v2/tailnet/{self.tailnet_id.get_secret_value()}/devices'

        req = Request(url)
        req.add_header('Authorization', f'Bearer {api_key.get_secret_value()}')

        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            if not data:
                raise RuntimeError("No devices found")
            return data

    async def get_devices_async(self, api_key: SecretStr) -> dict:
        return await asyncio.to_thread(self._get_devices, api_key)

    def _get_viable_ips(self, devices: list[dict]) -> list[str]:
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
        logging.info("Fetching Cassandra contact points from Tailscale API")

        viable_cassandra_nodes = await retry_with_delay(max_retries=max_retries, base_delay=base_delay,
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
