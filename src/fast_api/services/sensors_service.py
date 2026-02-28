import logging
import uuid
from datetime import UTC
from datetime import datetime
from uuid import UUID

from contracts import ISensorRepository, ILocationRepository, SensorBoard, IFederationRepository, \
    ITokenRepository, Token, Location, Federation
from contracts.data_models.backend_location import LocationDTO
from contracts.data_models.backend_sensors import SensorBoardRegisterDTO, SensorBoardDTOBase, SensorBoardDTO

from fast_api.exceptions.base_exception import AppBaseException
from fast_api.exceptions.conversion_exceptions import ConversionException
from fast_api.exceptions.database_exceptions import GenericDatabaseException


class SensorsService:
    def __init__(self, sensor_repo: ISensorRepository, location_repo: ILocationRepository,
                 federation_repo: IFederationRepository,
                 token_repo: ITokenRepository):
        self.sensor_repo = sensor_repo
        self.location_repo = location_repo
        self.federation_repo = federation_repo
        self.token_repo = token_repo

    async def _location_dto_to_db(self, locationDTO: LocationDTO, radius: int, limit: int = 1) -> Location:
        db_location = await self.location_repo.find_nearest(target_lat=locationDTO.lat,
                                                            target_lon=locationDTO.long,
                                                            radius_km=radius, limit=limit)
        return db_location[0] if db_location else None

    async def _locations_dto_to_db(self, locationDTO: LocationDTO, radius: int, limit: int = 1) -> list[Location]:
        db_locations = await self.location_repo.find_nearest(target_lat=locationDTO.lat,
                                                             target_lon=locationDTO.long,
                                                             radius_km=radius, limit=limit)
        return db_locations

    async def _get_or_create_location(self, sensor_dto: SensorBoardDTOBase, radius: int) -> Location:
        sensor_location = sensor_dto.location

        db_location = await self._location_dto_to_db(sensor_location, radius)

        if not db_location:
            db_location = Location(
                id=uuid.uuid4(),
                localization_lat=sensor_location.lat,
                localization_lon=sensor_location.long,
            )

        return db_location

    @staticmethod
    def _create_token(federation_id: UUID) -> Token:
        db_token = Token(federation_id=federation_id, token=str(uuid.uuid4()), created_at=datetime.now(UTC))
        return db_token

    async def _get_federation(self) -> Federation:
        return await self.federation_repo.get_or_create_unassigned()

    async def _sensor_dto_to_db(self, sensor_dto: SensorBoardDTO | SensorBoardRegisterDTO, radius: int) -> tuple[
        SensorBoard, tuple[Location, Federation]]:

        try:
            sensor_id = uuid.uuid4()
            location = await self._get_or_create_location(sensor_dto, radius)

            if isinstance(sensor_dto, SensorBoardDTO):
                federation = await self.federation_repo.get_by_token(sensor_dto.token)
                token = self._create_token(federation.id)
            else:
                federation = await self._get_federation()
                token = self._create_token(federation.id)

            sensor_board = SensorBoard(
                id=sensor_id,
                id_location=location.id,
                status=sensor_dto.status,
                token=token.token,
            )
        except Exception as e:
            logging.error(f"Failed to convert SensorBoardDTO to SensorBoard: {e}")
            raise ConversionException(f"Failed to create sensor board model",
                                      convert_from=type(sensor_dto),
                                      convert_to=SensorBoard) from e

        return sensor_board, (location, federation)

    async def register_sensor(self, sensor_register_dto: SensorBoardRegisterDTO) -> SensorBoard:
        db_sensor, (location, federation) = await self._sensor_dto_to_db(sensor_register_dto, radius=int(1 / 100))
        try:
            await self.sensor_repo.register(entity=db_sensor, location=location, federation=federation)
        except Exception as e:
            logging.error(f"Failed to register sensor {db_sensor.id}")
            raise GenericDatabaseException(message="Sensor registration failed") from e
        return db_sensor

    async def upsert_sensor(self, sensor_dto: SensorBoardDTO) -> SensorBoard:
        existing = await self.sensor_repo.get_by_token(sensor_dto.token)
        if existing is None:
            raise AppBaseException('Invalid token', 401)

        db_sensor, _ = await self._sensor_dto_to_db(sensor_dto, radius=int(1 / 100))
        await self.sensor_repo.save(db_sensor)
        return db_sensor

    async def get_sensors_by_location(self, location: LocationDTO, radius: int, locations_limit: int, page_size: int) \
            -> list[SensorBoard]:

        location_db = await self._locations_dto_to_db(location, radius, locations_limit)
        if location_db is None:
            raise AppBaseException('Location not found', 404)

        result_sensors = []
        for location in location_db:
            sensors = await self.sensor_repo.get_by_location(location.id, page_size)

            if len(sensors) > 0:
                result_sensors = [*result_sensors, *sensors]

        return result_sensors

    async def get_sensors(self, page_size: int) \
            -> list[SensorBoard]:
        result_sensors, _ = await self.sensor_repo.get_all(page_size)

        return result_sensors
