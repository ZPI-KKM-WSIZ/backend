from enum import Enum


class Environment(Enum):
    """
    Defines the deployment environment for the application.
    
    Attributes:
        PRODUCTION: Production environment with optimized settings.
        DEVELOPMENT: Development environment with enhanced debugging.
    """
    PRODUCTION = "production"
    DEVELOPMENT = "development"
