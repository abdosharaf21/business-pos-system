"""Product routes for product-related API endpoints."""

from flask import Blueprint, request, jsonify

from backend.modules.products.service import ProductService
from backend.middleware.rbac import require_authenticated, require_admin_or_manager

products_bp = Blueprint("products", __name__, url_prefix="/api/products")

_product_service: ProductService = None


def init_product_service(product_service: ProductService) -> None:
    """Initialize the product service dependency.

    Args:
        product_service: Instance of ProductService for dependency injection.
    """
    global _product_service
    _product_service = product_service


@products_bp.route("/", methods=["GET"])
@require_authenticated
def get_all_products():
    """Get all products with optional search and filters.

    Query params:
        search: Search term for name or barcode.
        category_id: Filter by category ID.
        status: Filter by status (active/inactive).

    Returns:
        JSON response with list of products.
    """
    search = request.args.get("search", "")
    category_id = request.args.get("category_id", type=int)
    status = request.args.get("status", "")

    products = _product_service.get_all_products(
        search=search or None,
        category_id=category_id,
        status=status or None,
    )
    return jsonify({
        "success": True,
        "message": "Products retrieved successfully",
        "data": [product.to_dict() for product in products]
    }), 200


@products_bp.route("/<int:product_id>", methods=["GET"])
@require_authenticated
def get_product(product_id):
    """Get a product by ID.

    Args:
        product_id: The unique identifier of the product.

    Returns:
        JSON response with product data.
    """
    try:
        product = _product_service.get_product(product_id)
        return jsonify({
            "success": True,
            "message": "Product retrieved successfully",
            "data": product.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@products_bp.route("/", methods=["POST"])
@require_admin_or_manager
def create_product():
    """Create a new product.

    Expects JSON body with product fields.

    Returns:
        JSON response with created product data.
    """
    data = request.get_json()
    try:
        product = _product_service.create_product(data)
        return jsonify({
            "success": True,
            "message": "Product created successfully",
            "data": product.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@products_bp.route("/<int:product_id>", methods=["PUT"])
@require_admin_or_manager
def update_product(product_id):
    """Update an existing product.

    Args:
        product_id: The unique identifier of the product.

    Returns:
        JSON response with updated product data.
    """
    data = request.get_json()
    try:
        product = _product_service.update_product(product_id, data)
        return jsonify({
            "success": True,
            "message": "Product updated successfully",
            "data": product.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_product(product_id):
    """Delete a product.

    Args:
        product_id: The unique identifier of the product.

    Returns:
        JSON response with result.
    """
    try:
        _product_service.delete_product(product_id)
        return jsonify({"success": True, "message": "Product deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
