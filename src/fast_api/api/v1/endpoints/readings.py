import logging

from contracts import SensorReadingDTO, SensorReading
from fastapi import APIRouter, Depends

from fast_api.dependencies import get_readings_service
from fast_api.services.readings_service import ReadingsService

readings_router = APIRouter(prefix="/api/v1")


@readings_router.post("/readings", response_model=SensorReading, status_code=201)
async def send_reading(reading: SensorReadingDTO,
                       readings_service: ReadingsService = Depends(get_readings_service)
                       ):
    """Process reading and forward to the database"""
    logging.debug(f"Received reading: {reading}")
    reading_data_model: SensorReading = await readings_service.convert_dto_to_db_model(reading)
    logging.debug(f"Adding to db: {reading_data_model}")
    await readings_service.add_reading_to_db(reading_data_model)
    return reading_data_model


@readings_router.post("/readings/bulk", response_model=list[SensorReading], status_code=201)
async def send_readings_bulk(readings: list[SensorReadingDTO],
                       readings_service: ReadingsService = Depends(get_readings_service)
                       ):
    """Process reading and forward to the database"""
    logging.debug(f"Received bulk readings {readings}")
    reading_data_models = await readings_service.convert_dto_to_db_model_bulk(readings)
    logging.debug(f"Adding to db: {reading_data_models}")
    await readings_service.add_reading_to_db_bulk(reading_data_models)
    return reading_data_models
