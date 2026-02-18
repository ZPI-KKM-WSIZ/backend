from contracts import SensorReading

from src.fast_api.exceptions.base_exception import AppBaseException


class GenericDatabaseException(AppBaseException):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(status_code=status_code, message=message)


class ReadingInsertException(GenericDatabaseException):
    def __init__(self, message: str, reading: SensorReading, status_code: int = 500):
        super().__init__(status_code=status_code, message=message)
        self.reading = reading

    def to_dict(self):
        base = super().to_dict()
        base["reading-dump"] = self.reading.model_dump(mode="json")
        return base
