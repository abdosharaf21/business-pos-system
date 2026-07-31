"""Application configuration loaded from environment variables."""

import os
import sys

from dotenv import load_dotenv

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cwd = os.getcwd()


def _load_env_file() -> None:
    """Load the .env file from the standard search paths, if present.

    Packaged app places the .env at ``resources/.env`` next to the
    executable; development places it at the project root.
    """
    candidates = []
    env_file = os.environ.get("ENV_FILE")
    if env_file:
        candidates.append(env_file)
    candidates.extend([
        os.path.join(_cwd, '.env'),
        os.path.join(_cwd, 'resources', '.env'),
        os.path.join(_project_root, '.env'),
        os.path.join(_project_root, 'resources', '.env'),
        os.path.normpath(os.path.join(_project_root, '..', '.env')),
    ])
    for path in candidates:
        if path and os.path.isfile(path):
            load_dotenv(path, override=False)
            return
    load_dotenv()


_load_env_file()


class BaseConfig:
    """Base configuration shared across all environments.

    Reads all settings from environment variables. Refuses to start
    if critical secrets are missing.

    Raises:
        ValueError: If required environment variables are not set.
    """

    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", "3306"))
    DB_NAME = os.environ.get("DB_NAME", "pos_system")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_POOL_NAME = os.environ.get("DB_POOL_NAME", "pos_pool")
    DB_POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", "5"))

    JWT_ACCESS_TOKEN_EXPIRES = 3600
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.environ.get("SERVER_PORT", "5001"))
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")

    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5174",
    ).split(",")

    _frontend_dist = os.environ.get(
        "FRONTEND_DIST",
        os.path.join(_project_root, "frontend", "dist"),
    )
    if _frontend_dist and _frontend_dist.startswith("\\\\?\\"):
        _frontend_dist = _frontend_dist[4:]
    FRONTEND_DIST = _frontend_dist
    SERVE_STATIC = False
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        """Validate that all required secrets are configured.

        Raises:
            ValueError: If SECRET_KEY or JWT_SECRET_KEY is missing.
        """
        missing = []
        if not cls.SECRET_KEY:
            missing.append("SECRET_KEY")
        if not cls.JWT_SECRET_KEY:
            missing.append("JWT_SECRET_KEY")
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Set them in your .env file or environment before starting the application."
            )


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(BaseConfig):
    """Production configuration."""

    DEBUG = False
    SERVE_STATIC = True


class DesktopConfig(BaseConfig):
    """Desktop (Electron/Tauri) configuration.

    Frontend is served as static files from the backend or
    connects directly to the backend API.
    """

    DEBUG = False
    SERVE_STATIC = True
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5174,file://",
    ).split(",")


def get_config() -> BaseConfig:
    """Select configuration class based on FLASK_ENV.

    Returns:
        Configuration class instance.
    """
    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        return ProductionConfig
    if env == "desktop":
        return DesktopConfig
    return DevelopmentConfig
