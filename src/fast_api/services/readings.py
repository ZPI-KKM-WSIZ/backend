import logging
import uuid

from contracts import SensorReadingDTO, SensorReading, IReadingsRepository

from fast_api.exceptions.conversion_exceptions import ConversionException
from fast_api.exceptions.database_exceptions import ReadingInsertException


class ReadingsService:
    def __init__(self, readings_repo: IReadingsRepository):
        self.readings_repo = readings_repo

    @staticmethod
    def convert_dto_to_db_model(reading: SensorReadingDTO) -> SensorReading:
        try:
            return SensorReading(
                id_sensor=uuid.uuid4(),
                created_at=reading.created_at,
                token=reading.token,
                disputed=False,
                co2=reading.sensors.co2,
                tvoc=reading.sensors.tvoc,
                pm1=reading.sensors.pm1,
                pm10=reading.sensors.pm10,
                pm25=reading.sensors.pm25,
                pressure=reading.sensors.pressure,
                humidity=reading.sensors.humidity,
                temperature=reading.sensors.temperature,
            )
        except Exception as e:
            logging.error(f"Failed to convert SensorReadingDTO to SensorReading: {e}")
            raise ConversionException(f"Failed to create sensor reading model: {e}",
                                      convert_from=type(reading),
                                      convert_to=SensorReading)

    async def add_reading_to_db(self, reading: SensorReading) -> None:
        try:
            await self.readings_repo.save(reading)
        except Exception as e:
            logging.error(f"Failed to save reading: {e}")
            raise ReadingInsertException(message=f"Failed to save reading: {e}", reading=reading)