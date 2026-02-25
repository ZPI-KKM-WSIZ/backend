import logging
import uuid

from contracts import SensorReadingDTO, SensorReading, IReadingsRepository, ISensorRepository, ILocationRepository

from fast_api.exceptions.conversion_exceptions import ConversionException
from fast_api.exceptions.database_exceptions import ReadingInsertException, ReadingsBulkInsertException


class ReadingsService:
    """
    Service for converting and persisting sensor readings.

    Handles the transformation of incoming DTOs into database models,
    resolving sensor and location data in the process, and persisting
    them to the database individually or in bulk.

    Attributes:
        readings_repo: Repository for saving sensor readings.
        sensor_repo: Repository for looking up sensor boards by token.
        location_repository: Repository for resolving or creating locations.
    """

    def __init__(self, readings_repo: IReadingsRepository,
                 sensor_repo: ISensorRepository,
                 location_repo: ILocationRepository):
        """
        Args:
            readings_repo: Repository for saving sensor readings.
            sensor_repo: Repository for looking up sensor boards by token.
            location_repo: Repository for resolving or creating locations.
        """

        self.readings_repo = readings_repo
        self.sensor_repo = sensor_repo
        self.location_repository = location_repo

    async def convert_dto_to_db_model(self, reading: SensorReadingDTO) -> SensorReading:
        """
        Convert a SensorReadingDTO to a SensorReading database model.

        Resolves the sensor by token and finds or creates a matching location
        based on the reading's coordinates before building the database model.

        Args:
            reading: The incoming sensor reading DTO.

        Returns:
            A SensorReading model ready to be persisted.

        Raises:
            ConversionException: If the sensor token is unregistered or the
                conversion fails for any other reason.
        """

        try:
            sensor = await self.sensor_repo.get_by_token(reading.token)
            reading_lat = reading.meta.lat
            reading_lon = reading.meta.lon
            location = await self.location_repository.find_nearest(target_lat=reading_lat,
                                                                   target_lon=reading_lon,
                                                                   radius_km=1 / 100, limit=1)
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
        """
        Convert a list of SensorReadingDTOs to SensorReading database models.

        Args:
            readings: List of incoming sensor reading DTOs.

        Returns:
            List of SensorReading models ready to be persisted.

        Raises:
            ConversionException: If any reading cannot be converted.
        """

        results = []
        for reading in readings:
            reading_model = await ReadingsService.convert_dto_to_db_model(self, reading=reading)
            results.append(reading_model)
        return results

    async def add_reading_to_db(self, reading: SensorReading) -> None:
        """
        Persist a single sensor reading to the database.

        Args:
            reading: The SensorReading model to save.

        Raises:
            ReadingInsertException: If the reading cannot be saved.
        """

        try:
            await self.readings_repo.save(reading)
        except Exception as e:
            logging.error(f"Failed to save reading: {e}")
            raise ReadingInsertException(message=f"Failed to save reading: {e}", reading=reading) from e

    async def add_reading_to_db_bulk(self, readings: list[SensorReading]) -> None:
        """
        Persist multiple sensor readings to the database in bulk.

        Args:
            readings: List of SensorReading models to save.

        Raises:
            ReadingsBulkInsertException: If the save fails entirely or only
                partially succeeds (some readings were not saved).
        """

        try:
            saved_readings, _ = await self.readings_repo.save_bulk(readings)
            if saved_readings != readings:
                raise ReadingsBulkInsertException(message=f"Readings Partially Saved",
                                                  readings=readings, saved_readings=saved_readings)

        except Exception as e:
            logging.error(f"Failed to save reading: {e}")
            raise ReadingsBulkInsertException(message=f"Failed to save readings: {e}",
                                              readings=readings, saved_readings=[], exception=e) from e
