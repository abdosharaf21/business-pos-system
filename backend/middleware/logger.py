"""Request and response logging middleware."""

import logging
import time
from typing import Callable

from flask import Request, Response, g, request


logger = logging.getLogger(__name__)


def log_request(request: Request) -> None:
    """Log incoming request details.

    Args:
        request: Flask request object.
    """
    logger.info(
        "Incoming request: %s %s from %s",
        request.method,
        request.url,
        request.remote_addr
    )


def log_response(response: Response, start_time: float) -> None:
    """Log outgoing response details.

    Args:
        response: Flask response object.
        start_time: Request start time.
    """
    duration = time.time() - start_time
    logger.info(
        "Response: %s %s - Status: %s - Duration: %.4fs",
        request.method,
        request.url,
        response.status_code,
        duration
    )


def log_error(error: Exception) -> None:
    """Log error details.

    Args:
        error: Exception that occurred.
    """
    logger.error(
        "Error: %s - %s",
        type(error).__name__,
        str(error),
        exc_info=True
    )
