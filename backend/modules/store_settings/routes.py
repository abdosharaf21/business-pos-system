"""Store settings routes for business configuration API endpoints."""

import os

from flask import Blueprint, jsonify, request, send_file

from backend.modules.store_settings.service import StoreSettingsService
from backend.middleware.rbac import require_authenticated, require_admin

store_settings_bp = Blueprint(
    "store_settings", __name__, url_prefix="/api/store-settings"
)

_store_settings_service: StoreSettingsService = None


def init_store_settings_service(service: StoreSettingsService) -> None:
    """Initialize the store settings service dependency.

    Args:
        service: Instance of StoreSettingsService for dependency injection.
    """
    global _store_settings_service
    _store_settings_service = service


@store_settings_bp.route("/", methods=["GET"])
@require_authenticated
def get_settings():
    """Get the current store settings.

    Returns:
        JSON response with the store settings.
    """
    settings = _store_settings_service.get_settings()
    return jsonify({"success": True, "data": settings}), 200


@store_settings_bp.route("/public", methods=["GET"])
def get_public_branding():
    """Get the public login branding fields.

    This endpoint requires no authentication because the login page
    must read branding before the user signs in. It only exposes the
    fields needed to render the login page.

    Returns:
        JSON response with the public login branding data.
    """
    branding = _store_settings_service.get_public_branding()
    return jsonify({"success": True, "data": branding}), 200


@store_settings_bp.route("/", methods=["PUT"])
@require_admin
def update_settings():
    """Update the store settings.

    Accepts application/json or multipart/form-data. A multipart request
    may include ``logo``, ``login_background`` and ``login_logo`` file
    parts.

    Returns:
        JSON response with the updated settings.

    Raises:
        400: If validation fails.
    """
    try:
        logo_file = request.files.get("logo") if request.files else None
        login_background_file = (
            request.files.get("login_background") if request.files else None
        )
        login_logo_file = (
            request.files.get("login_logo") if request.files else None
        )

        if request.form:
            data = {key: value for key, value in request.form.items()}
            remove_logo = str(data.pop("remove_logo", "")).lower() in ("1", "true", "yes")
            remove_login_background = str(
                data.pop("remove_login_background", "")
            ).lower() in ("1", "true", "yes")
            remove_login_logo = str(
                data.pop("remove_login_logo", "")
            ).lower() in ("1", "true", "yes")
        else:
            data = request.get_json(silent=True) or {}
            remove_logo = bool(data.pop("remove_logo", False))
            remove_login_background = bool(
                data.pop("remove_login_background", False)
            )
            remove_login_logo = bool(data.pop("remove_login_logo", False))

        settings = _store_settings_service.update_settings(
            data=data,
            logo_file=logo_file,
            login_background_file=login_background_file,
            login_logo_file=login_logo_file,
            remove_logo=remove_logo,
            remove_login_background=remove_login_background,
            remove_login_logo=remove_login_logo,
        )
        return jsonify({
            "success": True,
            "message": "Store settings updated successfully",
            "data": settings,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@store_settings_bp.route("/logo", methods=["GET"])
@require_authenticated
def get_logo():
    """Serve the uploaded store logo image.

    Returns:
        The logo image file.

    Raises:
        404: If no logo has been uploaded.
    """
    settings = _store_settings_service.get_settings()
    logo_path = settings.get("logo_path")

    if not logo_path:
        return jsonify({"success": False, "message": "No logo uploaded"}), 404

    resolved = _store_settings_service.resolve_logo_path(logo_path)

    if resolved is None or not os.path.isfile(resolved):
        return jsonify({"success": False, "message": "Logo file not found"}), 404

    return send_file(resolved, mimetype="image/*", conditional=True)


@store_settings_bp.route("/login-background", methods=["GET"])
def get_login_background():
    """Serve the uploaded login page background image.

    This endpoint requires no authentication so the login page can
    render the background before the user signs in.

    Returns:
        The login background image file.

    Raises:
        404: If no login background has been uploaded.
    """
    branding = _store_settings_service.get_public_branding()
    image_path = branding.get("login_background_path")

    if not image_path:
        return jsonify({"success": False, "message": "No login background uploaded"}), 404

    resolved = _store_settings_service.resolve_login_image_path(image_path)

    if resolved is None or not os.path.isfile(resolved):
        return jsonify({"success": False, "message": "Login background file not found"}), 404

    return send_file(resolved, mimetype="image/*", conditional=True)


@store_settings_bp.route("/login-logo", methods=["GET"])
def get_login_logo():
    """Serve the uploaded login page logo image.

    This endpoint requires no authentication so the login page can
    render the logo before the user signs in.

    Returns:
        The login logo image file.

    Raises:
        404: If no login logo has been uploaded.
    """
    branding = _store_settings_service.get_public_branding()
    image_path = branding.get("login_logo_path")

    if not image_path:
        return jsonify({"success": False, "message": "No login logo uploaded"}), 404

    resolved = _store_settings_service.resolve_login_image_path(image_path)

    if resolved is None or not os.path.isfile(resolved):
        return jsonify({"success": False, "message": "Login logo file not found"}), 404

    return send_file(resolved, mimetype="image/*", conditional=True)
