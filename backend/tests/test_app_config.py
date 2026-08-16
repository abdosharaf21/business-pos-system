"""Regression tests for the main application database configuration.

Guards against the misconfiguration that switched the main app to the
``worker_management`` schema (DB defaults flipped to ``worker_management`` /
``worker_mgmt_pool``). These tests ensure the main application resolves to the
``worker_management`` database and ``worker_mgmt_pool`` connection pool unless
explicitly overridden by the environment.
"""

import importlib
import os

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)


def _read_env_file(filename):
    """Read a repository env file as text.

    Args:
        filename: Name of the env file (e.g. ".env").

    Returns:
        Raw file contents.
    """
    path = os.path.join(PROJECT_ROOT, filename)
    assert os.path.isfile(path), f"{filename} file is missing"
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def test_runtime_env_targets_worker_management():
    """The repository .env must target the worker_management database."""
    content = _read_env_file(".env")
    assert "DB_NAME=worker_management" in content
    assert "DB_POOL_NAME=worker_mgmt_pool" in content
    assert "pos_system" not in content.split("DB_NAME=")[1].split("\n")[0]


def test_env_example_targets_worker_management():
    """The documented defaults in .env.example must target worker_management."""
    content = _read_env_file(".env.example")
    assert "DB_NAME=worker_management" in content
    assert "DB_POOL_NAME=worker_mgmt_pool" in content


def test_base_config_defaults_to_worker_management(monkeypatch):
    """BaseConfig resolves to worker_management/worker_mgmt_pool when env vars are absent."""
    monkeypatch.delenv("DB_NAME", raising=False)
    monkeypatch.delenv("DB_POOL_NAME", raising=False)

    import backend.config as config_module

    importlib.reload(config_module)
    assert config_module.BaseConfig.DB_NAME == "worker_management"
    assert config_module.BaseConfig.DB_POOL_NAME == "worker_mgmt_pool"


def test_database_config_defaults_to_worker_management(monkeypatch):
    """DatabaseConfig resolves to worker_management/worker_mgmt_pool when env vars are absent."""
    monkeypatch.delenv("DB_NAME", raising=False)
    monkeypatch.delenv("DB_POOL_NAME", raising=False)

    import backend.database.config as db_config_module

    importlib.reload(db_config_module)
    config = db_config_module.DatabaseConfig()
    assert config.name == "worker_management"
    assert config.pool_name == "worker_mgmt_pool"