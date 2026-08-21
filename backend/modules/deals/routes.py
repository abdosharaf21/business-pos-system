"""Deal routes for deal-related API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from backend.modules.deals.service import DealService
from backend.middleware.rbac import require_authenticated, require_admin_or_manager

deals_bp = Blueprint("deals", __name__, url_prefix="/api/deals")

_deal_service: DealService = None


def init_deal_service(deal_service: DealService) -> None:
    """Initialize the deal service dependency.

    Args:
        deal_service: Instance of DealService for dependency injection.
    """
    global _deal_service
    _deal_service = deal_service


@deals_bp.route("/", methods=["GET"])
@require_authenticated
def get_all_deals():
    """Get all deals.

    Returns:
        JSON response with list of deals.
    """
    search = request.args.get("search", "").strip()
    if search:
        deals = _deal_service.search_deals(search)
    else:
        deals = _deal_service.get_all_deals()
    return jsonify({
        "success": True,
        "message": "Deals retrieved successfully",
        "data": [deal.to_dict() for deal in deals]
    }), 200


@deals_bp.route("/<int:deal_id>", methods=["GET"])
@require_authenticated
def get_deal(deal_id):
    """Get a deal by ID.

    Args:
        deal_id: The unique identifier of the deal.

    Returns:
        JSON response with deal data.
    """
    try:
        deal = _deal_service.get_deal(deal_id)
        return jsonify({
            "success": True,
            "message": "Deal retrieved successfully",
            "data": deal.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@deals_bp.route("/", methods=["POST"])
@require_admin_or_manager
def create_deal():
    """Create a new deal.

    Returns:
        JSON response with created deal data.
    """
    data = request.get_json()
    try:
        created_by = int(get_jwt_identity())
        deal = _deal_service.create_deal(data, created_by=created_by)
        return jsonify({
            "success": True,
            "message": "Deal created successfully",
            "data": deal.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@deals_bp.route("/<int:deal_id>", methods=["PUT"])
@require_admin_or_manager
def update_deal(deal_id):
    """Update an existing deal.

    Args:
        deal_id: The unique identifier of the deal.

    Returns:
        JSON response with updated deal data.
    """
    data = request.get_json()
    try:
        deal = _deal_service.update_deal(deal_id, data)
        return jsonify({
            "success": True,
            "message": "Deal updated successfully",
            "data": deal.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@deals_bp.route("/<int:deal_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_deal(deal_id):
    """Delete a deal.

    Args:
        deal_id: The unique identifier of the deal.

    Returns:
        JSON response with result.
    """
    try:
        _deal_service.delete_deal(deal_id)
        return jsonify({"success": True, "message": "Deal deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@deals_bp.route("/<int:deal_id>/status", methods=["PUT"])
@require_admin_or_manager
def change_deal_status(deal_id):
    """Change a deal's status.

    Args:
        deal_id: The unique identifier of the deal.

    Returns:
        JSON response with updated deal data.
    """
    data = request.get_json()
    try:
        deal = _deal_service.change_deal_status(deal_id, data["status"])
        return jsonify({
            "success": True,
            "message": "Deal status changed successfully",
            "data": deal.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@deals_bp.route("/<int:deal_id>/payment-status", methods=["PUT"])
@require_admin_or_manager
def change_payment_status(deal_id):
    """Change a deal's payment status.

    Args:
        deal_id: The unique identifier of the deal.

    Returns:
        JSON response with updated deal data.
    """
    data = request.get_json()
    try:
        deal = _deal_service.change_payment_status(deal_id, data["status"])
        return jsonify({
            "success": True,
            "message": "Payment status changed successfully",
            "data": deal.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@deals_bp.route("/statistics", methods=["GET"])
@require_authenticated
def get_statistics():
    """Get aggregated deal statistics.

    Returns:
        JSON response with deal statistics.
    """
    stats = _deal_service.get_statistics()
    return jsonify({
        "success": True,
        "data": stats
    }), 200


@deals_bp.route("/client/<int:client_id>", methods=["GET"])
@require_authenticated
def get_deals_by_client(client_id):
    """Get all deals for a specific client.

    Args:
        client_id: The unique identifier of the client.

    Returns:
        JSON response with list of deals.
    """
    deals = _deal_service.get_deals_by_client(client_id)
    return jsonify({
        "success": True,
        "message": "Client deals retrieved successfully",
        "data": [deal.to_dict() for deal in deals]
    }), 200


@deals_bp.route("/service/<int:service_id>", methods=["GET"])
@require_authenticated
def get_deals_by_service(service_id):
    """Get all deals for a specific service.

    Args:
        service_id: The unique identifier of the service.

    Returns:
        JSON response with list of deals.
    """
    deals = _deal_service.get_deals_by_service(service_id)
    return jsonify({
        "success": True,
        "message": "Service deals retrieved successfully",
        "data": [deal.to_dict() for deal in deals]
    }), 200
