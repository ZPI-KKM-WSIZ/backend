from core.identity_configuration import IdentityConfig


class IdentityService:
    """
    Service providing access to application identity information.
    
    Attributes:
        identity: The identity configuration containing server details.
    """

    def __init__(self, identity: IdentityConfig):
        """
        Initialise the identity service.
        
        Args:
            identity: IdentityConfig instance with server identification.
        """
        self.identity = identity

    def get_app_version(self) -> str:
        """
        Get the application version.
        
        Returns:
            The current application version string.
        """
        return self.identity.app_version

    def get_server_id(self) -> str:
        """
        Get the server identifier.
        
        Returns:
            The unique server ID for this instance.
        """
        return self.identity.server_id
