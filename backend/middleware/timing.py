"""Request timing middleware."""

import time
from flask import Request, g


def start_timer() -> None:
    """Start request timer.

    Records the start time of the request in Flask's g context.
    """
    g.start_time = time.time()


def get_request_duration() -> float:
    """Get elapsed request duration.

    Returns:
        Duration in seconds since request started.
    """
    if hasattr(g, "start_time"):
        return time.time() - g.start_time
    return 0.0
