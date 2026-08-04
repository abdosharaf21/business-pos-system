"""Notification routes for the in-app notification center API."""

from flask import Blueprint, jsonify, request

from backend.modules.notifications.service import NotificationService
from backend.middleware.rbac import require_authenticated, require_admin_or_manager

notifications_bp = Blueprint(
    "notifications", __name__, url_prefix="/api/notifications"
)

_notification_service: NotificationService = None


def init_notification_service(notification_service: NotificationService) -> None:
    """Initialize the notification service dependency.

    Args:
        notification_service: Instance of NotificationService for dependency injection.
    """
    global _notification_service
    _notification_service = notification_service


@notifications_bp.route("/", methods=["GET"])
@require_authenticated
def get_notifications():
    """List notifications with optional filters.

    Query params:
        notification_type: Optional filter: low_stock, out_of_stock,
            expired, expiring_soon.
        priority: Optional filter: critical, warning.
        unread_only: When 1/true, return only unread notifications.
        limit: Optional maximum number of notifications to return.

    Returns:
        JSON response with the notification list.
    """
    notification_type = request.args.get("notification_type") or None
    priority = request.args.get("priority") or None
    unread_only = request.args.get("unread_only", "false").lower() in ("1", "true", "yes")
    limit = request.args.get("limit", type=int)

    try:
        notifications = _notification_service.get_notifications(
            notification_type=notification_type,
            priority=priority,
            unread_only=unread_only,
            limit=limit,
        )
        return jsonify({"success": True, "data": notifications}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@notifications_bp.route("/unread-count", methods=["GET"])
@require_authenticated
def get_unread_count():
    """Count unread notifications.

    Returns:
        JSON response with the unread count.
    """
    count = _notification_service.get_unread_count()
    return jsonify({"success": True, "data": {"unread_count": count}}), 200


@notifications_bp.route("/sync", methods=["POST"])
@require_admin_or_manager
def sync_notifications():
    """Regenerate notifications from current product state.

    Returns:
        JSON response with created, updated, and deleted counts.
    """
    result = _notification_service.sync_notifications()
    return jsonify({
        "success": True,
        "message": "Notifications synchronized successfully",
        "data": result,
    }), 200


@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@require_authenticated
def mark_as_read(notification_id):
    """Mark a single notification as read.

    Args:
        notification_id: ID of the notification to mark read.

    Returns:
        JSON response confirming the update.
    """
    try:
        result = _notification_service.mark_as_read(notification_id)
        return jsonify({
            "success": True,
            "message": "Notification marked as read",
            "data": result,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@notifications_bp.route("/read-all", methods=["POST"])
@require_authenticated
def mark_all_as_read():
    """Mark every notification as read.

    Returns:
        JSON response with the number of notifications updated.
    """
    count = _notification_service.mark_all_as_read()
    return jsonify({
        "success": True,
        "message": "All notifications marked as read",
        "data": {"updated": count},
    }), 200
