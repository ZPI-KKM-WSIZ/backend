class AppBaseException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        self.type = type(self).__name__
        super().__init__(message)

    def to_dict(self):
        return {
            "type": self.type,
            "message": self.message
        }
