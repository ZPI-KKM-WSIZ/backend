from contracts import SensorReading

from fast_api.exceptions.base_exception import AppBaseException


class GenericDatabaseException(AppBaseException):
    """Base exception for all database-related errors."""

    def __init__(self, message: str, status_code: int = 500):
        """
        Args:
            message: Error message describing the database failure.
            status_code: HTTP status code (default: 500).
        """

        super().__init__(status_code=status_code, message=message)


class ReadingInsertException(GenericDatabaseException):
    """Raised when a single sensor reading fails to be saved to the database."""

    def __init__(self, message: str, reading: SensorReading, status_code: int = 500):
        """
        Args:
            message: Error message describing the failure.
            reading: The SensorReading that could not be saved.
            status_code: HTTP status code (default: 500).
        """

        super().__init__(status_code=status_code, message=message)
        self.reading = reading

    def to_dict(self):
        """
        Convert the exception to a dictionary including the failed reading.

        Returns:
            Dict with error details and a JSON dump of the failed reading.
        """

        base = super().to_dict()
        base["reading-dump"] = self.reading.model_dump(mode="json")
        return base


class ReadingsBulkInsertException(GenericDatabaseException):
    """
    Raised when a bulk insert of sensor readings fails or only partially succeeds.

    The status code is determined automatically if not provided:
    - 207 Multi-Status if some readings were saved successfully.
    - 500 Internal Server Error if none were saved.

    Attributes:
        readings: The full list of readings that were attempted.
        saved_readings: The subset that was successfully saved.
        exception: The underlying exception that caused the failure, if any.
    """

    def __init__(self, message: str,
                 readings: list[SensorReading],
                 saved_readings: list[SensorReading],
                 exception: Exception | None = None,
                 status_code: int | None = None):
        """
        Args:
            message: Error message describing the failure.
            readings: All readings that were attempted.
            saved_readings: Readings that were successfully saved.
            exception: Underlying exception that caused the failure, if any.
            status_code: Explicit HTTP status code. If omitted, inferred from
                saved_readings (207 for partial success, 500 for total failure).
        """

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
        """
        Convert the exception to a dictionary with per-reading result details.

        Each reading in the response includes its status code: 201 if saved
        successfully, 500 if it failed.

        Returns:
            Dict with error details, optional nested exception, and a results
            list containing each reading's data and its individual status code.
        """

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
