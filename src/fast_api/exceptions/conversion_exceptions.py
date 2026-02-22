from fast_api.exceptions.base_exception import AppBaseException


class ConversionException(AppBaseException):
    """
    Exception raised when type conversion between models fails.
    
    Tracks both the source and target types to provide detailed
    error context for debugging conversion issues.
    
    Attributes:
        convert_from: Name of the source type being converted from.
        convert_to: Name of the target type being converted to.
    """

    def __init__(self, message: str, convert_from: type, convert_to: type, status_code: int = 500):
        """
        Initialise a conversion exception.
        
        Args:
            message: Error message describing the conversion failure.
            convert_from: The source type class.
            convert_to: The target type class.
            status_code: HTTP status code (default: 500).
        """
        super().__init__(status_code=status_code, message=message)
        self.convert_from = convert_from.__name__
        self.convert_to = convert_to.__name__

    def to_dict(self):
        """
        Convert the exception to a dictionary including type information.
        
        Returns:
            Dict with exception details and conversion type names.
        """
        base = super().to_dict()
        base["convert_from"] = self.convert_from
        base["convert_to"] = self.convert_to
        return base
