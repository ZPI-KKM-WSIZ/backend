from src.core.identity_configuration import IdentityConfig


class IdentityService:
    def __init__(self, identity: IdentityConfig):
        self.identity = identity

    def get_app_version(self, ) -> str:
        return self.identity.app_version

    def get_server_id(self, ) -> str:
        return self.identity.server_id