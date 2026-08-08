"""Phase 2 web-readiness tests.

Covers the configurable CORS middleware, config-driven security headers
(CSP/HSTS), and the factory-level database bootstrap flag added for WSGI
deployments. No real database is used; repositories and the connection
pool are mocked as in conftest.
"""

from unittest.mock import MagicMock

import pytest

from backend.app import create_app
from backend.database.bootstrap import BootstrapError

_TEST_SECRET = "web-readiness-test-secret-key-xxxxxxxxxxxxxxxxxxxx"


@pytest.fixture
def web_app(monkeypatch):
    """Factory fixture that builds a mocked app with explicit overrides.

    Patches the connection pool and repositories exactly like conftest so
    ``create_app`` can run without a database, then returns a callable that
    builds an app with the given config overrides.
    """
    monkeypatch.setattr(
        "backend.database.connection.Database._initialize_pool", MagicMock()
    )
    monkeypatch.setattr(
        "backend.modules.auth.repository.AuthRepository", MagicMock()
    )
    monkeypatch.setattr(
        "backend.modules.users.repository.UserRepository", MagicMock()
    )

    def _make(bootstrap=False, **overrides):
        config = {
            "TESTING": True,
            "SECRET_KEY": _TEST_SECRET,
            "JWT_SECRET_KEY": _TEST_SECRET,
        }
        config.update(overrides)
        return create_app(config=config, bootstrap=bootstrap)

    return _make


class TestCors:
    """CORS middleware must be configurable per deployment."""

    def test_echoes_configured_origin_with_credentials(self, web_app):
        """A request from an allowed origin gets it echoed back with Vary."""
        app = web_app(
            CORS_ORIGINS=["https://pos.example.com"],
            CORS_EXPAND_LAN=False,
        )
        response = app.test_client().get(
            "/api/setup/status",
            headers={"Origin": "https://pos.example.com"},
        )
        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Origin"] == "https://pos.example.com"
        assert "Origin" in response.headers.get("Vary", "")
        assert response.headers["Access-Control-Allow-Credentials"] == "true"

    def test_rejects_disallowed_origin(self, web_app):
        """A request from a non-allowed origin gets no allow-origin header."""
        app = web_app(
            CORS_ORIGINS=["https://pos.example.com"],
            CORS_EXPAND_LAN=False,
        )
        response = app.test_client().get(
            "/api/setup/status",
            headers={"Origin": "https://evil.example.com"},
        )
        assert "Access-Control-Allow-Origin" not in response.headers

    def test_wildcard_never_combined_with_credentials(self, web_app):
        """'*' is never paired with Allow-Credentials."""
        app = web_app(CORS_ORIGINS=["*"], CORS_EXPAND_LAN=False)
        response = app.test_client().get(
            "/api/setup/status",
            headers={"Origin": "https://any.example.com"},
        )
        assert "Access-Control-Allow-Origin" not in response.headers
        assert "Access-Control-Allow-Credentials" not in response.headers

    def test_default_dev_origins_allowed(self, client):
        """The default localhost dev origins still work out of the box."""
        response = client.get(
            "/api/setup/status",
            headers={"Origin": "http://localhost:5174"},
        )
        assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:5174"


class TestSecurityHeaders:
    """Security headers must be config-driven (CSP/HSTS opt-in)."""

    def test_dev_defaults_have_base_headers_without_csp_hsts(self, web_app):
        """Base headers ship; CSP and HSTS stay off for dev/Vite HMR."""
        app = web_app(
            SECURITY_HEADERS_ENABLED=True,
            CSP_ENABLED=False,
            HSTS_ENABLED=False,
        )
        response = app.test_client().get("/api/setup/status")
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "Content-Security-Policy" not in response.headers
        assert "Strict-Transport-Security" not in response.headers

    def test_csp_and_hsts_enabled_via_config(self, web_app):
        """Production-style config sends CSP with the configured policy and HSTS."""
        app = web_app(
            CSP_ENABLED=True,
            CSP_POLICY="default-src 'none'",
            HSTS_ENABLED=True,
        )
        response = app.test_client().get("/api/setup/status")
        assert response.headers["Content-Security-Policy"] == "default-src 'none'"
        assert (
            response.headers["Strict-Transport-Security"]
            == "max-age=31536000; includeSubDomains"
        )

    def test_global_disable_suppresses_all_security_headers(self, web_app):
        """SECURITY_HEADERS_ENABLED=false removes every security header."""
        app = web_app(SECURITY_HEADERS_ENABLED=False, CSP_ENABLED=True)
        response = app.test_client().get("/api/setup/status")
        assert "X-Content-Type-Options" not in response.headers
        assert "Content-Security-Policy" not in response.headers


class TestFactoryBootstrap:
    """create_app must optionally run the idempotent database bootstrap."""

    def test_bootstrap_runs_when_requested(self, web_app, monkeypatch):
        """bootstrap=True triggers ensure_database_ready once."""
        mock_bootstrap = MagicMock(
            return_value={"database_created": False, "schema_imported": False, "admin_present": True}
        )
        monkeypatch.setattr("backend.app.ensure_database_ready", mock_bootstrap)
        web_app(bootstrap=True)
        mock_bootstrap.assert_called_once()

    def test_bootstrap_skipped_by_default(self, web_app, monkeypatch):
        """The default factory call must not touch the database bootstrap."""
        mock_bootstrap = MagicMock()
        monkeypatch.setattr("backend.app.ensure_database_ready", mock_bootstrap)
        web_app()
        mock_bootstrap.assert_not_called()

    def test_bootstrap_failure_propagates(self, web_app, monkeypatch):
        """A BootstrapError raised inside the factory must surface to the caller."""
        def _raise_bootstrap_error():
            raise BootstrapError("MySQL unavailable", "Install MySQL")

        monkeypatch.setattr("backend.app.ensure_database_ready", _raise_bootstrap_error)
        with pytest.raises(BootstrapError):
            web_app(bootstrap=True)
