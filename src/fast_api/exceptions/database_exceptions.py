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
                 saved_readings: list[SensorReading],
                 exception: Exception | None = None,
                 status_code: int | None = None):

        super().__init__(status_code=status_code, message=message)
        self.readings = readings
        self.saved_readings = saved_readings
        self.exception = exception
        if status_code:
            self.status_code = status_code
        elif len(saved_readings) > 0:
            self.status_code = 207
        else:
            self.status_code = 500

    def to_dict(self):
        base = super().to_dict()
        if self.exception:
            if hasattr(self.exception, "to_dict") and callable(getattr(self.exception, "to_dict")):
                base["exception"] = self.exception.to_dict()
            else:
                base["exception"] = str(self.exception)

        reading_dumps_with_satus_codes = []
        for reading in self.readings:
            reading_dump = reading.model_dump(mode="json")
            if reading not in self.saved_readings:
                status_code = 500
            else:
                status_code = 201
            reading_dumps_with_satus_codes.append({"entity": reading_dump, "status": status_code})

        base["results"] = reading_dumps_with_satus_codes
        return base
