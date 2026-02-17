import json
from urllib.request import urlopen, Request

from pydantic import SecretStr


def get_access_token(client_id: SecretStr, client_secret: SecretStr):
    """Exchange OAuth credentials for an access token"""
    from urllib.parse import urlencode

    url = 'https://api.tailscale.com/api/v2/oauth/token'
    data = urlencode({
        'client_id': client_id.get_secret_value(),
        'client_secret': client_secret.get_secret_value(),
        'grant_type': 'client_credentials'
    }).encode()

    req = Request(url, data=data)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    with urlopen(req) as response:
        result = json.loads(response.read().decode())
        if "access_token" not in result:
            raise Exception(f"No accesses token found: {result}")
        return SecretStr(result['access_token'])
