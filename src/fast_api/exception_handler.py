from fastapi import Request
from starlette.responses import JSONResponse

from fast_api.exceptions.base_exception import AppBaseException


def add_exception_handlers(app):
    """
    Register custom exception handlers for the FastAPI application.

    Sets up handlers that convert application exceptions into properly
    formatted JSON responses with appropriate HTTP status codes.

    Args:
        app: The FastAPI application instance to register handlers on.
    """

    @app.exception_handler(AppBaseException)
    async def base_handler(request: Request, exc: AppBaseException):
        """
        Handle all AppBaseException instances and convert them to JSON responses.

        Args:
            request: The incoming request that triggered the exception.
            exc: The application exception instance.

        Returns:
            JSONResponse with error details and appropriate status code.
        """
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.to_dict()})
