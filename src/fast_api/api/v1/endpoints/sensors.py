from contracts import SensorBoard, PaginatedResponse
from contracts.data_models.backend_location import LocationDTO
from contracts.data_models.backend_sensors import SensorBoardRegisterDTO, SensorBoardDTO
from fastapi import APIRouter, Depends

from fast_api.dependencies import get_sensors_service
from fast_api.services.sensors_service import SensorsService

sensors_router = APIRouter(prefix="/api/v1")


@sensors_router.get("/sensors", response_model=list[PaginatedResponse[SensorBoard]])
async def get_sensors(location: LocationDTO, radius: int, page_size: int, locations_limit: int = 500,
                      paging_state: str | None = None,
                      sensors_service: SensorsService = Depends(get_sensors_service)):
    """ Get paginated sensors """
    response = await sensors_service.get_sensors(location, radius, page_size, locations_limit, paging_state)
    return response


@sensors_router.post("/sensors", response_model=SensorBoard)
async def sensor_register(sensor_dto: SensorBoardDTO,
                          sensors_service: SensorsService = Depends(get_sensors_service)):
    """ Upsert sensor """
    added_record = await sensors_service.upsert_sensor(sensor_dto)
    return added_record


@sensors_router.post("/sensors/register", response_model=SensorBoard)
async def sensor_register(sensor_register_dto: SensorBoardRegisterDTO,
                          sensors_service: SensorsService = Depends(get_sensors_service)):
    """ Register sensor """
    added_record = await sensors_service.register_sensor(sensor_register_dto)
    return added_record
