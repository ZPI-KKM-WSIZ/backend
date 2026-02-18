from fast_api.exceptions.base_exception import AppBaseException


class ConversionException(AppBaseException):
    def __init__(self, message: str, convert_from: type, convert_to: type, status_code: int = 500):
        super().__init__(status_code=status_code, message=message)
        self.convert_from = convert_from.__name__
        self.convert_to = convert_to.__name__

    def to_dict(self):
        base = super().to_dict()
        base["convert_from"] = self.convert_from
        base["convert_to"] = self.convert_to
        return base
