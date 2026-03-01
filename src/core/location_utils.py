from dataclasses import dataclass

from contracts import Location
from geopy import Nominatim

from core.basic_configuration import get_env_config


@dataclass
class AddressDTO:
    city: str
    state: str
    country: str


def location_to_address(location: Location, language: str = "en") -> AddressDTO:
    server_id = get_env_config().SERVER_ID
    geolocator = Nominatim(user_agent=f"zpi-backend-{server_id}")
    loc = geolocator.reverse(f"{location.localization_lat}, {location.localization_lon}", language=language)
    address = loc.raw.get('address', {})

    city = address.get('city', '')
    state = address.get('state', '')
    country = address.get('country', '')
    return AddressDTO(city=city, state=state, country=country)
