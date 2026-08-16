"""Business development routes for aggregated statistics API endpoints."""

from flask import Blueprint, jsonify

from backend.modules.business_development.service import BusinessDevelopmentService
from backend.middleware.rbac import require_authenticated

business_development_bp = Blueprint(
    "business_development", __name__, url_prefix="/api/business-development"
)

_business_development_service: BusinessDevelopmentService = None


def init_business_development_service(
    business_development_service: BusinessDevelopmentService
) -> None:
    """Initialize the business development service dependency.

    Args:
        business_development_service: Instance of BusinessDevelopmentService
            for dependency injection.
    """
    global _business_development_service
    _business_development_service = business_development_service


@business_development_bp.route("/statistics", methods=["GET"])
@require_authenticated
def get_statistics():
    """Get aggregated business development statistics.

    Returns:
        JSON response with business development statistics.
    """
    statistics = _business_development_service.get_statistics()
    return jsonify({
        "success": True,
        "message": "Business development statistics retrieved successfully",
        "data": statistics
    }), 200
