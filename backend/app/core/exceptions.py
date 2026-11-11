"""AapadaOps Structured Exception Handling Module."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception with structured error metadata."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}


class NotFoundError(AppException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "identifier": str(identifier)},
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication credentials are required or invalid."):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
        )


class ForbiddenError(AppException):
    def __init__(self, message: str = "Access denied. Insufficient operational permissions."):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            code="PERMISSION_DENIED",
        )


class ConflictError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT_ERROR",
            details=details,
        )


class InvalidStateTransitionError(AppException):
    def __init__(self, current_state: str, attempted_state: str, reason: str = ""):
        super().__init__(
            message=(
                f"Invalid incident lifecycle transition: '{current_state}' -> '{attempted_state}'. "
                + (f"Reason: {reason}" if reason else "")
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_STATE_TRANSITION",
            details={"current_state": current_state, "attempted_state": attempted_state},
        )


class RateLimitExceededError(AppException):
    def __init__(self, retry_after_seconds: int = 60):
        super().__init__(
            message="Rate limit exceeded. Emergency operation system safety throttling active.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED",
            details={"retry_after_seconds": retry_after_seconds},
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """FastAPI global exception handler for structured application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": request.url.path,
            }
        },
    )

