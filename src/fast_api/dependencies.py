from fastapi import Request, Depends

from core.database_repositories import Repositories
from fast_api.services.readings_service import ReadingsService
from core.env_configuration import EnvConfig
from core.cassandra_service import CassandraConfig
from core.identity_configuration import IdentityConfig
from fast_api.services.identity_service import IdentityService


def get_identity(request: Request) -> IdentityConfig:
    """Get identity from the app state"""
    return request.app.state.identity


def get_cassandra_config(request: Request) -> CassandraConfig:
    """Get Cassandra config from the app state"""
    return request.app.state.cassandra_config


def get_env_config_from_app(request: Request) -> EnvConfig:
    """Get env config from the app state"""
    return request.app.state.env_config


def get_repositories(request: Request) -> Repositories:
    """Get env config from the app state"""
    return request.app.state.repositories


def get_identity_service(identity: IdentityConfig = Depends(get_identity)) -> IdentityService:
    """Create InfoService with injected dependencies"""
    return IdentityService(identity)


def get_readings_service(repositories: Repositories = Depends(get_repositories)) -> ReadingsService:
    """Create ReadingsService with injected dependencies"""
    return ReadingsService(repositories.readings_repository, repositories.sensor_repository,
                           repositories.location_repository)
