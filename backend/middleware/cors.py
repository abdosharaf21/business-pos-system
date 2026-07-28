"""CORS middleware for Flask application."""

import socket
from typing import List, Optional

from flask import Response, request


def _get_lan_ip() -> str:
    """Detect the machine's LAN IP address.

    Returns:
        LAN IP string, or empty string if detection fails.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return ""


_LAN_IP = _get_lan_ip()
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
if _LAN_IP:
    DEFAULT_ALLOWED_ORIGINS.append(f"http://{_LAN_IP}:5173")
    DEFAULT_ALLOWED_ORIGINS.append(f"http://{_LAN_IP}:3000")
DEFAULT_ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
DEFAULT_ALLOWED_HEADERS = ["Content-Type", "Authorization", "X-Requested-With"]
DEFAULT_EXPOSE_HEADERS = ["Content-Length", "X-Request-Id"]
DEFAULT_MAX_AGE = 3600


def create_cors_middleware(
    allowed_origins: Optional[List[str]] = None,
    allowed_methods: Optional[List[str]] = None,
    allowed_headers: Optional[List[str]] = None,
    expose_headers: Optional[List[str]] = None,
    max_age: int = DEFAULT_MAX_AGE,
    allow_credentials: bool = True
) -> callable:
    """Create CORS middleware with configurable options.

    Args:
        allowed_origins: List of allowed origins.
        allowed_methods: List of allowed HTTP methods.
        allowed_headers: List of allowed headers.
        expose_headers: List of headers to expose to the browser.
        max_age: Maximum age for preflight cache in seconds.
        allow_credentials: Whether to allow credentials.

    Returns:
        CORS middleware function for Flask after_request.
    """
    if allowed_origins is None:
        allowed_origins = DEFAULT_ALLOWED_ORIGINS

    if allowed_methods is None:
        allowed_methods = DEFAULT_ALLOWED_METHODS

    if allowed_headers is None:
        allowed_headers = DEFAULT_ALLOWED_HEADERS

    if expose_headers is None:
        expose_headers = DEFAULT_EXPOSE_HEADERS

    def cors_after_request(response: Response) -> Response:
        """Add CORS headers to the response.

        Args:
            response: Flask response object.

        Returns:
            Response with CORS headers added.
        """
        origin = request.headers.get("Origin")

        if origin and origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
        elif "*" in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"

        response.headers["Access-Control-Allow-Methods"] = ", ".join(allowed_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(allowed_headers)
        response.headers["Access-Control-Expose-Headers"] = ", ".join(expose_headers)
        response.headers["Access-Control-Max-Age"] = str(max_age)

        if allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"

        return response

    return cors_after_request


def handle_preflight_request(response: Response) -> Response:
    """Handle CORS preflight (OPTIONS) requests.

    Args:
        response: Flask response object.

    Returns:
        Response with appropriate CORS headers.
    """
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Methods"] = ", ".join(DEFAULT_ALLOWED_METHODS)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(DEFAULT_ALLOWED_HEADERS)
        response.headers["Access-Control-Max-Age"] = str(DEFAULT_MAX_AGE)

    return response


def register_cors(app, allowed_origins: Optional[List[str]] = None) -> None:
    """Register CORS middleware for the Flask application.

    Args:
        app: Flask application instance.
        allowed_origins: Optional list of allowed origins.
    """
    cors_handler = create_cors_middleware(allowed_origins=allowed_origins)
    app.after_request(cors_handler)
    app.after_request(handle_preflight_request)
