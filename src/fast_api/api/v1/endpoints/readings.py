from contracts import SensorReadingDTO
from fastapi import APIRouter, Depends

from src.fast_api.dependencies import get_readings_service
from src.fast_api.services.readings import ReadingsService

readings_router = APIRouter(prefix="/api/v1")


@readings_router.post("/send_reading")
async def send_reading(reading: SensorReadingDTO,
                 readings_service: ReadingsService = Depends(get_readings_service)
                 ):
    """Process reading and forward to the database"""
    reading_data_model = readings_service.convert_dto_to_db_model(reading)
    reading_saved_or_err = await readings_service.add_reading_to_db(reading_data_model)
    if not reading_saved_or_err:
        return {"status": "failed", "message": f"Error {reading_saved_or_err}"}
    return {"status": "success", "data": reading_data_model}
