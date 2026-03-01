from uuid import UUID

from contracts import Location
from fastapi import APIRouter, Depends

from core.location_utils import AddressDTO, location_to_address
from fast_api.dependencies import get_locations_service
from fast_api.services.location_service import LocationsService

locations_router = APIRouter(prefix="/api/v1")


@locations_router.get("/locations/by-sensor", response_model=tuple[Location, AddressDTO])
async def get_location_by_sensor(
        sensor_id: UUID,
        locations_service: LocationsService = Depends(get_locations_service),
):
    """
    Retrieve the location associated with a specific sensor.

    Args:
        sensor_id: UUID of the sensor board to look up.
        locations_service: Injected locations service.

    Returns:
        The Location model linked to the given sensor.

    Raises:
        AppBaseException: 404 if the sensor or its location does not exist.
    """
    location = await locations_service.get_location_by_sensor(sensor_id)
    address = location_to_address(location)
    return location, address
