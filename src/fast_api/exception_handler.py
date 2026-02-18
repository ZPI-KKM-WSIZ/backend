from fastapi import Request
from starlette.responses import JSONResponse

from src.fast_api.exceptions.base_exception import AppBaseException


def add_exception_handlers(app):
    @app.exception_handler(AppBaseException)
    async def base_handler(request: Request, exc: AppBaseException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.to_dict()})