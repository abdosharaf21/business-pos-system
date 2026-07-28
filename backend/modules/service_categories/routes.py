"""Service category routes for category-related API endpoints."""

from flask import Blueprint, request, jsonify

from backend.modules.service_categories.service import ServiceCategoryService
from backend.middleware.rbac import require_authenticated, require_admin_or_manager

service_categories_bp = Blueprint("service_categories", __name__, url_prefix="/api/service-categories")

_category_service: ServiceCategoryService = None


def init_category_service(category_service: ServiceCategoryService) -> None:
    """Initialize the category service dependency.

    Args:
        category_service: Instance of ServiceCategoryService for dependency injection.
    """
    global _category_service
    _category_service = category_service


@service_categories_bp.route("/", methods=["GET"])
@require_authenticated
def get_all_categories():
    """Get all service categories.

    Returns:
        JSON response with list of categories.
    """
    categories = _category_service.get_all_categories()
    return jsonify({
        "success": True,
        "message": "Categories retrieved successfully",
        "data": [category.to_dict() for category in categories]
    }), 200


@service_categories_bp.route("/<int:category_id>", methods=["GET"])
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


@service_categories_bp.route("/", methods=["POST"])
@require_admin_or_manager
def create_category():
    """Create a new service category.

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


@service_categories_bp.route("/<int:category_id>", methods=["PUT"])
@require_admin_or_manager
def update_category(category_id):
    """Update an existing service category.

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


@service_categories_bp.route("/<int:category_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_category(category_id):
    """Delete a service category.

    Args:
        category_id: The unique identifier of the category.

    Returns:
        JSON response with result.
    """
    try:
        _category_service.delete_category(category_id)
        return jsonify({"success": True, "message": "Category deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
