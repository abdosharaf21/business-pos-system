"""Inventory routes for stock management API endpoints."""

from flask import Blueprint, request, jsonify

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
    """Get all products with stock information.

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


@inventory_bp.route("/transactions", methods=["GET"])
@require_authenticated
def get_transactions():
    """Get inventory transaction history.

    Returns:
        JSON response with transaction list.
    """
    product_id = request.args.get("product_id", type=int)
    limit = request.args.get("limit", 50, type=int)
    transactions = _inventory_service.get_transactions(
        product_id=product_id, limit=limit
    )
    return jsonify({
        "success": True,
        "data": transactions,
    }), 200


@inventory_bp.route("/", methods=["POST"])
@require_admin_or_manager
def adjust_stock():
    """Adjust product stock level.

    Expects JSON body with product_id, type, quantity.
    Positive quantity adds stock, negative removes stock.

    Returns:
        JSON response with adjustment result.
    """
    data = request.get_json(silent=True) or {}
    try:
        product_id = data.get("product_id")
        transaction_type = data.get("type")
        quantity = data.get("quantity", 0)
        reference_id = data.get("reference_id")

        if not product_id:
            return jsonify({"success": False, "message": "Product ID is required"}), 400

        result = _inventory_service.adjust_stock(
            product_id=int(product_id),
            transaction_type=transaction_type,
            quantity=int(quantity),
            reference_id=reference_id,
        )
        return jsonify({
            "success": True,
            "message": "Stock adjusted successfully",
            "data": result,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
