"""Middleware package for Flask application."""

from backend.middleware.exceptions import (
    AppException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    ValidationException,
    DatabaseException,
    ServiceUnavailableException
)
from backend.middleware.error_handlers import register_error_handlers
from backend.middleware.logger import log_request, log_response, log_error
from backend.middleware.timing import start_timer, get_request_duration
from backend.middleware.security import register_security_headers, add_security_headers
from backend.middleware.cors import register_cors
from backend.middleware.auth_context import load_user_context, clear_user_context

__all__ = [
    "AppException",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "ConflictException",
    "ValidationException",
    "DatabaseException",
    "ServiceUnavailableException",
    "register_error_handlers",
    "log_request",
    "log_response",
    "log_error",
    "start_timer",
    "get_request_duration",
    "register_security_headers",
    "add_security_headers",
    "register_cors",
    "load_user_context",
    "clear_user_context"
]
