"""Tests for Authentication API endpoints.

Tests /api/auth/login, /api/auth/logout, /api/auth/refresh,
/api/auth/me, and /api/auth/change-password.
"""

from unittest.mock import MagicMock, patch

from backend.modules.users.model import User


def _user(**kw):
    defaults = dict(id=1, full_name="Test User", email="test@test.com",
                    password_hash="$2b$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                    role="employee", status="active")
    defaults.update(kw)
    return User(**defaults)


class TestAuthServiceSeedCredentials:
    """Regression tests for the canonical admin seed credentials.

    Verifies that the documented default admin account
    (admin@pos.com / 123456) authenticates successfully through the
    real ``AuthService.login`` + bcrypt path using the canonical
    password hash defined by the database bootstrap. This guards
    against login regressions caused by a drifted or mismatched
    password hash in the database.
    """

    def test_admin_seed_credentials_login_succeeds(self, app):
        """admin@pos.com + 123456 must authenticate with the seed hash."""
        from backend.modules.auth.service import AuthService
        from backend.database.bootstrap import ADMIN_PASSWORD_HASH

        admin = _user(
            id=1,
            full_name="Admin User",
            email="admin@pos.com",
            password_hash=ADMIN_PASSWORD_HASH,
            role="admin",
            status="active",
        )
        user_repo = MagicMock()
        user_repo.get_by_email.return_value = admin
        service = AuthService(MagicMock(), user_repo, blocklist=set())

        with app.app_context():
            result = service.login("admin@pos.com", "123456")

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["user"]["email"] == "admin@pos.com"
        assert result["user"]["role"] == "admin"
        user_repo.get_by_email.assert_called_once_with("admin@pos.com")

    def test_admin_seed_credentials_reject_wrong_password(self, app):
        """Wrong password must be rejected even with the seed hash."""
        from backend.modules.auth.service import AuthService
        from backend.middleware.exceptions import UnauthorizedException
        from backend.database.bootstrap import ADMIN_PASSWORD_HASH

        admin = _user(
            id=1,
            full_name="Admin User",
            email="admin@pos.com",
            password_hash=ADMIN_PASSWORD_HASH,
            role="admin",
            status="active",
        )
        user_repo = MagicMock()
        user_repo.get_by_email.return_value = admin
        service = AuthService(MagicMock(), user_repo, blocklist=set())

        with app.app_context():
            try:
                service.login("admin@pos.com", "not-the-password")
            except UnauthorizedException:
                pass
            else:
                raise AssertionError("login with wrong password must raise 401")

    def test_admin_seed_credentials_login_via_api(self, app, client):
        """Full HTTP path: canonical admin credentials return HTTP 200."""
        from backend.modules.auth.routes import _auth_service
        from backend.database.bootstrap import ADMIN_PASSWORD_HASH

        admin = _user(
            id=1,
            full_name="Admin User",
            email="admin@pos.com",
            password_hash=ADMIN_PASSWORD_HASH,
            role="admin",
            status="active",
        )
        user_repo = MagicMock()
        user_repo.get_by_email.return_value = admin
        _auth_service._user_repository = user_repo

        response = client.post("/api/auth/login", json={
            "email": "admin@pos.com", "password": "123456"
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["user"]["email"] == "admin@pos.com"
        assert data["data"]["user"]["role"] == "admin"
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]


class TestAuthLogin:
    """Tests for POST /api/auth/login."""

    def test_login_success(self, client):
        """Test successful login returns tokens + user."""
        with patch("backend.modules.auth.service.AuthService.login") as mock_login:
            mock_login.return_value = {
                "access_token": "test-access",
                "refresh_token": "test-refresh",
                "user": {"id": 1, "email": "test@test.com", "role": "admin"},
            }
            response = client.post("/api/auth/login", json={
                "email": "admin@test.com", "password": "password123"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert "access_token" in data["data"]
            assert "refresh_token" in data["data"]
            assert "user" in data["data"]

    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        with patch("backend.modules.auth.service.AuthService.login") as mock_login:
            from backend.middleware.exceptions import UnauthorizedException
            mock_login.side_effect = UnauthorizedException("Invalid email or password")
            response = client.post("/api/auth/login", json={
                "email": "admin@test.com", "password": "wrong"
            })
            assert response.status_code == 401
            data = response.get_json()
            assert data["success"] is False
            assert "Invalid email or password" in data["message"]

    def test_login_invalid_user(self, client):
        """Test login with non-existent user."""
        with patch("backend.modules.auth.service.AuthService.login") as mock_login:
            from backend.middleware.exceptions import UnauthorizedException
            mock_login.side_effect = UnauthorizedException("Invalid email or password")
            response = client.post("/api/auth/login", json={
                "email": "noone@test.com", "password": "password123"
            })
            assert response.status_code == 401
            data = response.get_json()
            assert data["success"] is False

    def test_login_missing_email(self, client):
        """Test login with missing email returns 400."""
        response = client.post("/api/auth/login", json={"password": "password123"})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_login_missing_password(self, client):
        """Test login with missing password returns 400."""
        response = client.post("/api/auth/login", json={"email": "admin@test.com"})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_login_empty_body(self, client):
        """Test login with empty body returns 400."""
        response = client.post("/api/auth/login", json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_login_inactive_user(self, client):
        """Test login with inactive account."""
        with patch("backend.modules.auth.service.AuthService.login") as mock_login:
            from backend.middleware.exceptions import UnauthorizedException
            mock_login.side_effect = UnauthorizedException("Account is inactive")
            response = client.post("/api/auth/login", json={
                "email": "inactive@test.com", "password": "password123"
            })
            assert response.status_code == 401
            data = response.get_json()
            assert data["success"] is False


class TestAuthLogout:
    """Tests for POST /api/auth/logout."""

    def test_logout_success(self, client, admin_headers, admin_token):
        """Test successful logout returns 200."""
        with patch("backend.modules.auth.service.AuthService.logout") as mock_logout:
            mock_logout.return_value = True
            response = client.post("/api/auth/logout", headers=admin_headers, json={
                "refresh_token": admin_token
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_logout_no_token(self, client):
        """Test logout without token returns 401."""
        response = client.post("/api/auth/logout")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestAuthRefresh:
    """Tests for POST /api/auth/refresh."""

    def test_refresh_success(self, client, admin_refresh_token):
        """Test successful token refresh returns new access token."""
        with patch("backend.modules.auth.service.AuthService.refresh_tokens") as mock_refresh:
            mock_refresh.return_value = {"access_token": "new-access-token"}
            response = client.post("/api/auth/refresh", json={
                "refresh_token": admin_refresh_token
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["access_token"] == "new-access-token"

    def test_refresh_missing_token(self, client):
        """Test refresh with missing token returns 400."""
        response = client.post("/api/auth/refresh", json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid token."""
        with patch("backend.modules.auth.service.AuthService.refresh_tokens") as mock_refresh:
            from backend.middleware.exceptions import UnauthorizedException
            mock_refresh.side_effect = UnauthorizedException("Invalid or expired refresh token")
            response = client.post("/api/auth/refresh", json={
                "refresh_token": "invalid-token"
            })
            assert response.status_code == 401
            data = response.get_json()
            assert data["success"] is False

    def test_refresh_revoked_token(self, client):
        """Test refresh with revoked token."""
        with patch("backend.modules.auth.service.AuthService.refresh_tokens") as mock_refresh:
            from backend.middleware.exceptions import UnauthorizedException
            mock_refresh.side_effect = UnauthorizedException("Refresh token has been revoked")
            response = client.post("/api/auth/refresh", json={
                "refresh_token": "revoked-token"
            })
            assert response.status_code == 401
            data = response.get_json()
            assert data["success"] is False


class TestAuthMe:
    """Tests for GET /api/auth/me."""

    def test_me_success(self, client, admin_headers):
        """Test get current user returns profile."""
        u = _user(id=1, full_name="Admin User", email="admin@test.com", role="admin")
        with patch("backend.modules.auth.service.AuthService.get_current_user") as mock_me:
            mock_me.return_value = u.to_dict()
            response = client.get("/api/auth/me", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["email"] == "admin@test.com"

    def test_me_no_token(self, client):
        """Test get current user without token."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False

    def test_me_user_not_found(self, client, admin_headers):
        """Test get current user when user not found."""
        with patch("backend.modules.auth.service.AuthService.get_current_user") as mock_me:
            from backend.middleware.exceptions import NotFoundException
            mock_me.side_effect = NotFoundException("User not found")
            response = client.get("/api/auth/me", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False


class TestAuthChangePassword:
    """Tests for PUT /api/auth/change-password."""

    def test_change_password_success(self, client, admin_headers):
        """Test successful password change."""
        with patch("backend.modules.auth.service.AuthService.change_password") as mock_change:
            mock_change.return_value = True
            response = client.put("/api/auth/change-password", headers=admin_headers, json={
                "current_password": "old123",
                "new_password": "new123456"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_change_password_no_token(self, client):
        """Test password change without token."""
        response = client.put("/api/auth/change-password", json={
            "current_password": "old", "new_password": "new"
        })
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False

    def test_change_password_short_new(self, client, admin_headers):
        """Test password change with short new password."""
        response = client.put("/api/auth/change-password", headers=admin_headers, json={
            "current_password": "old123",
            "new_password": "abc"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_change_password_missing_fields(self, client, admin_headers):
        """Test password change with missing fields."""
        response = client.put("/api/auth/change-password", headers=admin_headers, json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_change_password_wrong_current(self, client, admin_headers):
        """Test password change with wrong current password."""
        with patch("backend.modules.auth.service.AuthService.change_password") as mock_change:
            from backend.middleware.exceptions import UnauthorizedException
            mock_change.side_effect = UnauthorizedException("Current password is incorrect")
            response = client.put("/api/auth/change-password", headers=admin_headers, json={
                "current_password": "wrong",
                "new_password": "new123456"
            })
            assert response.status_code == 401
            data = response.get_json()
            assert data["success"] is False
