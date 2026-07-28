"""Custom exception classes for the application."""


class AppException(Exception):
    """Base exception class for application errors.

    Attributes:
        message: Error message.
        status_code: HTTP status code.
        success: Always False for errors.
    """

    def __init__(self, message: str = "An error occurred", status_code: int = 400) -> None:
        """Initialize AppException.

        Args:
            message: Error message.
            status_code: HTTP status code.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.success = False

    def to_dict(self) -> dict:
        """Convert exception to dictionary.

        Returns:
            Dictionary representation of the error.
        """
        return {
            "success": self.success,
            "message": self.message,
            "status": self.status_code
        }


class BadRequestException(AppException):
    """Exception for bad request errors (400)."""

    def __init__(self, message: str = "Bad request") -> None:
        """Initialize BadRequestException.

        Args:
            message: Error message.
        """
        super().__init__(message, 400)


class UnauthorizedException(AppException):
    """Exception for unauthorized errors (401)."""

    def __init__(self, message: str = "Unauthorized") -> None:
        """Initialize UnauthorizedException.

        Args:
            message: Error message.
        """
        super().__init__(message, 401)


class ForbiddenException(AppException):
    """Exception for forbidden errors (403)."""

    def __init__(self, message: str = "Access denied") -> None:
        """Initialize ForbiddenException.

        Args:
            message: Error message.
        """
        super().__init__(message, 403)


class NotFoundException(AppException):
    """Exception for not found errors (404)."""

    def __init__(self, message: str = "Resource not found") -> None:
        """Initialize NotFoundException.

        Args:
            message: Error message.
        """
        super().__init__(message, 404)


class ConflictException(AppException):
    """Exception for conflict errors (409)."""

    def __init__(self, message: str = "Resource conflict") -> None:
        """Initialize ConflictException.

        Args:
            message: Error message.
        """
        super().__init__(message, 409)


class ValidationException(AppException):
    """Exception for validation errors (422)."""

    def __init__(self, message: str = "Validation failed", errors: dict = None) -> None:
        """Initialize ValidationException.

        Args:
            message: Error message.
            errors: Dictionary of field-specific validation errors.
        """
        super().__init__(message, 422)
        self.errors = errors or {}

    def to_dict(self) -> dict:
        """Convert exception to dictionary.

        Returns:
            Dictionary representation of the error.
        """
        result = super().to_dict()
        if self.errors:
            result["errors"] = self.errors
        return result


class DatabaseException(AppException):
    """Exception for database errors (500)."""

    def __init__(self, message: str = "Database error occurred") -> None:
        """Initialize DatabaseException.

        Args:
            message: Error message.
        """
        super().__init__(message, 500)


class ServiceUnavailableException(AppException):
    """Exception for service unavailable errors (503)."""

    def __init__(self, message: str = "Service unavailable") -> None:
        """Initialize ServiceUnavailableException.

        Args:
            message: Error message.
        """
        super().__init__(message, 503)
