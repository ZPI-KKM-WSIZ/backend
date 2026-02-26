import base64
import logging
import uuid
from datetime import UTC
from datetime import datetime
from uuid import UUID

from contracts import ISensorRepository, ILocationRepository, SensorBoard, IFederationRepository, \
    ITokenRepository, Token, Location, Federation
from contracts.data_models.backend_location import LocationDTO
from contracts.data_models.backend_paginated import PaginatedResponse
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

    async def _location_dto_to_db(self, locationDTO: LocationDTO) -> Location:
        db_location = await self.location_repo.find_nearest(target_lat=locationDTO.lat,
                                                            target_lon=locationDTO.long,
                                                            radius_km=1 / 100, limit=1)
        return db_location[0] if db_location else None

    async def _get_or_create_location(self, sensor_dto: SensorBoardDTOBase) -> Location:
        sensor_location = sensor_dto.location

        db_location = await self._location_dto_to_db(sensor_location)

        if not db_location:
            db_location = Location(
                id=uuid.uuid4(),
                localization_lat=sensor_location.lat,
                localization_lon=sensor_location.long,
            )

        return db_location

    @staticmethod
    def _create_token(federation_id: UUID) -> Token:
        db_token = Token(id_federation=federation_id, token=str(uuid.uuid4()), created_at=datetime.now(UTC))
        return db_token

    async def _get_federation(self) -> Federation:
        return await self.federation_repo.get_or_create_unassigned()

    async def _sensor_dto_to_db(self, sensor_dto: SensorBoardDTO | SensorBoardRegisterDTO) -> tuple[
        SensorBoard, tuple[Location, Federation]]:

        try:
            sensor_id = uuid.uuid4()
            location = await self._get_or_create_location(sensor_dto)

            if isinstance(sensor_dto, SensorBoardDTO):
                token = sensor_dto.token
                federation = await self.federation_repo.get_by_token(token)
            else:
                federation = await self._get_federation()
                token = self._create_token(federation.id)

            sensor_board = SensorBoard(
                id=sensor_id,
                id_location=location.id,
                status=sensor_dto.status,
                token=token,
            )
        except Exception as e:
            logging.error(f"Failed to convert SensorBoardDTO to SensorBoard: {e}")
            raise ConversionException(f"Failed to create sensor board model",
                                      convert_from=type(sensor_dto),
                                      convert_to=SensorBoard) from e

        return sensor_board, (location, federation)

    async def register_sensor(self, sensor_register_dto: SensorBoardRegisterDTO) -> SensorBoard:
        db_sensor, (location, federation) = await self._sensor_dto_to_db(sensor_register_dto)
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

        db_sensor, _ = await self._sensor_dto_to_db(sensor_dto)
        await self.sensor_repo.save(db_sensor)
        return db_sensor

    async def get_sensors(self, location: LocationDTO, page_size: int, cursor: str | None = None) \
            -> PaginatedResponse[SensorBoard]:

        location_db = await self._location_dto_to_db(location)
        if location_db is None:
            raise AppBaseException('Location not found', 404)

        # decode cursor from base64 string back to bytes for Cassandra
        paging_state = base64.b64decode(cursor) if cursor else None

        sensors, next_paging_state = await self.sensor_repo.get_paginated(
            location_db.id, page_size, paging_state
        )

        # encode bytes cursor to base64 string for the client
        next_cursor = base64.b64encode(next_paging_state).decode() if next_paging_state else None

        return PaginatedResponse(
            data=sensors,
            next_cursor=next_cursor
        )
