"""Client routes for client-related API endpoints."""

from flask import Blueprint, request, jsonify

from backend.modules.clients.service import ClientService
from backend.middleware.rbac import require_authenticated, require_admin_or_manager

clients_bp = Blueprint("clients", __name__, url_prefix="/api/clients")

_client_service: ClientService = None


def init_client_service(client_service: ClientService) -> None:
    """Initialize the client service dependency.

    Args:
        client_service: Instance of ClientService for dependency injection.
    """
    global _client_service
    _client_service = client_service


@clients_bp.route("/", methods=["GET"])
@require_authenticated
def get_all_clients():
    """Get all clients.

    Returns:
        JSON response with list of clients.
    """
    clients = _client_service.get_all_clients()
    return jsonify({
        "success": True,
        "message": "Clients retrieved successfully",
        "data": [client.to_dict() for client in clients]
    }), 200


@clients_bp.route("/<int:client_id>", methods=["GET"])
@require_authenticated
def get_client(client_id):
    """Get a client by ID.

    Args:
        client_id: The unique identifier of the client.

    Returns:
        JSON response with client data.
    """
    try:
        client = _client_service.get_client(client_id)
        return jsonify({
            "success": True,
            "message": "Client retrieved successfully",
            "data": client.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@clients_bp.route("/", methods=["POST"])
@require_admin_or_manager
def create_client():
    """Create a new client.

    Returns:
        JSON response with created client data.
    """
    data = request.get_json()
    try:
        client = _client_service.create_client(data)
        return jsonify({
            "success": True,
            "message": "Client created successfully",
            "data": client.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@clients_bp.route("/<int:client_id>", methods=["PUT"])
@require_admin_or_manager
def update_client(client_id):
    """Update an existing client.

    Args:
        client_id: The unique identifier of the client.

    Returns:
        JSON response with updated client data.
    """
    data = request.get_json()
    try:
        client = _client_service.update_client(client_id, data)
        return jsonify({
            "success": True,
            "message": "Client updated successfully",
            "data": client.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@clients_bp.route("/<int:client_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_client(client_id):
    """Delete a client.

    Args:
        client_id: The unique identifier of the client.

    Returns:
        JSON response with result.
    """
    try:
        _client_service.delete_client(client_id)
        return jsonify({"success": True, "message": "Client deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@clients_bp.route("/<int:client_id>/status", methods=["PUT"])
@require_admin_or_manager
def change_status(client_id):
    """Change a client's status.

    Args:
        client_id: The unique identifier of the client.

    Returns:
        JSON response with updated client data.
    """
    data = request.get_json()
    try:
        client = _client_service.change_status(client_id, data["status"])
        return jsonify({
            "success": True,
            "message": "Client status changed successfully",
            "data": client.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
