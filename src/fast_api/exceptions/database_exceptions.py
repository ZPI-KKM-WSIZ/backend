from contracts import SensorReading

from fast_api.exceptions.base_exception import AppBaseException


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


class ReadingsBulkInsertException(GenericDatabaseException):
    def __init__(self, message: str,
                 readings: list[SensorReading],
                 exception: Exception | None = None,
                 status_code: int = 500):

        super().__init__(status_code=status_code, message=message)
        self.readings = readings
        self.exception = exception

    def to_dict(self):
        base = super().to_dict()
        if self.exception:
            if hasattr(self.exception, "to_dict") and callable(getattr(self.exception, "to_dict")):
                base["exception"] = self.exception.to_dict()
            else:
                base["exception"] = str(self.exception)

        reading_dumps = [reading.model_dump(mode="json") for reading in self.readings]
        base["reading-dumps"] = reading_dumps
        return base
