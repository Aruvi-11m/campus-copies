"""
Campus Copies ERP - Global Exception Handling & Error Envelopes

Grounding: docs/API.md §1.5, docs/BackendSpecification.md §12
"""

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import logger


class AppException(Exception):
    """Base application exception for all domain business exceptions."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class AuthenticationError(AppException):
    def __init__(
        self, message: str = "Authentication failed", details: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class PermissionDeniedError(AppException):
    def __init__(
        self, message: str = "Permission denied", details: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class NotFoundError(AppException):
    def __init__(
        self, message: str = "Resource not found", details: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class ValidationError(AppException):
    def __init__(
        self, message: str = "Validation failed", details: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class ConflictError(AppException):
    def __init__(
        self, message: str = "Conflict detected", details: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class FileValidationError(AppException):
    def __init__(
        self, message: str = "Invalid file payload", details: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            code="INVALID_FILE",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


def build_error_response(
    code: str, message: str, status_code: int, details: Optional[Any] = None
) -> JSONResponse:
    """Helper to format standard JSON error envelope."""
    payload = {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": jsonable_encoder(details) if details is not None else None,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(status_code=status_code, content=payload)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler for custom business exceptions."""
    logger.warning(
        "app_exception_triggered",
        path=request.url.path,
        code=exc.code,
        status_code=exc.status_code,
        message=exc.message,
    )
    return build_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handler for Pydantic / FastAPI request validation errors."""
    logger.warning(
        "request_validation_failed",
        path=request.url.path,
        errors=jsonable_encoder(exc.errors()),
    )
    return build_error_response(
        code="VALIDATION_ERROR",
        message="Request payload or parameters failed validation",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details=exc.errors(),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global catch-all handler for unexpected internal server errors."""
    logger.error(
        "unhandled_server_exception",
        path=request.url.path,
        error_type=type(exc).__name__,
        error_message=str(exc),
        exc_info=True,
    )
    return build_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected internal server error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
