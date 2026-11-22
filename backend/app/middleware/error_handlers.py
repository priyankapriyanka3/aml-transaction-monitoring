from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with standard error shape"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with standard error shape"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()}
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions with standard error shape"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
