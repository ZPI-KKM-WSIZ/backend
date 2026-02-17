import json
import logging
import random
from urllib.error import HTTPError
from urllib.request import urlopen, Request

from pydantic import SecretStr

from src.core.env_config import Environment


class TailscaleService:
    def __init__(self, client_id: SecretStr, client_secret: SecretStr, tailnet_id: SecretStr, environment: Environment):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tailnet_id = tailnet_id
        self.environment = environment

    def get_access_token(self):
        """Exchange OAuth credentials for an access token"""
        from urllib.parse import urlencode

        url = 'https://api.tailscale.com/api/v2/oauth/token'
        data = urlencode({
            'client_id': self.client_id.get_secret_value(),
            'client_secret': self.client_secret.get_secret_value(),
            'grant_type': 'client_credentials'
        }).encode()

        req = Request(url, data=data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')

        with urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            if "access_token" not in result:
                raise Exception(f"No accesses token found: {result}")
            return SecretStr(result['access_token'])

    def get_cassandra_contact_points(self) -> list[str]:
        logging.info("Fetching Cassandra contact points from Tailscale API")

        try:
            api_key = self.get_access_token()
        except Exception as e:
            logging.error(f"Failed to get access token from Tailscale API: {e}")
            return []

        url = f'https://api.tailscale.com/api/v2/tailnet/{self.tailnet_id.get_secret_value()}/devices'

        req = Request(url)
        req.add_header('Authorization', f'Bearer {api_key.get_secret_value()}')

        try:
            with urlopen(req, timeout=10) as response:
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
            environment_str = "prod" if self.environment == Environment.PRODUCTION else "test"
            environment_match = any(environment_str in tag for tag in tags)

            logging.debug(f"{hostname}: tags={tags}, "
                          f"has_cassandra_tag={has_cassandra_tag}, "
                          f"environment_match={environment_match}, "
                          f"addresses={addresses}")

            if has_cassandra_tag and environment_match and addresses:
                ipv4_addr = next((addr for addr in addresses if ':' not in addr), None)
                if ipv4_addr:
                    cassandra_nodes.append(ipv4_addr)

        recommended_contact_point_count = 3
        k = min(len(cassandra_nodes), recommended_contact_point_count)
        res = random.sample(cassandra_nodes, k)

        if len(res) == 0:
            logging.error("No viable Cassandra nodes found")
            return []
        elif len(res) < recommended_contact_point_count:
            logging.warning(f"Only {len(res)} Cassandra contact points selected, "
                            f"recommended amount: {recommended_contact_point_count}")
        else:
            logging.info(f"Found {len(cassandra_nodes)} online Cassandra nodes")

        logging.debug(f"Selected contact points for Cassandra: {res}")
        return res
