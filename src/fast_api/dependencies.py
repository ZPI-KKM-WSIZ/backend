from fastapi import Request, Depends

from core.basic_configuration import EnvConfig
from core.cassandra_service import CassandraConfig
from core.database_repositories import Repositories
from core.identity_configuration import IdentityConfig
from fast_api.services.identity_service import IdentityService
from fast_api.services.readings_service import ReadingsService
from fast_api.services.sensors_service import SensorsService


def get_identity(request: Request) -> IdentityConfig:
    """
    Retrieve the server identity from application state.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The IdentityConfig instance stored in app state.
    """
    return request.app.state.identity


def get_cassandra_config(request: Request) -> CassandraConfig:
    """
    Retrieve the Cassandra configuration from application state.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The CassandraConfig instance stored in app state.
    """
    return request.app.state.cassandra_config


def get_env_config_from_app(request: Request) -> EnvConfig:
    """
    Retrieve the environment configuration from application state.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The EnvConfig instance stored in app state.
    """
    return request.app.state.env_config


def get_repositories(request: Request) -> Repositories:
    """
    Retrieve the repository container from application state.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The Repositories instance stored in app state.
    """
    return request.app.state.repositories


def get_identity_service(identity: IdentityConfig = Depends(get_identity)) -> IdentityService:
    """
    Create an IdentityService with injected identity configuration.

    Args:
        identity: The IdentityConfig resolved from app state.

    Returns:
        A new IdentityService instance.
    """
    return IdentityService(identity)


def get_readings_service(repositories: Repositories = Depends(get_repositories)) -> ReadingsService:
    """
    Create a ReadingsService with injected repository dependencies.

    Args:
        repositories: The Repositories container resolved from app state.

    Returns:
        A new ReadingsService instance.
    """
    return ReadingsService(repositories.readings_repository, repositories.sensor_repository,
                           repositories.location_repository)


def get_sensors_service(repositories: Repositories = Depends(get_repositories)) -> SensorsService:
    """
    Create a SensorsService with injected repository dependencies.

    Args:
        repositories: The Repositories container resolved from app state.

    Returns:
        A new SensorsService instance.
    """
    return SensorsService(sensor_repo=repositories.sensor_repository, location_repo=repositories.location_repository,
                          federation_repo=repositories.federation_repository,
                          token_repo=repositories.token_repository)
