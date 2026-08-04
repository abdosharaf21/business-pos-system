"""Routes for the POS (Cashier) interface."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from backend.middleware.rbac import require_authenticated
from backend.modules.pos.service import PosService

pos_bp = Blueprint("pos", __name__, url_prefix="/api/pos")
_pos_service: PosService = None


def init_pos_service(pos_service: PosService) -> None:
    """Initialize the POS service dependency.

    Args:
        pos_service: PosService instance.
    """
    global _pos_service
    _pos_service = pos_service


@pos_bp.route("/products", methods=["GET"])
@require_authenticated
def get_pos_products():
    """Get active products for the POS interface.

    Query params:
        search: Search term for name or barcode.
        barcode: Exact barcode match.
        category_id: Filter by category ID.

    Returns:
        JSON with active products list.
    """
    try:
        search = request.args.get("search", "").strip() or None
        barcode = request.args.get("barcode", "").strip() or None
        category_id = request.args.get("category_id", type=int)

        products = _pos_service.get_active_products(
            search=search, barcode=barcode, category_id=category_id
        )

        return jsonify({
            "success": True,
            "message": "Products retrieved successfully",
            "data": products,
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
        }), 500


@pos_bp.route("/categories", methods=["GET"])
@require_authenticated
def get_pos_categories():
    """Get categories for the POS filter dropdown.

    Returns:
        JSON with categories list.
    """
    try:
        categories = _pos_service.get_categories()
        return jsonify({
            "success": True,
            "message": "Categories retrieved successfully",
            "data": categories,
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
        }), 500


@pos_bp.route("/checkout", methods=["POST"])
@require_authenticated
def create_checkout():
    """Process a POS checkout.

    Body:
        items: List of {product_id, quantity, unit_price}.
        customer_id: Optional customer ID.
        payment_method: Payment method (cash, card, transfer, mixed, vodafone_cash).
        discount: Optional discount amount.

    Returns:
        JSON with completed sale details.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided",
            }), 400

        user_id = int(get_jwt_identity())
        sale = _pos_service.checkout(data, user_id)

        return jsonify({
            "success": True,
            "message": "Checkout completed successfully",
            "data": sale,
        }), 201
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e),
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
        }), 500


@pos_bp.route("/invoice/<int:sale_id>", methods=["GET"])
@require_authenticated
def get_sale_invoice(sale_id: int):
    """Get formatted invoice data for a completed sale.

    Args:
        sale_id: ID of the sale.

    Returns:
        JSON with invoice header, items, and totals.
    """
    try:
        invoice = _pos_service.get_invoice(sale_id)
        return jsonify({
            "success": True,
            "message": "Invoice retrieved successfully",
            "data": invoice,
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e),
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
        }), 500


@pos_bp.route("/customers/search", methods=["GET"])
@require_authenticated
def search_pos_customers():
    """Search customers for the POS checkout modal.

    Query params:
        q: Search term.

    Returns:
        JSON with matching customers list.
    """
    try:
        search = request.args.get("q", "").strip()
        if not search:
            return jsonify({
                "success": True,
                "message": "Customers retrieved successfully",
                "data": [],
            }), 200

        customers = _pos_service.search_customers(search)
        return jsonify({
            "success": True,
            "message": "Customers retrieved successfully",
            "data": customers,
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
        }), 500
