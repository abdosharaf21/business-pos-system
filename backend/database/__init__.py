"""Database package for the Business Development Web App.

Provides a production-ready connection pool for MySQL with
environment-based configuration.

Usage:
    from backend.database import Database, DatabaseConfig

    db = Database()
    with db.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
"""

from backend.database.connection import Database, DatabaseError, DatabaseConnectionError
from backend.database.config import DatabaseConfig, get_database_config

__all__ = [
    "Database",
    "DatabaseConfig",
    "DatabaseError",
    "DatabaseConnectionError",
    "get_database_config",
]
