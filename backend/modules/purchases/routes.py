"""Purchase routes for purchase-related API endpoints."""

import traceback

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity

from backend.modules.purchases.service import PurchaseService
from backend.middleware.rbac import require_authenticated, require_admin_or_manager

purchases_bp = Blueprint("purchases", __name__, url_prefix="/api/purchases")
suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/api/suppliers")

_purchase_service: PurchaseService = None


def init_purchase_service(purchase_service: PurchaseService) -> None:
    """Initialize the purchase service dependency.

    Args:
        purchase_service: Instance of PurchaseService for dependency injection.
    """
    global _purchase_service
    _purchase_service = purchase_service


# --- Supplier endpoints ---

@suppliers_bp.route("/", methods=["GET"])
@require_authenticated
def get_all_suppliers():
    """Get all suppliers for dropdown selection.

    Returns:
        JSON response with list of suppliers.
    """
    suppliers = _purchase_service.get_all_suppliers()
    return jsonify({
        "success": True,
        "message": "Suppliers retrieved successfully",
        "data": suppliers,
    }), 200


@suppliers_bp.route("/", methods=["POST"])
@require_admin_or_manager
def create_supplier():
    """Create a new supplier from the purchase flow.

    Expects JSON body with name, phone, optional email, optional address.
    Returns the created supplier data for immediate selection.

    Returns:
        JSON response with created supplier.
    """
    try:
        data = request.get_json()
        supplier = _purchase_service.create_supplier(data)
        return jsonify({
            "success": True,
            "message": "Supplier created successfully",
            "data": supplier,
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred while creating the supplier",
        }), 500


@suppliers_bp.route("/<int:supplier_id>", methods=["GET"])
@require_authenticated
def get_supplier(supplier_id: int):
    """Get a single supplier by id.

    Args:
        supplier_id: The unique identifier of the supplier.

    Returns:
        JSON response with the supplier.
    """
    try:
        supplier = _purchase_service.get_supplier(supplier_id)
        return jsonify({
            "success": True,
            "message": "Supplier retrieved successfully",
            "data": supplier,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@suppliers_bp.route("/<int:supplier_id>", methods=["PUT"])
@require_admin_or_manager
def update_supplier(supplier_id: int):
    """Update an existing supplier.

    Expects JSON body with name, phone, optional email, optional address.

    Args:
        supplier_id: The unique identifier of the supplier.

    Returns:
        JSON response with the updated supplier.
    """
    try:
        data = request.get_json()
        supplier = _purchase_service.update_supplier(supplier_id, data)
        return jsonify({
            "success": True,
            "message": "Supplier updated successfully",
            "data": supplier,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred while updating the supplier",
        }), 500


@suppliers_bp.route("/<int:supplier_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_supplier(supplier_id: int):
    """Delete a supplier by id.

    Args:
        supplier_id: The unique identifier of the supplier.

    Returns:
        JSON response confirming the deletion.
    """
    try:
        _purchase_service.delete_supplier(supplier_id)
        return jsonify({
            "success": True,
            "message": "Supplier deleted successfully",
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except Exception:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred while deleting the supplier",
        }), 500


# --- Product search (for purchase item selection) ---

@purchases_bp.route("/products/search", methods=["GET"])
@require_authenticated
def search_products():
    """Search products by name, barcode, or SKU for purchase item selection.

    Query params:
        q: Search term.

    Returns:
        JSON response with matching products.
    """
    query = request.args.get("q", "")
    if not query:
        return jsonify({"success": True, "data": []}), 200
    products = _purchase_service.search_products(query)
    return jsonify({
        "success": True,
        "data": products,
    }), 200


# --- Purchase endpoints ---

@purchases_bp.route("/", methods=["GET"])
@require_authenticated
def get_all_purchases():
    """Get all purchases with optional filters and pagination.

    Query params:
        search: Search term for invoice number or supplier name.
        date: Exact purchase date (YYYY-MM-DD).
        date_from: Start of date range (YYYY-MM-DD).
        date_to: End of date range (YYYY-MM-DD).
        page: Page number (default 1).
        per_page: Records per page (default 20, max 100).
        limit: Legacy records-per-page alias.
        offset: Legacy pagination offset.

    Returns:
        JSON response with paginated purchase list.
    """
    filters = {
        "search": request.args.get("search", "").strip() or None,
        "date": request.args.get("date", "").strip() or None,
        "date_from": request.args.get("date_from", "").strip() or None,
        "date_to": request.args.get("date_to", "").strip() or None,
    }

    if request.args.get("limit", type=int) is not None:
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        purchases = _purchase_service.get_all_purchases(
            search=filters["search"],
            date=filters["date"],
            date_from=filters["date_from"],
            date_to=filters["date_to"],
            limit=limit,
            offset=offset,
        )
        return jsonify({
            "success": True,
            "message": "Purchases retrieved successfully",
            "data": [p.to_dict() for p in purchases],
        }), 200

    filters["page"] = request.args.get("page", 1, type=int)
    filters["per_page"] = request.args.get("per_page", 20, type=int)
    data = _purchase_service.list_purchases(filters)
    return jsonify({
        "success": True,
        "message": "Purchases retrieved successfully",
        "data": data,
    }), 200


@purchases_bp.route("/<int:purchase_id>", methods=["GET"])
@require_authenticated
def get_purchase(purchase_id):
    """Get a purchase by ID with line items.

    Args:
        purchase_id: The unique identifier of the purchase.

    Returns:
        JSON response with purchase data.
    """
    try:
        purchase = _purchase_service.get_purchase(purchase_id)
        return jsonify({
            "success": True,
            "message": "Purchase retrieved successfully",
            "data": purchase.to_dict(),
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@purchases_bp.route("/", methods=["POST"])
@require_admin_or_manager
def create_purchase():
    """Create a new purchase.

    Expects JSON body with supplier_id and items array.
    Each item must have product_id, quantity, cost_price.
    Automatically updates product stock and creates inventory transactions.

    Returns:
        JSON response with created purchase data.
    """
    data = request.get_json()
    user_id = int(get_jwt_identity())
    try:
        purchase = _purchase_service.create_purchase(data, user_id)
        return jsonify({
            "success": True,
            "message": "Purchase created successfully",
            "data": purchase.to_dict(),
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@purchases_bp.route("/<int:purchase_id>/invoice", methods=["GET"])
@require_authenticated
def get_purchase_invoice(purchase_id):
    """Get formatted invoice data for a purchase.

    Args:
        purchase_id: The unique identifier of the purchase.

    Returns:
        JSON response with invoice data.
    """
    try:
        invoice = _purchase_service.get_purchase_invoice(purchase_id)
        return jsonify({
            "success": True,
            "message": "Invoice retrieved successfully",
            "data": invoice,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
