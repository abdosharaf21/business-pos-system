"""Security headers middleware."""

from typing import Callable

from flask import Response


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache"
}


def add_security_headers(response: Response) -> Response:
    """Add security headers to the response.

    Args:
        response: Flask response object.

    Returns:
        Response with security headers added.
    """
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value

    return response


def register_security_headers(app) -> None:
    """Register the security headers middleware for the Flask application.

    Args:
        app: Flask application instance.
    """
    app.after_request(add_security_headers)
