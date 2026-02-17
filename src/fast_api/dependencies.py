from fastapi import Request, Depends

from src.core.database_repositories import Repositories
from src.core.env_configuration import EnvConfig
from src.core.cassandra_configuration import CassandraConfig
from src.core.identity_configuration import IdentityConfig
from src.fast_api.services.identity import IdentityService


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
