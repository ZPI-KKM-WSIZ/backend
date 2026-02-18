from contracts import SensorReadingDTO, SensorReading
from fastapi import APIRouter, Depends

from fast_api.dependencies import get_readings_service
from fast_api.services.readings import ReadingsService

readings_router = APIRouter(prefix="/api/v1")


@readings_router.post("/send_reading", response_model=SensorReading)
async def send_reading(reading: SensorReadingDTO,
                       readings_service: ReadingsService = Depends(get_readings_service)
                       ):
    """Process reading and forward to the database"""
    reading_data_model: SensorReading = readings_service.convert_dto_to_db_model(reading)
    await readings_service.add_reading_to_db(reading_data_model)
    return reading_data_model
