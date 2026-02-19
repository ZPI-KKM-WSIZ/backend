from dataclasses import dataclass

from contracts import IFederationRepository, ILocationRepository, \
    IReadingsRepository, ITokenRepository, ISensorRepository


@dataclass
class Repositories:
    """Container for all repositories used by the application."""
    federation_repository: IFederationRepository
    location_repository: ILocationRepository
    readings_repository: IReadingsRepository
    sensor_repository: ISensorRepository
    token_repository: ITokenRepository
