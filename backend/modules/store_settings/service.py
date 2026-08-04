"""Store settings service for business configuration business logic."""

import os
from datetime import datetime
from typing import Any, Dict, Optional

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from backend.config import Config
from backend.modules.store_settings.model import StoreSettings
from backend.modules.store_settings.repository import StoreSettingsRepository
from backend.modules.store_settings.validator import StoreSettingsValidator


class StoreSettingsService:
    """Service for store settings business operations.

    Handles validation, image persistence (store logo, login branding),
    and the single-record rule. Communicates only with
    StoreSettingsRepository for data access.
    """

    LOGO_ROUTE = "/api/store-settings/logo"
    LOGIN_BACKGROUND_ROUTE = "/api/store-settings/login-background"
    LOGIN_LOGO_ROUTE = "/api/store-settings/login-logo"

    def __init__(self, settings_repository: StoreSettingsRepository) -> None:
        """Initialize StoreSettingsService with a repository.

        Args:
            settings_repository: Repository for store settings database operations.
        """
        self._repository = settings_repository

    def get_settings(self) -> Dict[str, Any]:
        """Retrieve the current store settings.

        Returns default settings when no row exists yet.

        Returns:
            Dictionary with all settings fields and asset URLs when set.
        """
        row = self._repository.get_settings()
        settings = StoreSettings.from_dict(row) if row else StoreSettings()
        return settings.to_dict(
            logo_url=self.LOGO_ROUTE if settings.logo_path else None,
            login_background_url=(
                self.LOGIN_BACKGROUND_ROUTE
                if settings.login_background_path
                else None
            ),
            login_logo_url=(
                self.LOGIN_LOGO_ROUTE if settings.login_logo_path else None
            ),
        )

    def get_public_branding(self) -> Dict[str, Any]:
        """Retrieve the public login branding fields.

        Intentionally returns only the fields needed by the login page
        so unauthenticated clients never see sensitive settings.

        Returns:
            Dictionary with store name, login title/subtitle, and login
            image URLs when set.
        """
        row = self._repository.get_settings()
        settings = StoreSettings.from_dict(row) if row else StoreSettings()
        return {
            "store_name": settings.store_name,
            "login_title": settings.login_title,
            "login_subtitle": settings.login_subtitle,
            "login_background_path": settings.login_background_path or None,
            "login_logo_path": settings.login_logo_path or None,
            "login_background_url": (
                self.LOGIN_BACKGROUND_ROUTE
                if settings.login_background_path
                else None
            ),
            "login_logo_url": (
                self.LOGIN_LOGO_ROUTE if settings.login_logo_path else None
            ),
        }

    def update_settings(
        self,
        data: Dict[str, Any],
        logo_file: Optional[FileStorage] = None,
        login_background_file: Optional[FileStorage] = None,
        login_logo_file: Optional[FileStorage] = None,
        remove_logo: bool = False,
        remove_login_background: bool = False,
        remove_login_logo: bool = False,
    ) -> Dict[str, Any]:
        """Validate and persist the store settings.

        Optionally saves uploaded images (store logo, login background,
        login logo) or removes existing images via the remove flags
        before updating the row.

        Args:
            data: Dictionary with optional settings fields.
            logo_file: Optional uploaded store logo file.
            login_background_file: Optional uploaded login background file.
            login_logo_file: Optional uploaded login logo file.
            remove_logo: Whether to remove the existing store logo.
            remove_login_background: Whether to remove the login background.
            remove_login_logo: Whether to remove the login logo.

        Returns:
            Dictionary with the updated settings and asset URLs.

        Raises:
            ValueError: If validation fails or an uploaded image is invalid.
        """
        validated = StoreSettingsValidator.validate_update(data)

        current = self._repository.get_settings()
        current_logo = current["logo_path"] if current else ""
        current_background = current["login_background_path"] if current else ""
        current_login_logo = current["login_logo_path"] if current else ""

        validated["logo_path"] = self._resolve_asset(
            current_logo,
            logo_file,
            remove_logo,
            self._save_logo,
            self._delete_logo_file,
        )
        validated["login_background_path"] = self._resolve_asset(
            current_background,
            login_background_file,
            remove_login_background,
            self._save_login_image,
            self._delete_login_image_file,
            prefix="login_background",
        )
        validated["login_logo_path"] = self._resolve_asset(
            current_login_logo,
            login_logo_file,
            remove_login_logo,
            self._save_login_image,
            self._delete_login_image_file,
            prefix="login_logo",
        )

        saved = self._repository.upsert_settings(validated)
        settings = StoreSettings.from_dict(saved)
        return settings.to_dict(
            logo_url=self.LOGO_ROUTE if settings.logo_path else None,
            login_background_url=(
                self.LOGIN_BACKGROUND_ROUTE
                if settings.login_background_path
                else None
            ),
            login_logo_url=(
                self.LOGIN_LOGO_ROUTE if settings.login_logo_path else None
            ),
        )

    # ------------------------------------------------------------------
    # Asset persistence
    # ------------------------------------------------------------------

    def _resolve_asset(
        self,
        current_path: str,
        new_file: Optional[FileStorage],
        remove: bool,
        save_func,
        delete_func,
        prefix: str = "",
    ) -> str:
        """Resolve the persisted asset path for a single field.

        Applies one of three rules: replace (save new file, delete old),
        remove (delete old, clear), or keep (retain current value).

        Args:
            current_path: Currently stored filename.
            new_file: Optional replacement file.
            remove: Whether to remove the current asset.
            save_func: Callable that persists the new file.
            delete_func: Callable that deletes an obsolete file.
            prefix: Filename prefix used by the save function.

        Returns:
            The filename to persist, or an empty string when removed.
        """
        if new_file is not None:
            new_path = save_func(new_file, prefix=prefix) if prefix else save_func(new_file)
            if current_path and current_path != new_path:
                delete_func(current_path)
            return new_path
        if remove:
            if current_path:
                delete_func(current_path)
            return ""
        return current_path

    def _save_logo(self, logo_file: FileStorage, prefix: str = "") -> str:
        """Save an uploaded logo to the uploads folder.

        Args:
            logo_file: The uploaded logo file.
            prefix: Unused filename prefix (logo uses its own naming).

        Returns:
            The stored filename.

        Raises:
            ValueError: If the file is invalid or its type is not allowed.
        """
        if not logo_file or not logo_file.filename:
            raise ValueError("Logo file is required")

        original_name = secure_filename(logo_file.filename)
        if not original_name:
            raise ValueError("Invalid logo filename")

        extension = os.path.splitext(original_name)[1].lower()
        if extension not in Config.ALLOWED_LOGO_EXTENSIONS:
            raise ValueError(
                "Invalid logo type. Allowed: png, jpg, jpeg, gif, webp, svg"
            )

        logo_file.seek(0, os.SEEK_END)
        size = logo_file.tell()
        logo_file.seek(0)
        if size > Config.MAX_LOGO_SIZE:
            raise ValueError("Logo file must not exceed 2 MB")

        os.makedirs(Config.LOGO_UPLOAD_FOLDER, exist_ok=True)

        stored_name = (
            f"logo_{datetime.now().strftime('%Y%m%d%H%M%S')}_{original_name}"
        )
        destination = os.path.join(Config.LOGO_UPLOAD_FOLDER, stored_name)
        logo_file.save(destination)
        return stored_name

    def _save_login_image(
        self, image_file: FileStorage, prefix: str
    ) -> str:
        """Save an uploaded login image (background or logo) to disk.

        Args:
            image_file: The uploaded image file.
            prefix: Filename prefix (login_background or login_logo).

        Returns:
            The stored filename.

        Raises:
            ValueError: If the file is invalid or its type is not allowed.
        """
        if not image_file or not image_file.filename:
            raise ValueError("Login image file is required")

        original_name = secure_filename(image_file.filename)
        if not original_name:
            raise ValueError("Invalid login image filename")

        extension = os.path.splitext(original_name)[1].lower()
        if extension not in Config.ALLOWED_LOGIN_IMAGE_EXTENSIONS:
            raise ValueError(
                "Invalid image type. Allowed: png, jpg, jpeg, webp"
            )

        image_file.seek(0, os.SEEK_END)
        size = image_file.tell()
        image_file.seek(0)
        if size > Config.MAX_LOGIN_IMAGE_SIZE:
            raise ValueError("Image file must not exceed 5 MB")

        os.makedirs(Config.LOGIN_UPLOAD_FOLDER, exist_ok=True)

        stored_name = (
            f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{original_name}"
        )
        destination = os.path.join(Config.LOGIN_UPLOAD_FOLDER, stored_name)
        image_file.save(destination)
        return stored_name

    def _delete_logo_file(self, logo_path: str) -> None:
        """Delete an obsolete logo file from disk.

        Args:
            logo_path: Stored filename to remove.
        """
        if not logo_path:
            return
        filename = secure_filename(os.path.basename(logo_path))
        if not filename:
            return
        try:
            os.remove(os.path.join(Config.LOGO_UPLOAD_FOLDER, filename))
        except OSError:
            pass

    def _delete_login_image_file(self, image_path: str) -> None:
        """Delete an obsolete login image file from disk.

        Args:
            image_path: Stored filename to remove.
        """
        if not image_path:
            return
        filename = secure_filename(os.path.basename(image_path))
        if not filename:
            return
        try:
            os.remove(os.path.join(Config.LOGIN_UPLOAD_FOLDER, filename))
        except OSError:
            pass

    def resolve_logo_path(self, logo_path: str) -> Optional[str]:
        """Resolve a stored logo filename to an absolute filesystem path.

        Args:
            logo_path: Stored logo filename.

        Returns:
            Absolute path to the logo file, or None if it is invalid.
        """
        if not logo_path:
            return None
        filename = secure_filename(os.path.basename(logo_path))
        if not filename:
            return None
        return os.path.join(Config.LOGO_UPLOAD_FOLDER, filename)

    def resolve_login_image_path(self, image_path: str) -> Optional[str]:
        """Resolve a stored login image filename to an absolute path.

        Args:
            image_path: Stored login image filename.

        Returns:
            Absolute path to the image file, or None if it is invalid.
        """
        if not image_path:
            return None
        filename = secure_filename(os.path.basename(image_path))
        if not filename:
            return None
        return os.path.join(Config.LOGIN_UPLOAD_FOLDER, filename)
