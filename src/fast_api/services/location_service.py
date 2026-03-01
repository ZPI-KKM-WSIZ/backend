from uuid import UUID

from contracts import ILocationRepository, ISensorRepository, Location

from fast_api.exceptions.base_exception import AppBaseException


class LocationsService:
    """
    Service for querying locations.

    Attributes:
        location_repo: Repository for fetching location records.
        sensor_repo: Repository for looking up sensor boards.
    """

    def __init__(self, location_repo: ILocationRepository, sensor_repo: ISensorRepository):
        """
        Args:
            location_repo: Repository for fetching location records.
            sensor_repo: Repository for looking up sensor boards.
        """
        self.location_repo = location_repo
        self.sensor_repo = sensor_repo

    async def get_location_by_sensor(self, sensor_id: UUID) -> Location:
        """
        Retrieve the location associated with a given sensor.

        Args:
            sensor_id: UUID of the sensor board.

        Returns:
            The Location model associated with the sensor.

        Raises:
            AppBaseException: If no sensor with the given ID exists (404),
                or if the sensor has no associated location (404).
        """
        sensor = await self.sensor_repo.get_by_id(sensor_id)
        if sensor is None:
            raise AppBaseException(f"Sensor {sensor_id} not found", 404)

        location = await self.location_repo.get_by_id(sensor.id_location)
        if location is None:
            raise AppBaseException(f"Location for sensor {sensor_id} not found", 404)

        return location
