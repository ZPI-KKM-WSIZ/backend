from pydantic.dataclasses import dataclass


@dataclass
class IdentityConfig:
    """
    Configuration for application identity and versioning.
    
    Attributes:
        server_id: Unique identifier for this server instance.
        app_version: Application version string from project configuration.
    """
    server_id: str
    app_version: str
