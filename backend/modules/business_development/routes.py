"""Routes for Business Development dashboard statistics."""

from flask import Blueprint, jsonify
from backend.middleware.rbac import require_authenticated

business_development_bp = Blueprint(
    "business_development", __name__, url_prefix="/api/business-development"
)

_service = None


def init_business_development_service(service):
    global _service
    _service = service


@business_development_bp.get("/statistics")
@require_authenticated
def get_statistics():
    """Return aggregated BD dashboard statistics."""
    data = _service.get_statistics()
    return jsonify({"success": True, "data": data})
