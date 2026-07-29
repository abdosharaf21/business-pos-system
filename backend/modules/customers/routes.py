"""Customer routes for customer-related API endpoints."""

from flask import Blueprint, request, jsonify

from backend.modules.customers.service import CustomerService
from backend.middleware.rbac import require_authenticated, require_admin_or_manager

customers_bp = Blueprint("customers", __name__, url_prefix="/api/customers")

_customer_service: CustomerService = None


def init_customer_service(customer_service: CustomerService) -> None:
    """Initialize the customer service dependency.

    Args:
        customer_service: Instance of CustomerService for dependency injection.
    """
    global _customer_service
    _customer_service = customer_service


@customers_bp.route("/", methods=["GET"])
@require_authenticated
def get_all_customers():
    """Get all customers with optional search.

    Query params:
        search: Search term for name or phone.

    Returns:
        JSON response with list of customers.
    """
    search = request.args.get("search", "")
    customers = _customer_service.get_all_customers(search=search or None)
    return jsonify({
        "success": True,
        "message": "Customers retrieved successfully",
        "data": [customer.to_dict() for customer in customers]
    }), 200


@customers_bp.route("/<int:customer_id>", methods=["GET"])
@require_authenticated
def get_customer(customer_id):
    """Get a customer by ID.

    Args:
        customer_id: The unique identifier of the customer.

    Returns:
        JSON response with customer data.
    """
    try:
        customer = _customer_service.get_customer(customer_id)
        return jsonify({
            "success": True,
            "message": "Customer retrieved successfully",
            "data": customer.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@customers_bp.route("/", methods=["POST"])
@require_admin_or_manager
def create_customer():
    """Create a new customer.

    Expects JSON body with customer fields.

    Returns:
        JSON response with created customer data.
    """
    data = request.get_json()
    try:
        customer = _customer_service.create_customer(data)
        return jsonify({
            "success": True,
            "message": "Customer created successfully",
            "data": customer.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@customers_bp.route("/<int:customer_id>", methods=["PUT"])
@require_admin_or_manager
def update_customer(customer_id):
    """Update an existing customer.

    Args:
        customer_id: The unique identifier of the customer.

    Returns:
        JSON response with updated customer data.
    """
    data = request.get_json()
    try:
        customer = _customer_service.update_customer(customer_id, data)
        return jsonify({
            "success": True,
            "message": "Customer updated successfully",
            "data": customer.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_customer(customer_id):
    """Delete a customer.

    Args:
        customer_id: The unique identifier of the customer.

    Returns:
        JSON response with result.
    """
    try:
        _customer_service.delete_customer(customer_id)
        return jsonify({"success": True, "message": "Customer deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
