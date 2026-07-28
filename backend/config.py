"""Application configuration loaded from environment variables."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()


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


def get_config() -> BaseConfig:
    """Select configuration class based on FLASK_ENV.

    Returns:
        Configuration class instance.
    """
    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        return ProductionConfig
    return DevelopmentConfig
