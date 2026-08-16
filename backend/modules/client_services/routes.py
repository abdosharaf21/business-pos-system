"""Client service assignment routes for assignment-related API endpoints."""

from flask import Blueprint, request, jsonify

from backend.modules.client_services.service import ClientServiceAssignmentService
from backend.middleware.rbac import require_authenticated, require_admin_or_manager

client_services_bp = Blueprint("client_services", __name__, url_prefix="/api/client-services")

_assignment_service: ClientServiceAssignmentService = None


def init_assignment_service(assignment_service: ClientServiceAssignmentService) -> None:
    """Initialize the assignment service dependency.

    Args:
        assignment_service: Instance of ClientServiceAssignmentService for dependency injection.
    """
    global _assignment_service
    _assignment_service = assignment_service


@client_services_bp.route("/client/<int:client_id>", methods=["GET"])
@require_authenticated
def get_client_services(client_id):
    """Get all services for a specific client.

    Args:
        client_id: The unique identifier of the client.

    Returns:
        JSON response with list of assignments.
    """
    assignments = _assignment_service.get_client_services(client_id)
    return jsonify({
        "success": True,
        "message": "Client services retrieved successfully",
        "data": [assignment.to_dict() for assignment in assignments]
    }), 200


@client_services_bp.route("/service/<int:service_id>", methods=["GET"])
@require_authenticated
def get_service_clients(service_id):
    """Get all clients for a specific service.

    Args:
        service_id: The unique identifier of the service.

    Returns:
        JSON response with list of assignments.
    """
    assignments = _assignment_service.get_service_clients(service_id)
    return jsonify({
        "success": True,
        "message": "Service clients retrieved successfully",
        "data": [assignment.to_dict() for assignment in assignments]
    }), 200


@client_services_bp.route("/<int:client_id>/assign/<int:service_id>", methods=["POST"])
@require_admin_or_manager
def assign_service(client_id, service_id):
    """Assign a service to a client.

    Args:
        client_id: The unique identifier of the client.
        service_id: The unique identifier of the service.

    Returns:
        JSON response with created assignment data.
    """
    data = request.get_json()
    try:
        assignment = _assignment_service.assign_service(client_id, service_id, data)
        return jsonify({
            "success": True,
            "message": "Service assigned successfully",
            "data": assignment.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@client_services_bp.route("/<int:assignment_id>", methods=["PUT"])
@require_admin_or_manager
def update_assignment(assignment_id):
    """Update an existing service assignment.

    Args:
        assignment_id: The unique identifier of the assignment.

    Returns:
        JSON response with updated assignment data.
    """
    data = request.get_json()
    try:
        assignment = _assignment_service.update_assignment(assignment_id, data)
        return jsonify({
            "success": True,
            "message": "Assignment updated successfully",
            "data": assignment.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@client_services_bp.route("/<int:assignment_id>", methods=["DELETE"])
@require_admin_or_manager
def remove_assignment(assignment_id):
    """Remove a service assignment.

    Args:
        assignment_id: The unique identifier of the assignment.

    Returns:
        JSON response with result.
    """
    try:
        _assignment_service.remove_assignment(assignment_id)
        return jsonify({"success": True, "message": "Assignment removed successfully"}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
