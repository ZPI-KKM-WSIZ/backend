from pydantic.dataclasses import dataclass


@dataclass
class IdentityConfig:
    server_id: str
    app_version: str
