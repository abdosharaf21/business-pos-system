"""Tests for User API endpoints.

Tests all /api/users/* endpoints including CRUD operations,
role-based access control, password management, and validation.
"""

from unittest.mock import patch

from backend.modules.users.model import User
from backend.modules.clients.model import Client
from backend.modules.services.model import Service
from backend.modules.service_categories.model import ServiceCategory
from backend.modules.client_services.model import ClientService


def _user(**kw):
    defaults = dict(id=1, full_name="Test", email="t@t.com", password_hash="$2b$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", role="employee", status="active")
    defaults.update(kw)
    return User(**defaults)


def _mock_to_dict(obj, fields):
    return {f: getattr(obj, f) for f in fields if hasattr(obj, f)}


class TestLogin:
    """Tests for POST /api/users/login endpoint."""

    def test_login_success(self, client):
        """Test successful login returns tokens."""
        with patch("backend.modules.users.service.UserService.login") as mock_login:
            mock_login.return_value = {
                "access_token": "test-token",
                "user": {"id": 1, "email": "test@example.com"}
            }
            response = client.post("/api/users/login", json={
                "email": "test@example.com",
                "password": "password123"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_login_missing_email(self, client):
        """Test login with missing email returns 400."""
        response = client.post("/api/users/login", json={"password": "password123"})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Email is required" in data["message"]

    def test_login_missing_password(self, client):
        """Test login with missing password returns 400."""
        response = client.post("/api/users/login", json={"email": "test@example.com"})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Password is required" in data["message"]

    def test_login_invalid_credentials(self, client):
        """Test login with wrong password returns 401."""
        with patch("backend.modules.users.service.UserService.login") as mock_login:
            mock_login.side_effect = ValueError("Invalid email or password")
            response = client.post("/api/users/login", json={
                "email": "test@example.com", "password": "wrong"
            })
            assert response.status_code == 401
            data = response.get_json()
            assert data["success"] is False

    def test_login_inactive_account(self, client):
        """Test login with inactive account returns 401."""
        with patch("backend.modules.users.service.UserService.login") as mock_login:
            mock_login.side_effect = ValueError("Account is inactive")
            response = client.post("/api/users/login", json={
                "email": "inactive@example.com", "password": "password123"
            })
            assert response.status_code == 401
            data = response.get_json()
            assert data["success"] is False


class TestLogout:
    """Tests for POST /api/users/logout endpoint."""

    def test_logout_success(self, client, admin_headers):
        """Test successful logout returns 200."""
        with patch("backend.modules.users.service.UserService.logout") as mock_logout:
            mock_logout.return_value = True
            response = client.post("/api/users/logout", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_logout_no_token(self, client):
        """Test logout without token returns 401."""
        response = client.post("/api/users/logout")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestGetCurrentUser:
    """Tests for GET /api/users/me endpoint."""

    def test_get_current_user_success(self, client, admin_headers):
        """Test get current user returns user data."""
        u = _user(id=1, full_name="Admin User", email="admin@example.com", role="admin")
        with patch("backend.modules.users.service.UserService.get_user_by_id") as mock_get:
            mock_get.return_value = u
            response = client.get("/api/users/me", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["full_name"] == "Admin User"

    def test_get_current_user_no_token(self, client):
        """Test get current user without token returns 401."""
        response = client.get("/api/users/me")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestGetAllUsers:
    """Tests for GET /api/users/ endpoint."""

    def test_get_all_users_admin(self, client, admin_headers):
        """Test admin can list all users."""
        users = [
            _user(id=1, full_name="User 1", email="u1@example.com"),
            _user(id=2, full_name="User 2", email="u2@example.com"),
        ]
        with patch("backend.modules.users.service.UserService.get_all_users") as mock_get:
            mock_get.return_value = users
            response = client.get("/api/users/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert len(data["data"]) == 2

    def test_get_all_users_employee_forbidden(self, client, employee_headers):
        """Test employee cannot list users."""
        response = client.get("/api/users/", headers=employee_headers)
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_get_all_users_no_token(self, client):
        """Test unauthenticated cannot list users."""
        response = client.get("/api/users/")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestGetUserById:
    """Tests for GET /api/users/<id> endpoint."""

    def test_get_user_by_id_success(self, client, admin_headers):
        """Test admin can get a user by ID."""
        u = _user(id=1, full_name="Test User", email="test@example.com")
        with patch("backend.modules.users.service.UserService.get_user_by_id") as mock_get:
            mock_get.return_value = u
            response = client.get("/api/users/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["email"] == "test@example.com"

    def test_get_user_by_id_not_found(self, client, admin_headers):
        """Test get user with non-existent ID returns 404."""
        with patch("backend.modules.users.service.UserService.get_user_by_id") as mock_get:
            mock_get.side_effect = ValueError("User not found")
            response = client.get("/api/users/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_get_user_by_id_employee_forbidden(self, client, employee_headers):
        """Test employee cannot get a user by ID."""
        response = client.get("/api/users/1", headers=employee_headers)
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestCreateUser:
    """Tests for POST /api/users/ endpoint."""

    def test_create_user_success(self, client, admin_headers):
        """Test admin can create a user."""
        u = _user(id=1, full_name="New User", email="new@example.com", role="employee")
        with patch("backend.modules.users.service.UserService.create_user") as mock_create:
            mock_create.return_value = u
            response = client.post("/api/users/", headers=admin_headers, json={
                "full_name": "New User", "email": "new@example.com", "password": "password123"
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["full_name"] == "New User"

    def test_create_user_missing_full_name(self, client, admin_headers):
        """Test create user with missing full_name returns 400."""
        response = client.post("/api/users/", headers=admin_headers, json={
            "email": "new@example.com", "password": "password123"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_user_missing_email(self, client, admin_headers):
        """Test create user with missing email returns 400."""
        response = client.post("/api/users/", headers=admin_headers, json={
            "full_name": "New User", "password": "password123"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_user_missing_password(self, client, admin_headers):
        """Test create user with missing password returns 400."""
        response = client.post("/api/users/", headers=admin_headers, json={
            "full_name": "New User", "email": "new@example.com"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_user_duplicate_email(self, client, admin_headers):
        """Test create user with duplicate email returns 400."""
        with patch("backend.modules.users.service.UserService.create_user") as mock_create:
            mock_create.side_effect = ValueError("Email already exists")
            response = client.post("/api/users/", headers=admin_headers, json={
                "full_name": "New User", "email": "existing@example.com", "password": "password123"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_create_user_employee_forbidden(self, client, employee_headers):
        """Test employee cannot create a user."""
        response = client.post("/api/users/", headers=employee_headers, json={
            "full_name": "New User", "email": "new@example.com", "password": "password123"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_create_user_manager_forbidden(self, client, manager_headers):
        """Test manager cannot create a user."""
        response = client.post("/api/users/", headers=manager_headers, json={
            "full_name": "New User", "email": "new@example.com", "password": "password123"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestUpdateUser:
    """Tests for PUT /api/users/<id> endpoint."""

    def test_update_user_success(self, client, admin_headers):
        """Test admin can update a user."""
        u = _user(id=1, full_name="Updated User", email="updated@example.com")
        with patch("backend.modules.users.service.UserService.update_user") as mock_update:
            mock_update.return_value = u
            response = client.put("/api/users/1", headers=admin_headers, json={
                "full_name": "Updated User"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["full_name"] == "Updated User"

    def test_update_user_not_found(self, client, admin_headers):
        """Test update non-existent user returns 400."""
        with patch("backend.modules.users.service.UserService.update_user") as mock_update:
            mock_update.side_effect = ValueError("User not found")
            response = client.put("/api/users/999", headers=admin_headers, json={
                "full_name": "Updated"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_update_user_employee_forbidden(self, client, employee_headers):
        """Test employee cannot update a user."""
        response = client.put("/api/users/1", headers=employee_headers, json={
            "full_name": "Updated"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestChangePassword:
    """Tests for PUT /api/users/<id>/password endpoint."""

    def test_change_password_success(self, client, admin_headers):
        """Test admin can change a user's password."""
        with patch("backend.modules.users.service.UserService.change_password") as mock_change:
            mock_change.return_value = True
            response = client.put("/api/users/1/password", headers=admin_headers, json={
                "new_password": "newpassword123"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_change_password_missing(self, client, admin_headers):
        """Test change password with missing new_password returns 400."""
        response = client.put("/api/users/1/password", headers=admin_headers, json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "New password is required" in data["message"]

    def test_change_password_user_not_found(self, client, admin_headers):
        """Test change password on non-existent user returns 400."""
        with patch("backend.modules.users.service.UserService.change_password") as mock_change:
            mock_change.side_effect = ValueError("User not found")
            response = client.put("/api/users/999/password", headers=admin_headers, json={
                "new_password": "newpassword123"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_change_password_employee_forbidden(self, client, employee_headers):
        """Test employee cannot change a user's password."""
        response = client.put("/api/users/1/password", headers=employee_headers, json={
            "new_password": "newpassword123"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestActivateDeactivateUser:
    """Tests for PUT /api/users/<id>/activate and deactivate endpoints."""

    def test_activate_user_success(self, client, admin_headers):
        """Test admin can activate a user."""
        u = _user(id=1, status="active")
        with patch("backend.modules.users.service.UserService.activate_user") as mock_activate:
            mock_activate.return_value = u
            response = client.put("/api/users/1/activate", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["status"] == "active"

    def test_deactivate_user_success(self, client, admin_headers):
        """Test admin can deactivate a user."""
        u = _user(id=1, status="inactive")
        with patch("backend.modules.users.service.UserService.deactivate_user") as mock_deactivate:
            mock_deactivate.return_value = u
            response = client.put("/api/users/1/deactivate", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["status"] == "inactive"

    def test_activate_user_not_found(self, client, admin_headers):
        """Test activate non-existent user returns 400."""
        with patch("backend.modules.users.service.UserService.activate_user") as mock_activate:
            mock_activate.side_effect = ValueError("User not found")
            response = client.put("/api/users/999/activate", headers=admin_headers)
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_activate_user_employee_forbidden(self, client, employee_headers):
        """Test employee cannot activate a user."""
        response = client.put("/api/users/1/activate", headers=employee_headers)
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_activate_user_manager_forbidden(self, client, manager_headers):
        """Test manager cannot activate a user."""
        response = client.put("/api/users/1/activate", headers=manager_headers)
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestDeleteUser:
    """Tests for DELETE /api/users/<id> endpoint."""

    def test_delete_user_success(self, client, admin_headers):
        """Test admin can delete a user."""
        with patch("backend.modules.users.service.UserService.delete_user") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/users/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["message"] == "User deleted successfully"

    def test_delete_user_not_found(self, client, admin_headers):
        """Test delete non-existent user returns 404."""
        with patch("backend.modules.users.service.UserService.delete_user") as mock_delete:
            mock_delete.side_effect = ValueError("User not found")
            response = client.delete("/api/users/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_delete_user_employee_forbidden(self, client, employee_headers):
        """Test employee cannot delete a user."""
        response = client.delete("/api/users/1", headers=employee_headers)
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_delete_user_manager_forbidden(self, client, manager_headers):
        """Test manager cannot delete a user."""
        response = client.delete("/api/users/1", headers=manager_headers)
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False
