from dataclasses import dataclass

from contracts import IBackendRepository, IRepository, IErrorRepository, IFederationRepository, ILocationRepository, \
    IReadingsRepository, ISensorRepository, ISensorStatusRepository, IVersionRepository


@dataclass
class Repositories:
    """Container for all repositories used by the application."""
    backend_repository: IBackendRepository
    base_repository: IRepository
    error_repository: IErrorRepository
    federation_repository: IFederationRepository
    location_repository: ILocationRepository
    readings_repository: IReadingsRepository
    sensor_repository: ISensorRepository
    sensor_status_repository: ISensorStatusRepository
    version_repository: IVersionRepository
