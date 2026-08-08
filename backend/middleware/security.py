"""Security headers middleware.

Headers are config-driven. CSP and HSTS are opt-in because the defaults
that suit a production HTTPS web deployment (Content-Security-Policy,
Strict-Transport-Security) actively break Vite dev HMR and plain-HTTP
local/LAN hosting.
"""

from typing import Dict, Optional

from flask import Response


BASE_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
}

DEFAULT_CSP_POLICY = (
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; font-src 'self' data:; connect-src 'self'"
)

HSTS_HEADER = "max-age=31536000; includeSubDomains"


def build_security_headers(
    enabled: bool,
    csp_enabled: bool,
    csp_policy: str,
    hsts_enabled: bool,
) -> Dict[str, str]:
    """Build the response security headers from configuration flags.

    Args:
        enabled: Whether security headers are enabled at all.
        csp_enabled: Whether to include the Content-Security-Policy header.
        csp_policy: The Content-Security-Policy value to send.
        hsts_enabled: Whether to include Strict-Transport-Security.

    Returns:
        Dictionary of header name to header value.
    """
    if not enabled:
        return {}
    headers = dict(BASE_SECURITY_HEADERS)
    if csp_enabled:
        headers["Content-Security-Policy"] = csp_policy
    if hsts_enabled:
        headers["Strict-Transport-Security"] = HSTS_HEADER
    return headers


def add_security_headers(response: Response, app=None) -> Response:
    """Add security headers to the response.

    Reads configuration from the Flask app when provided; otherwise uses
    defaults (base headers only, CSP and HSTS off).

    Args:
        response: Flask response object.
        app: Optional Flask app instance to read configuration from.

    Returns:
        Response with security headers added.
    """
    enabled = True
    csp_enabled = False
    csp_policy = DEFAULT_CSP_POLICY
    hsts_enabled = False

    if app is not None:
        config = getattr(app, "config", None)
        if config is not None:
            enabled = config.get("SECURITY_HEADERS_ENABLED", True)
            csp_enabled = config.get("CSP_ENABLED", False)
            csp_policy = config.get("CSP_POLICY", DEFAULT_CSP_POLICY)
            hsts_enabled = config.get("HSTS_ENABLED", False)

    for header, value in build_security_headers(
        enabled=enabled,
        csp_enabled=csp_enabled,
        csp_policy=csp_policy,
        hsts_enabled=hsts_enabled,
    ).items():
        response.headers[header] = value

    return response


def register_security_headers(app) -> None:
    """Register the security headers middleware for the Flask application.

    Args:
        app: Flask application instance.
    """
    app.after_request(lambda response: add_security_headers(response, app=app))
