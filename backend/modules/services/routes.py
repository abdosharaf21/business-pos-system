"""Service routes for service-related API endpoints."""

from flask import Blueprint, request, jsonify

from backend.modules.services.service import ServiceService
from backend.middleware.rbac import require_authenticated, require_admin_or_manager

services_bp = Blueprint("services", __name__, url_prefix="/api/services")

_service_service: ServiceService = None


def init_service_service(service_service: ServiceService) -> None:
    """Initialize the service service dependency.

    Args:
        service_service: Instance of ServiceService for dependency injection.
    """
    global _service_service
    _service_service = service_service


@services_bp.route("/", methods=["GET"])
@require_authenticated
def get_all_services():
    """Get all services.

    Returns:
        JSON response with list of services.
    """
    services = _service_service.get_all_services()
    return jsonify({
        "success": True,
        "message": "Services retrieved successfully",
        "data": [service.to_dict() for service in services]
    }), 200


@services_bp.route("/<int:service_id>", methods=["GET"])
@require_authenticated
def get_service(service_id):
    """Get a service by ID.

    Args:
        service_id: The unique identifier of the service.

    Returns:
        JSON response with service data.
    """
    try:
        service = _service_service.get_service(service_id)
        return jsonify({
            "success": True,
            "message": "Service retrieved successfully",
            "data": service.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@services_bp.route("/category/<int:category_id>", methods=["GET"])
@require_authenticated
def get_services_by_category(category_id):
    """Get all services by category.

    Args:
        category_id: The unique identifier of the category.

    Returns:
        JSON response with list of services.
    """
    services = _service_service.get_services_by_category(category_id)
    return jsonify({
        "success": True,
        "message": "Services retrieved successfully",
        "data": [service.to_dict() for service in services]
    }), 200


@services_bp.route("/", methods=["POST"])
@require_admin_or_manager
def create_service():
    """Create a new service.

    Returns:
        JSON response with created service data.
    """
    data = request.get_json()
    try:
        service = _service_service.create_service(data)
        return jsonify({
            "success": True,
            "message": "Service created successfully",
            "data": service.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@services_bp.route("/<int:service_id>", methods=["PUT"])
@require_admin_or_manager
def update_service(service_id):
    """Update an existing service.

    Args:
        service_id: The unique identifier of the service.

    Returns:
        JSON response with updated service data.
    """
    data = request.get_json()
    try:
        service = _service_service.update_service(service_id, data)
        return jsonify({
            "success": True,
            "message": "Service updated successfully",
            "data": service.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@services_bp.route("/<int:service_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_service(service_id):
    """Delete a service.

    Args:
        service_id: The unique identifier of the service.

    Returns:
        JSON response with result.
    """
    try:
        _service_service.delete_service(service_id)
        return jsonify({"success": True, "message": "Service deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
