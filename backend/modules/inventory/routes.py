"""Inventory routes for multi-location stock management API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from backend.modules.inventory.service import InventoryService
from backend.middleware.rbac import require_authenticated, require_admin_or_manager

inventory_bp = Blueprint("inventory", __name__, url_prefix="/api/inventory")

_inventory_service: InventoryService = None


def init_inventory_service(inventory_service: InventoryService) -> None:
    """Initialize the inventory service dependency.

    Args:
        inventory_service: Instance of InventoryService for dependency injection.
    """
    global _inventory_service
    _inventory_service = inventory_service


@inventory_bp.route("/", methods=["GET"])
@require_authenticated
def get_inventory():
    """Get all products with per-location stock information.

    Query params:
        search: Optional term to filter by name or barcode.

    Returns:
        JSON response with inventory list.
    """
    search = request.args.get("search", "")
    products = _inventory_service.get_inventory(search=search or None)
    return jsonify({
        "success": True,
        "data": products,
    }), 200


@inventory_bp.route("/summary", methods=["GET"])
@require_authenticated
def get_summary():
    """Get inventory summary statistics.

    Returns:
        JSON response with summary.
    """
    summary = _inventory_service.get_summary()
    return jsonify({
        "success": True,
        "data": summary,
    }), 200


@inventory_bp.route("/low-stock", methods=["GET"])
@require_authenticated
def get_low_stock():
    """Get products with low stock.

    Returns:
        JSON response with low stock products.
    """
    products = _inventory_service.get_low_stock()
    return jsonify({
        "success": True,
        "data": products,
    }), 200


@inventory_bp.route("/movements", methods=["GET"])
@require_authenticated
def get_movements():
    """Get stock movement history with optional filters.

    Query params:
        product_id: Optional product filter.
        movement_type: Optional movement type filter.
        start_date: Optional start date (YYYY-MM-DD).
        end_date: Optional end date (YYYY-MM-DD).
        limit: Maximum records (default 50).
        offset: Pagination offset.

    Returns:
        JSON response with movement list.
    """
    product_id = request.args.get("product_id", type=int)
    movement_type = request.args.get("movement_type")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)

    try:
        movements = _inventory_service.get_movements(
            product_id=product_id,
            movement_type=movement_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        return jsonify({
            "success": True,
            "data": movements,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@inventory_bp.route("/transfer", methods=["POST"])
@require_admin_or_manager
def transfer_stock():
    """Transfer stock from the warehouse to the store.

    Expects JSON body with product_id and quantity.

    Returns:
        JSON response with transfer result.
    """
    data = request.get_json(silent=True) or {}
    try:
        product_id = data.get("product_id")
        quantity = data.get("quantity")

        if not product_id:
            return jsonify({"success": False, "message": "Product ID is required"}), 400
        if quantity is None:
            return jsonify({"success": False, "message": "Quantity is required"}), 400

        user_id = int(get_jwt_identity())
        result = _inventory_service.transfer_stock(
            product_id=int(product_id),
            quantity=int(quantity),
            user_id=user_id,
        )
        return jsonify({
            "success": True,
            "message": "Stock transferred to store successfully",
            "data": result,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@inventory_bp.route("/adjust", methods=["POST"])
@require_admin_or_manager
def adjust_stock():
    """Adjust stock at a location and record the movement.

    Expects JSON body with product_id, location, quantity, and
    movement_type (adjustment, damage, return).

    Returns:
        JSON response with adjustment result.
    """
    data = request.get_json(silent=True) or {}
    try:
        product_id = data.get("product_id")
        location = data.get("location")
        quantity = data.get("quantity")
        movement_type = data.get("movement_type", "adjustment")
        notes = data.get("notes")

        if not product_id:
            return jsonify({"success": False, "message": "Product ID is required"}), 400
        if not location:
            return jsonify({"success": False, "message": "Location is required"}), 400

        user_id = int(get_jwt_identity())
        result = _inventory_service.adjust_stock(
            product_id=int(product_id),
            location=location,
            quantity=int(quantity),
            movement_type=movement_type,
            user_id=user_id,
            notes=notes,
        )
        return jsonify({
            "success": True,
            "message": "Stock adjusted successfully",
            "data": result,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
