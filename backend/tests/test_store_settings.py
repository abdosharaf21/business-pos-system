"""Tests for Store Settings API endpoints and service logic.

Covers the /api/store-settings/* endpoints including retrieving and
updating settings, admin-only access control, validation rules for
store name/phone/email, and logo upload handling.
"""

import io
from unittest.mock import MagicMock, patch

from backend.modules.store_settings.model import StoreSettings
from backend.modules.store_settings.service import StoreSettingsService
from backend.modules.store_settings.validator import StoreSettingsValidator


def _settings_dict(**kw):
    """Create a fake store settings row dict."""
    defaults = dict(
        id=1,
        store_name="My Store",
        owner_name="John Doe",
        phone="+10000000000",
        email="store@example.com",
        address="123 Business Avenue",
        website="https://mystore.com",
        tax_number="TAX-12345",
        currency="EGP",
        receipt_footer="Thank you!",
        logo_path="",
        login_background_path="",
        login_logo_path="",
        login_title="",
        login_subtitle="",
        created_at="2026-08-01T10:00:00",
        updated_at="2026-08-01T10:00:00",
    )
    defaults.update(kw)
    return defaults


def _logo_file(name="logo.png"):
    """Create an in-memory upload file."""
    return io.BytesIO(b"fake-image-bytes"), name


class TestGetSettings:
    """Tests for GET /api/store-settings/."""

    def test_get_settings_success(self, client, admin_headers):
        """Test an authenticated user can read the settings."""
        settings = _settings_dict()
        settings["logo_url"] = "/api/store-settings/logo"
        with patch(
            "backend.modules.store_settings.service.StoreSettingsService.get_settings"
        ) as mock_get:
            mock_get.return_value = settings
            response = client.get("/api/store-settings/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["store_name"] == "My Store"
            assert data["data"]["currency"] == "EGP"

    def test_get_settings_no_token(self, client):
        """Test unauthenticated cannot read the settings."""
        response = client.get("/api/store-settings/")
        assert response.status_code == 401
        assert response.get_json()["success"] is False


class TestUpdateSettings:
    """Tests for PUT /api/store-settings/."""

    def test_update_success(self, client, admin_headers):
        """Test admin can update the settings."""
        with patch(
            "backend.modules.store_settings.service.StoreSettingsService.update_settings"
        ) as mock_update:
            mock_update.return_value = _settings_dict(
                store_name="New Name", logo_url=None
            )
            response = client.put(
                "/api/store-settings/",
                headers=admin_headers,
                json={"store_name": "New Name"},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["store_name"] == "New Name"

    def test_update_employee_forbidden(self, client, employee_headers):
        """Test employees cannot update the settings."""
        response = client.put(
            "/api/store-settings/",
            headers=employee_headers,
            json={"store_name": "New Name"},
        )
        assert response.status_code == 403
        assert response.get_json()["success"] is False

    def test_update_manager_forbidden(self, client, manager_headers):
        """Test managers cannot update the settings."""
        response = client.put(
            "/api/store-settings/",
            headers=manager_headers,
            json={"store_name": "New Name"},
        )
        assert response.status_code == 403

    def test_update_validation_error(self, client, admin_headers):
        """Test invalid data returns 400."""
        with patch(
            "backend.modules.store_settings.service.StoreSettingsService.update_settings"
        ) as mock_update:
            mock_update.side_effect = ValueError("Store name is required")
            response = client.put(
                "/api/store-settings/",
                headers=admin_headers,
                json={"store_name": ""},
            )
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False
            assert data["message"] == "Store name is required"


class TestGetLogo:
    """Tests for GET /api/store-settings/logo."""

    def test_logo_not_found(self, client):
        """Test requesting the logo when none is uploaded returns 404."""
        with patch(
            "backend.modules.store_settings.service.StoreSettingsService.get_settings"
        ) as mock_get:
            mock_get.return_value = _settings_dict(logo_path="")
            response = client.get("/api/store-settings/logo")
            assert response.status_code == 404
            assert response.get_json()["success"] is False

    def test_logo_served_without_token(self, client, tmp_path):
        """Test the logo is public and served with the correct MIME type."""
        import os

        logo_file = tmp_path / "logo.png"
        logo_file.write_bytes(b"\x89PNG\r\n\x1a\nfake-image-bytes")
        with patch(
            "backend.modules.store_settings.service.StoreSettingsService.get_settings"
        ) as mock_get, patch(
            "backend.modules.store_settings.service.StoreSettingsService.resolve_logo_path"
        ) as mock_resolve:
            mock_get.return_value = _settings_dict(logo_path="logo.png")
            mock_resolve.return_value = str(logo_file)
            response = client.get("/api/store-settings/logo")
            assert response.status_code == 200
            assert response.data == logo_file.read_bytes()
            assert response.content_type.startswith("image/png")


class TestGetPublicBranding:
    """Tests for GET /api/store-settings/public."""

    def test_public_branding_without_token(self, client):
        """Test the public endpoint requires no authentication."""
        with patch(
            "backend.modules.store_settings.service.StoreSettingsService.get_public_branding"
        ) as mock_get:
            mock_get.return_value = {
                "store_name": "My Store",
                "login_title": "",
                "login_subtitle": "",
                "login_background_path": None,
                "login_logo_path": None,
                "login_background_url": None,
                "login_logo_url": None,
            }
            response = client.get("/api/store-settings/public")
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["store_name"] == "My Store"

    def test_public_branding_with_urls(self, client):
        """Test the public endpoint exposes login image URLs when set."""
        with patch(
            "backend.modules.store_settings.service.StoreSettingsService.get_public_branding"
        ) as mock_get:
            mock_get.return_value = {
                "store_name": "My Store",
                "login_title": "Welcome",
                "login_subtitle": "Sign in to continue",
                "login_background_path": "bg.png",
                "login_logo_path": "logo.png",
                "login_background_url": "/api/store-settings/login-background",
                "login_logo_url": "/api/store-settings/login-logo",
            }
            response = client.get("/api/store-settings/public")
            data = response.get_json()
            assert data["data"]["login_background_url"] == "/api/store-settings/login-background"
            assert data["data"]["login_logo_url"] == "/api/store-settings/login-logo"


class TestGetLoginAssets:
    """Tests for GET /api/store-settings/login-* endpoints."""

    def test_login_background_not_found(self, client):
        """Test requesting the login background when none exists returns 404."""
        with patch(
            "backend.modules.store_settings.service.StoreSettingsService.get_public_branding"
        ) as mock_get:
            mock_get.return_value = {
                "login_background_path": None,
                "login_logo_path": None,
            }
            response = client.get("/api/store-settings/login-background")
            assert response.status_code == 404

    def test_login_logo_not_found(self, client):
        """Test requesting the login logo when none exists returns 404."""
        with patch(
            "backend.modules.store_settings.service.StoreSettingsService.get_public_branding"
        ) as mock_get:
            mock_get.return_value = {
                "login_background_path": None,
                "login_logo_path": None,
            }
            response = client.get("/api/store-settings/login-logo")
            assert response.status_code == 404


class TestValidator:
    """Tests for the store settings validator."""

    def test_store_name_required(self):
        """Test an empty store name raises ValueError."""
        try:
            StoreSettingsValidator.validate_update({})
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Store name is required" in str(exc)

    def test_store_name_required_when_blank(self):
        """Test a blank store name raises ValueError."""
        try:
            StoreSettingsValidator.validate_update({"store_name": "   "})
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Store name is required" in str(exc)

    def test_invalid_email(self):
        """Test an invalid email raises ValueError."""
        try:
            StoreSettingsValidator.validate_update({
                "store_name": "My Store",
                "email": "not-an-email",
            })
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Invalid email format" in str(exc)

    def test_valid_email(self):
        """Test a valid email passes validation."""
        result = StoreSettingsValidator.validate_update({
            "store_name": "My Store",
            "email": "store@example.com",
        })
        assert result["email"] == "store@example.com"

    def test_invalid_phone(self):
        """Test a phone with invalid characters raises ValueError."""
        try:
            StoreSettingsValidator.validate_update({
                "store_name": "My Store",
                "phone": "abc123",
            })
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "invalid characters" in str(exc)

    def test_phone_too_short(self):
        """Test a phone with too few digits raises ValueError."""
        try:
            StoreSettingsValidator.validate_update({
                "store_name": "My Store",
                "phone": "123",
            })
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "at least 7 digits" in str(exc)

    def test_valid_phone(self):
        """Test a phone with formatting passes validation."""
        result = StoreSettingsValidator.validate_update({
            "store_name": "My Store",
            "phone": "+1 (555) 123-4567",
        })
        assert result["phone"] == "+1 (555) 123-4567"

    def test_currency_defaults_to_egp(self):
        """Test an empty currency defaults to EGP."""
        result = StoreSettingsValidator.validate_update({"store_name": "My Store"})
        assert result["currency"] == "EGP"

    def test_currency_uppercased(self):
        """Test a currency code is uppercased."""
        result = StoreSettingsValidator.validate_update({
            "store_name": "My Store",
            "currency": "usd",
        })
        assert result["currency"] == "USD"

    def test_login_title_defaults_to_empty(self):
        """Test an absent login title defaults to an empty string."""
        result = StoreSettingsValidator.validate_update({"store_name": "My Store"})
        assert result["login_title"] == ""

    def test_login_title_valid(self):
        """Test a login title passes validation."""
        result = StoreSettingsValidator.validate_update({
            "store_name": "My Store",
            "login_title": "Welcome to My Store",
        })
        assert result["login_title"] == "Welcome to My Store"

    def test_login_title_too_long(self):
        """Test an over-long login title raises ValueError."""
        try:
            StoreSettingsValidator.validate_update({
                "store_name": "My Store",
                "login_title": "x" * 151,
            })
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Login title must not exceed 150 characters" in str(exc)

    def test_login_subtitle_defaults_to_empty(self):
        """Test an absent login subtitle defaults to an empty string."""
        result = StoreSettingsValidator.validate_update({"store_name": "My Store"})
        assert result["login_subtitle"] == ""

    def test_login_subtitle_valid(self):
        """Test a login subtitle passes validation."""
        result = StoreSettingsValidator.validate_update({
            "store_name": "My Store",
            "login_subtitle": "Sign in to continue",
        })
        assert result["login_subtitle"] == "Sign in to continue"

    def test_login_subtitle_too_long(self):
        """Test an over-long login subtitle raises ValueError."""
        try:
            StoreSettingsValidator.validate_update({
                "store_name": "My Store",
                "login_subtitle": "x" * 256,
            })
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Login subtitle must not exceed 255 characters" in str(exc)


class TestService:
    """Tests for the store settings service."""

    def test_get_settings_returns_defaults_when_no_row(self):
        """Test get_settings returns defaults when no row exists."""
        repo = MagicMock()
        repo.get_settings.return_value = None
        service = StoreSettingsService(repo)

        result = service.get_settings()

        assert result["store_name"] == ""
        assert result["currency"] == "EGP"
        assert result["logo_path"] is None
        assert result["login_background_path"] is None
        assert result["login_logo_path"] is None
        assert result["login_title"] == ""

    def test_get_settings_includes_logo_url(self):
        """Test get_settings includes a logo URL when a logo exists."""
        repo = MagicMock()
        repo.get_settings.return_value = _settings_dict(logo_path="logo_1.png")
        service = StoreSettingsService(repo)

        result = service.get_settings()

        assert result["logo_url"] == "/api/store-settings/logo"

    def test_get_settings_includes_login_image_urls(self):
        """Test get_settings includes login image URLs when set."""
        repo = MagicMock()
        repo.get_settings.return_value = _settings_dict(
            login_background_path="login_background_1.png",
            login_logo_path="login_logo_1.png",
        )
        service = StoreSettingsService(repo)

        result = service.get_settings()

        assert result["login_background_url"] == "/api/store-settings/login-background"
        assert result["login_logo_url"] == "/api/store-settings/login-logo"

    def test_update_settings_keeps_existing_logo(self):
        """Test updating settings without a file keeps the current logo."""
        repo = MagicMock()
        repo.get_settings.return_value = _settings_dict(logo_path="logo_1.png")
        repo.upsert_settings.side_effect = lambda data: _settings_dict(
            logo_path=data["logo_path"]
        )
        service = StoreSettingsService(repo)

        result = service.update_settings({"store_name": "My Store"})

        assert result["logo_path"] == "logo_1.png"
        assert result["logo_url"] == "/api/store-settings/logo"

    def test_update_settings_removes_logo(self):
        """Test updating settings with remove_logo clears the logo."""
        repo = MagicMock()
        repo.get_settings.return_value = _settings_dict(logo_path="logo_1.png")
        repo.upsert_settings.side_effect = lambda data: _settings_dict(
            logo_path=data["logo_path"]
        )
        service = StoreSettingsService(repo)

        with patch(
            "backend.modules.store_settings.service.os.remove"
        ) as mock_remove:
            result = service.update_settings(
                {"store_name": "My Store"},
                remove_logo=True,
            )

        mock_remove.assert_called_once()
        assert result["logo_path"] is None
        assert "logo_url" not in result

    def test_update_settings_with_logo_file(self, tmp_path, monkeypatch):
        """Test updating settings with a logo saves the file."""
        repo = MagicMock()
        repo.get_settings.return_value = _settings_dict(logo_path="")
        repo.upsert_settings.side_effect = lambda data: _settings_dict(
            logo_path=data["logo_path"]
        )
        service = StoreSettingsService(repo)

        logo_bytes, filename = _logo_file()
        logo_file = MagicMock()
        logo_file.filename = filename
        logo_file.read.return_value = logo_bytes.getvalue()
        logo_file.seek.side_effect = lambda *a, **k: None
        logo_file.tell.side_effect = [0, len(logo_bytes.getvalue())]

        folder = str(tmp_path)
        monkeypatch.setattr(
            "backend.modules.store_settings.service.Config.LOGO_UPLOAD_FOLDER",
            folder,
        )

        with patch(
            "backend.modules.store_settings.service.FileStorage.save"
        ) as mock_save:
            mock_save.return_value = None
            result = service.update_settings(
                {"store_name": "My Store"},
                logo_file=logo_file,
            )

        assert result["logo_path"].startswith("logo_")
        assert result["logo_url"] == "/api/store-settings/logo"

    def test_update_settings_rejects_invalid_extension(self):
        """Test an invalid logo extension raises ValueError."""
        repo = MagicMock()
        repo.get_settings.return_value = None
        service = StoreSettingsService(repo)

        logo_file = MagicMock()
        logo_file.filename = "logo.exe"
        logo_file.seek.side_effect = lambda *a, **k: None
        logo_file.tell.side_effect = [0, 100]

        try:
            service.update_settings({"store_name": "My Store"}, logo_file=logo_file)
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Invalid logo type" in str(exc)

    def test_get_public_branding_defaults(self):
        """Test public branding falls back to empty values when no row."""
        repo = MagicMock()
        repo.get_settings.return_value = None
        service = StoreSettingsService(repo)

        result = service.get_public_branding()

        assert result["store_name"] == ""
        assert result["login_title"] == ""
        assert result["login_subtitle"] == ""
        assert result["login_background_path"] is None
        assert result["login_logo_path"] is None

    def test_get_public_branding_includes_urls(self):
        """Test public branding includes login image URLs when set."""
        repo = MagicMock()
        repo.get_settings.return_value = _settings_dict(
            store_name="Sharaf Market",
            login_background_path="login_background_1.png",
            login_logo_path="login_logo_1.png",
            login_title="Welcome",
            login_subtitle="Sign in to continue",
        )
        service = StoreSettingsService(repo)

        result = service.get_public_branding()

        assert result["store_name"] == "Sharaf Market"
        assert result["login_title"] == "Welcome"
        assert result["login_background_url"] == "/api/store-settings/login-background"
        assert result["login_logo_url"] == "/api/store-settings/login-logo"

    def test_update_settings_with_login_background(self, tmp_path, monkeypatch):
        """Test updating settings with a login background saves the file."""
        repo = MagicMock()
        repo.get_settings.return_value = _settings_dict()
        repo.upsert_settings.side_effect = lambda data: _settings_dict(
            login_background_path=data["login_background_path"]
        )
        service = StoreSettingsService(repo)

        login_file = MagicMock()
        login_file.filename = "bg.png"
        login_file.seek.side_effect = lambda *a, **k: None
        login_file.tell.side_effect = [0, 100]

        monkeypatch.setattr(
            "backend.modules.store_settings.service.Config.LOGIN_UPLOAD_FOLDER",
            str(tmp_path),
        )
        with patch(
            "backend.modules.store_settings.service.FileStorage.save"
        ) as mock_save:
            mock_save.return_value = None
            result = service.update_settings(
                {"store_name": "My Store"},
                login_background_file=login_file,
            )

        assert result["login_background_path"].startswith("login_background_")
        assert result["login_background_url"] == "/api/store-settings/login-background"

    def test_update_settings_with_login_logo(self, tmp_path, monkeypatch):
        """Test updating settings with a login logo saves the file."""
        repo = MagicMock()
        repo.get_settings.return_value = _settings_dict()
        repo.upsert_settings.side_effect = lambda data: _settings_dict(
            login_logo_path=data["login_logo_path"]
        )
        service = StoreSettingsService(repo)

        login_logo = MagicMock()
        login_logo.filename = "brand.png"
        login_logo.seek.side_effect = lambda *a, **k: None
        login_logo.tell.side_effect = [0, 100]

        monkeypatch.setattr(
            "backend.modules.store_settings.service.Config.LOGIN_UPLOAD_FOLDER",
            str(tmp_path),
        )
        with patch(
            "backend.modules.store_settings.service.FileStorage.save"
        ) as mock_save:
            mock_save.return_value = None
            result = service.update_settings(
                {"store_name": "My Store"},
                login_logo_file=login_logo,
            )

        assert result["login_logo_path"].startswith("login_logo_")
        assert result["login_logo_url"] == "/api/store-settings/login-logo"

    def test_update_settings_keeps_existing_login_images(self):
        """Test updating settings without files keeps the current login images."""
        repo = MagicMock()
        repo.get_settings.return_value = _settings_dict(
            login_background_path="login_background_1.png",
            login_logo_path="login_logo_1.png",
        )
        repo.upsert_settings.side_effect = lambda data: _settings_dict(
            login_background_path=data["login_background_path"],
            login_logo_path=data["login_logo_path"],
        )
        service = StoreSettingsService(repo)

        result = service.update_settings({"store_name": "My Store"})

        assert result["login_background_path"] == "login_background_1.png"
        assert result["login_logo_path"] == "login_logo_1.png"

    def test_update_settings_removes_login_background(self):
        """Test removing the login background deletes the file."""
        repo = MagicMock()
        repo.get_settings.return_value = _settings_dict(
            login_background_path="login_background_1.png",
            login_logo_path="login_logo_1.png",
        )
        repo.upsert_settings.side_effect = lambda data: _settings_dict(
            login_background_path=data["login_background_path"],
            login_logo_path=data["login_logo_path"],
        )
        service = StoreSettingsService(repo)

        with patch(
            "backend.modules.store_settings.service.os.remove"
        ) as mock_remove:
            result = service.update_settings(
                {"store_name": "My Store"},
                remove_login_background=True,
            )

        mock_remove.assert_called_once()
        assert result["login_background_path"] is None

    def test_update_settings_removes_login_logo(self):
        """Test removing the login logo deletes the file."""
        repo = MagicMock()
        repo.get_settings.return_value = _settings_dict(
            login_background_path="login_background_1.png",
            login_logo_path="login_logo_1.png",
        )
        repo.upsert_settings.side_effect = lambda data: _settings_dict(
            login_background_path=data["login_background_path"],
            login_logo_path=data["login_logo_path"],
        )
        service = StoreSettingsService(repo)

        with patch(
            "backend.modules.store_settings.service.os.remove"
        ) as mock_remove:
            result = service.update_settings(
                {"store_name": "My Store"},
                remove_login_logo=True,
            )

        mock_remove.assert_called_once()
        assert result["login_logo_path"] is None

    def test_update_settings_removing_login_background_keeps_logo(self):
        """Test removing the login background keeps the login logo file."""
        repo = MagicMock()
        repo.get_settings.return_value = _settings_dict(
            login_background_path="login_background_1.png",
            login_logo_path="login_logo_1.png",
        )
        repo.upsert_settings.side_effect = lambda data: _settings_dict(
            login_background_path=data["login_background_path"],
            login_logo_path=data["login_logo_path"],
        )
        service = StoreSettingsService(repo)

        with patch(
            "backend.modules.store_settings.service.os.remove"
        ) as mock_remove:
            result = service.update_settings(
                {"store_name": "My Store"},
                remove_login_background=True,
            )

        assert result["login_background_path"] is None
        assert result["login_logo_path"] == "login_logo_1.png"

    def test_update_settings_rejects_invalid_login_extension(self):
        """Test an invalid login image extension raises ValueError."""
        repo = MagicMock()
        repo.get_settings.return_value = None
        service = StoreSettingsService(repo)

        login_file = MagicMock()
        login_file.filename = "bg.gif"
        login_file.seek.side_effect = lambda *a, **k: None
        login_file.tell.side_effect = [0, 100]

        try:
            service.update_settings(
                {"store_name": "My Store"},
                login_background_file=login_file,
            )
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Invalid image type" in str(exc)

    def test_model_to_dict_defaults(self):
        """Test StoreSettings model serializes with defaults."""
        settings = StoreSettings()
        result = settings.to_dict()
        assert result["store_name"] == ""
        assert result["currency"] == "EGP"
        assert result["logo_path"] is None
        assert result["login_background_path"] is None
        assert result["login_logo_path"] is None
        assert result["login_title"] == ""
        assert result["login_subtitle"] == ""
        assert "logo_url" not in result
        assert "login_background_url" not in result
        assert "login_logo_url" not in result
