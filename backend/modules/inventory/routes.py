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
        expiration_status: Optional filter: expired, expiring_soon, normal.
        sort: Optional sort key: expiration (oldest first).

    Returns:
        JSON response with inventory list.
    """
    search = request.args.get("search", "")
    expiration_status = request.args.get("expiration_status", "")
    sort = request.args.get("sort", "")

    try:
        products = _inventory_service.get_inventory(
            search=search or None,
            expiration_status=expiration_status or None,
            sort=sort or None,
        )
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

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
        warehouse_id: Optional warehouse filter.
        start_date: Optional start date (YYYY-MM-DD).
        end_date: Optional end date (YYYY-MM-DD).
        page: Page number (default 1).
        per_page: Items per page (default 20, max 100).

    Returns:
        JSON response with paginated movement list.
    """
    product_id = request.args.get("product_id", type=int)
    movement_type = request.args.get("movement_type")
    warehouse_id = request.args.get("warehouse_id", type=int)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    try:
        movements = _inventory_service.get_movements(
            product_id=product_id,
            movement_type=movement_type,
            warehouse_id=warehouse_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page,
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


@inventory_bp.route("/<int:product_id>/expiration", methods=["PUT"])
@require_admin_or_manager
def update_expiration_date(product_id):
    """Set the expiration date for a product's existing stock.

    Expects a JSON body with expiration_date (YYYY-MM-DD). Applies the
    date to the product's purchase items that have no expiration date yet.

    Returns:
        JSON response with the updated expiration result.
    """
    data = request.get_json(silent=True) or {}
    expiration_date = data.get("expiration_date")

    if not expiration_date:
        return jsonify({"success": False, "message": "Expiration date is required"}), 400

    try:
        result = _inventory_service.update_expiration_date(
            product_id=product_id,
            expiration_date=expiration_date,
        )
        return jsonify({
            "success": True,
            "message": "Expiration date updated successfully",
            "data": result,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


# ----------------------------------------------------------------------
# Warehouses
# ----------------------------------------------------------------------


@inventory_bp.route("/warehouses", methods=["GET"])
@require_authenticated
def list_warehouses():
    """List all warehouses with their total stock.

    Query params:
        active_only: When 'true', only return active warehouses.

    Returns:
        JSON response with the warehouse list.
    """
    active_only = request.args.get("active_only") == "true"
    warehouses = _inventory_service.list_warehouses(active_only=active_only)
    return jsonify({"success": True, "data": warehouses}), 200


@inventory_bp.route("/warehouses", methods=["POST"])
@require_admin_or_manager
def create_warehouse():
    """Create a new warehouse.

    Expects a JSON body with name, code, and optional address,
    manager_name, and phone.

    Returns:
        JSON response with the created warehouse.
    """
    data = request.get_json(silent=True) or {}
    try:
        warehouse = _inventory_service.create_warehouse(data)
        return jsonify({
            "success": True,
            "message": "Warehouse created successfully",
            "data": warehouse,
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@inventory_bp.route("/warehouses/<int:warehouse_id>", methods=["GET"])
@require_authenticated
def get_warehouse(warehouse_id):
    """Get a single warehouse.

    Returns:
        JSON response with the warehouse details.
    """
    try:
        warehouse = _inventory_service.get_warehouse(warehouse_id)
        return jsonify({"success": True, "data": warehouse}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@inventory_bp.route("/warehouses/<int:warehouse_id>", methods=["PUT"])
@require_admin_or_manager
def update_warehouse(warehouse_id):
    """Update an existing warehouse.

    Expects a JSON body with optional name, code, address, manager_name,
    and phone.

    Returns:
        JSON response with the updated warehouse.
    """
    data = request.get_json(silent=True) or {}
    try:
        warehouse = _inventory_service.update_warehouse(warehouse_id, data)
        return jsonify({
            "success": True,
            "message": "Warehouse updated successfully",
            "data": warehouse,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@inventory_bp.route("/warehouses/<int:warehouse_id>/status", methods=["PATCH"])
@require_admin_or_manager
def toggle_warehouse(warehouse_id):
    """Activate or deactivate a warehouse.

    Expects a JSON body with status ('active' or 'inactive').

    Returns:
        JSON response with the updated warehouse.
    """
    data = request.get_json(silent=True) or {}
    try:
        warehouse = _inventory_service.toggle_warehouse(
            warehouse_id, data.get("status")
        )
        return jsonify({
            "success": True,
            "message": "Warehouse status updated successfully",
            "data": warehouse,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@inventory_bp.route("/warehouses/<int:warehouse_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_warehouse(warehouse_id):
    """Delete an empty, non-built-in warehouse.

    Returns:
        JSON response confirming deletion.
    """
    try:
        _inventory_service.delete_warehouse(warehouse_id)
        return jsonify({
            "success": True,
            "message": "Warehouse deleted successfully",
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@inventory_bp.route("/warehouses/<int:warehouse_id>/stock", methods=["GET"])
@require_authenticated
def get_warehouse_stock(warehouse_id):
    """Get the stock held by a specific warehouse.

    Query params:
        search: Optional term to filter by product name or barcode.

    Returns:
        JSON response with the warehouse stock list.
    """
    search = request.args.get("search", "")
    try:
        stock = _inventory_service.get_warehouse_stock(
            warehouse_id, search=search or None
        )
        return jsonify({"success": True, "data": stock}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


# ----------------------------------------------------------------------
# Transfers
# ----------------------------------------------------------------------


@inventory_bp.route("/transfers", methods=["GET"])
@require_authenticated
def list_transfers():
    """List stock transfers with filtering and pagination.

    Query params:
        search: Optional transfer number filter.
        status: Optional status filter (pending, completed, cancelled).
        sort: Optional sort column.
        order: asc or desc.
        page: Page number.
        per_page: Items per page.

    Returns:
        JSON response with the transfer list.
    """
    try:
        result = _inventory_service.list_transfers({
            "search": request.args.get("search"),
            "status": request.args.get("status"),
            "sort": request.args.get("sort", "created_at"),
            "order": request.args.get("order", "desc"),
            "page": request.args.get("page", 1),
            "per_page": request.args.get("per_page", 20),
        })
        return jsonify({"success": True, "data": result}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@inventory_bp.route("/transfers", methods=["POST"])
@require_admin_or_manager
def create_transfer():
    """Create a pending stock transfer.

    Expects a JSON body with source_warehouse_id, destination_warehouse_id,
    items (list of product_id, quantity, cost_price), and optional notes.

    Returns:
        JSON response with the created transfer.
    """
    data = request.get_json(silent=True) or {}
    try:
        user_id = int(get_jwt_identity())
        transfer = _inventory_service.create_transfer(data, user_id)
        return jsonify({
            "success": True,
            "message": "Transfer created successfully",
            "data": transfer,
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@inventory_bp.route("/transfers/<int:transfer_id>", methods=["GET"])
@require_authenticated
def get_transfer(transfer_id):
    """Get a single transfer with its items.

    Returns:
        JSON response with the transfer details.
    """
    try:
        transfer = _inventory_service.get_transfer(transfer_id)
        return jsonify({"success": True, "data": transfer}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@inventory_bp.route("/transfers/<int:transfer_id>/complete", methods=["POST"])
@require_admin_or_manager
def complete_transfer(transfer_id):
    """Complete a pending transfer, moving stock between warehouses.

    Returns:
        JSON response with the completed transfer.
    """
    try:
        user_id = int(get_jwt_identity())
        transfer = _inventory_service.complete_transfer(transfer_id, user_id)
        return jsonify({
            "success": True,
            "message": "Transfer completed successfully",
            "data": transfer,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@inventory_bp.route("/transfers/<int:transfer_id>/cancel", methods=["POST"])
@require_admin_or_manager
def cancel_transfer(transfer_id):
    """Cancel a pending transfer without moving stock.

    Returns:
        JSON response with the cancelled transfer.
    """
    try:
        transfer = _inventory_service.cancel_transfer(transfer_id)
        return jsonify({
            "success": True,
            "message": "Transfer cancelled successfully",
            "data": transfer,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400



