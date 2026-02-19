import logging
import uuid

from contracts import SensorReadingDTO, SensorReading, IReadingsRepository, ISensorRepository, ILocationRepository

from fast_api.exceptions.conversion_exceptions import ConversionException
from fast_api.exceptions.database_exceptions import ReadingInsertException, ReadingsBulkInsertException


class ReadingsService:
    def __init__(self, readings_repo: IReadingsRepository,
                 sensor_repo: ISensorRepository,
                 location_repository: ILocationRepository):
        self.readings_repo = readings_repo
        self.sensor_repo = sensor_repo
        self.location_repository = location_repository

    async def convert_dto_to_db_model(self, reading: SensorReadingDTO) -> SensorReading:
        """Convert SensorReadingDTO to SensorReading"""
        try:
            sensor = await self.sensor_repo.get_by_token(reading.token)
            reading_lat = reading.meta.lat
            reading_lon = reading.meta.lon
            #FIXME: DB CODE CURRENTLY DOES NOT ALLOW EXACT MATCHES!
            location = await self.location_repository.find_nearest(target_lat=reading_lat+1/10000, target_lon=reading_lon,
                                                                   radius_km=1/1000, limit=1)
            location = location[0] if location else None

            if not sensor:
                raise ConversionException(f"No sensor found with token {reading.token}, register sensor first",
                                          convert_from=type(reading),
                                          convert_to=SensorReading)
            if not location:
                from contracts import Location
                new_location = Location(id=uuid.uuid4(), localization_lat=reading_lat, localization_lon=reading_lon)
                location = await self.location_repository.save(new_location)

            return SensorReading(
                id_sensor=sensor.id,
                id_location=location.id,
                created_at=reading.created_at,
                token=reading.token,
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

    async def convert_dto_to_db_model_bulk(self, readings: list[SensorReadingDTO]) -> list[SensorReading]:
        results = []
        for reading in readings:
            reading_model = await ReadingsService.convert_dto_to_db_model(self, reading=reading)
            results.append(reading_model)
        return results

    async def add_reading_to_db(self, reading: SensorReading) -> None:
        try:
            await self.readings_repo.save(reading)
        except Exception as e:
            logging.error(f"Failed to save reading: {e}")
            raise ReadingInsertException(message=f"Failed to save reading: {e}", reading=reading) from e

    async def add_reading_to_db_bulk(self, readings: list[SensorReading]) -> None:
        try:
            saved_readings, readings = await self.readings_repo.save_bulk(readings)
            if saved_readings != readings:
                raise ReadingsBulkInsertException(message=f"Readings Partially Saved",
                                                  readings=readings, saved_readings=saved_readings)

        except Exception as e:
            logging.error(f"Failed to save reading: {e}")
            raise ReadingsBulkInsertException(message=f"Failed to save readings: {e}",
                                              readings=readings, saved_readings=[], exception=e) from e
