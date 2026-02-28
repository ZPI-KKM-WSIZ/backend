import logging
import uuid
from datetime import datetime

from contracts import SensorReadingDTO, SensorReading
from fastapi import APIRouter, Depends

from fast_api.dependencies import get_readings_service
from fast_api.services.readings_service import ReadingsService

readings_router = APIRouter(prefix="/api/v1")


@readings_router.post("/readings", response_model=SensorReading, status_code=201)
async def send_reading(reading: SensorReadingDTO,
                       readings_service: ReadingsService = Depends(get_readings_service)
                       ):
    """
    Process a single sensor reading and store it in the database.
    
    Args:
        reading: The sensor reading data transfer object.
        readings_service: Injected readings service for processing.
        
    Returns:
        The created SensorReading database model.
        
    Raises:
        ConversionException: If the DTO cannot be converted to a database model.
        ReadingInsertException: If the reading cannot be saved to the database.
    """
    logging.debug(f"Received reading: {reading}")
    reading_data_model: SensorReading = await readings_service.convert_dto_to_db_model(reading)
    logging.debug(f"Adding to db: {reading_data_model}")
    await readings_service.add_reading_to_db(reading_data_model)
    return reading_data_model


@readings_router.get("/readings", response_model=list[SensorReading], status_code=201)
async def get_latest(sensor_id: uuid.UUID, start_time: None | datetime = None, end_time: None | datetime = None,
                     limit: int = 1000,
                     readings_service: ReadingsService = Depends(get_readings_service)
                     ):
    return await readings_service.get_readings_by_id(sensor_id, start_time, end_time, limit)


@readings_router.post("/readings/bulk", response_model=list[SensorReading], status_code=201)
async def send_readings_bulk(readings: list[SensorReadingDTO],
                             readings_service: ReadingsService = Depends(get_readings_service)
                             ):
    """
    Process multiple sensor readings in bulk and store them in the database.
    
    Args:
        readings: List of sensor reading data transfer objects.
        readings_service: Injected readings service for processing.
        
    Returns:
        List of created SensorReading database models.
        
    Raises:
        ConversionException: If any DTO cannot be converted to a database model.
        ReadingsBulkInsertException: If the readings cannot be saved or only partially saved.
    """
    logging.debug(f"Received bulk readings {readings}")
    reading_data_models = await readings_service.convert_dto_to_db_model_bulk(readings)
    logging.debug(f"Adding to db: {reading_data_models}")
    await readings_service.add_reading_to_db_bulk(reading_data_models)
    return reading_data_models
