class AppBaseException(Exception):
    """
    Base exception class for all application-specific exceptions.
    
    Provides structured error information with HTTP status codes
    and serialization support for API error responses.
    
    Attributes:
        message: Human-readable error message.
        status_code: HTTP status code for the error (default: 400).
        type: The name of the exception class.
    """

    def __init__(self, message: str, status_code: int = 400):
        """
        Initialise the base exception.
        
        Args:
            message: Error message describing what went wrong.
            status_code: HTTP status code (default: 400).
        """
        self.message = message
        self.status_code = status_code
        self.type = type(self).__name__
        super().__init__(message)

    def to_dict(self):
        """
        Convert the exception to a dictionary for API responses.
        
        Returns:
            Dict containing exception type and message.
        """
        return {
            "type": self.type,
            "message": self.message
        }
