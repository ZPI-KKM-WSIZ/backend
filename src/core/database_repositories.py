from dataclasses import dataclass

from contracts import IFederationRepository, ILocationRepository, \
    IReadingsRepository, ITokenRepository, ISensorRepository


@dataclass
class Repositories:
    """
    Container for all repositories used by the application.

    Aggregates every repository interface into a single object for
    convenient dependency injection throughout the application.

    Attributes:
        federation_repository: Repository for federation data access.
        location_repository: Repository for location data access.
        readings_repository: Repository for sensor readings data access.
        sensor_repository: Repository for sensor board data access.
        token_repository: Repository for token data access.
    """

    federation_repository: IFederationRepository
    location_repository: ILocationRepository
    readings_repository: IReadingsRepository
    sensor_repository: ISensorRepository
    token_repository: ITokenRepository
