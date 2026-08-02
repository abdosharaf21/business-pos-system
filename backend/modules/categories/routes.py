"""Category routes for category-related API endpoints."""

from flask import Blueprint, request, jsonify

from backend.modules.categories.service import CategoryService
from backend.middleware.rbac import require_authenticated, require_admin_or_manager

categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")

_category_service: CategoryService = None


def init_category_service(category_service: CategoryService) -> None:
    """Initialize the category service dependency.

    Args:
        category_service: Instance of CategoryService for dependency injection.
    """
    global _category_service
    _category_service = category_service


@categories_bp.route("/", methods=["GET"])
@require_authenticated
def get_all_categories():
    """Get all categories.

    Returns:
        JSON response with list of categories.
    """
    categories = _category_service.get_all_categories()
    return jsonify({
        "success": True,
        "message": "Categories retrieved successfully",
        "data": [category.to_dict() for category in categories]
    }), 200


@categories_bp.route("/tree", methods=["GET"])
@require_authenticated
def get_category_tree():
    """Get all categories as a nested tree.

    Returns:
        JSON response with the category tree.
    """
    tree = _category_service.get_category_tree()
    return jsonify({
        "success": True,
        "message": "Category tree retrieved successfully",
        "data": tree
    }), 200


@categories_bp.route("/<int:category_id>", methods=["GET"])
@require_authenticated
def get_category(category_id):
    """Get a category by ID.

    Args:
        category_id: The unique identifier of the category.

    Returns:
        JSON response with category data.
    """
    try:
        category = _category_service.get_category(category_id)
        return jsonify({
            "success": True,
            "message": "Category retrieved successfully",
            "data": category.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@categories_bp.route("/", methods=["POST"])
@require_admin_or_manager
def create_category():
    """Create a new category.

    Returns:
        JSON response with created category data.
    """
    data = request.get_json()
    try:
        category = _category_service.create_category(data)
        return jsonify({
            "success": True,
            "message": "Category created successfully",
            "data": category.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@categories_bp.route("/<int:category_id>", methods=["PUT"])
@require_admin_or_manager
def update_category(category_id):
    """Update an existing category.

    Args:
        category_id: The unique identifier of the category.

    Returns:
        JSON response with updated category data.
    """
    data = request.get_json()
    try:
        category = _category_service.update_category(category_id, data)
        return jsonify({
            "success": True,
            "message": "Category updated successfully",
            "data": category.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@categories_bp.route("/<int:category_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_category(category_id):
    """Delete a category.

    Args:
        category_id: The unique identifier of the category.

    Returns:
        JSON response with result.
    """
    try:
        _category_service.delete_category(category_id)
        return jsonify({"success": True, "message": "Category deleted successfully"}), 200
    except ValueError as e:
        if str(e) == "Category not found":
            return jsonify({"success": False, "message": str(e)}), 404
        return jsonify({"success": False, "message": str(e)}), 400
