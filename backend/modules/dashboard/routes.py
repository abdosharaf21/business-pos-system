"""Dashboard routes for aggregated statistics API endpoints."""

from flask import Blueprint, jsonify

from backend.modules.dashboard.service import DashboardService
from backend.middleware.rbac import require_authenticated

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

_dashboard_service: DashboardService = None


def init_dashboard_service(dashboard_service: DashboardService) -> None:
    """Initialize the dashboard service dependency.

    Args:
        dashboard_service: Instance of DashboardService for dependency injection.
    """
    global _dashboard_service
    _dashboard_service = dashboard_service


@dashboard_bp.route("/statistics", methods=["GET"])
@require_authenticated
def get_statistics():
    """Get aggregated dashboard statistics.

    Returns:
        JSON response with dashboard statistics.
    """
    statistics = _dashboard_service.get_dashboard_statistics()
    return jsonify({
        "success": True,
        "message": "Dashboard statistics retrieved successfully",
        "data": statistics
    }), 200
