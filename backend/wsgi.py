"""WSGI entry point for web deployments.

Run with gunicorn from the repository root::

    backend/.venv/bin/gunicorn --bind 0.0.0.0:5001 backend.wsgi:application

The database bootstrap runs once per worker process on import. It is
idempotent and non-destructive; use ``--preload`` to run module-level
code (including the bootstrap) a single time before forking workers.
"""

import logging

from backend.app import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

application = create_app(bootstrap=True)

app = application
