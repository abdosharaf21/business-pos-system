"""Expense routes for expense management API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from backend.modules.expenses.service import ExpenseService
from backend.middleware.rbac import require_authenticated, require_admin_or_manager

expenses_bp = Blueprint("expenses", __name__, url_prefix="/api/expenses")

_expense_service: ExpenseService = None


def init_expense_service(expense_service: ExpenseService) -> None:
    """Initialize the expense service dependency.

    Args:
        expense_service: Instance of ExpenseService for dependency injection.
    """
    global _expense_service
    _expense_service = expense_service


@expenses_bp.route("/", methods=["GET"])
@require_authenticated
def list_expenses():
    """List expenses with filters, sorting, and pagination.

    Query params:
        category_id: Filter by expense category id.
        payment_method: Filter by payment method.
        start_date: Filter by expense date (from, YYYY-MM-DD).
        end_date: Filter by expense date (to, YYYY-MM-DD).
        search: Search in title or notes.
        sort: Sort column (title, category, amount, ...).
        order: Sort direction (asc, desc).
        page: Page number (default 1).
        per_page: Records per page (default 20, max 100).

    Returns:
        JSON response with paginated expense list.
    """
    filters = {
        "category_id": request.args.get("category_id"),
        "payment_method": request.args.get("payment_method"),
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
        "search": request.args.get("search"),
        "sort": request.args.get("sort", "expense_date"),
        "order": request.args.get("order", "desc"),
        "page": request.args.get("page", 1),
        "per_page": request.args.get("per_page", 20),
    }
    try:
        result = _expense_service.list_expenses(filters)
        return jsonify({
            "success": True,
            "message": "Expenses retrieved successfully",
            "data": result,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@expenses_bp.route("/categories", methods=["GET"])
@require_authenticated
def get_expense_categories():
    """Get all expense categories.

    Returns:
        JSON response with the expense categories list.
    """
    categories = _expense_service.get_categories()
    return jsonify({
        "success": True,
        "message": "Expense categories retrieved successfully",
        "data": [category.to_dict() for category in categories],
    }), 200


@expenses_bp.route("/summary", methods=["GET"])
@require_authenticated
def get_expense_summary():
    """Get expense summary metrics.

    Returns:
        JSON response with expense summary data.
    """
    summary = _expense_service.get_summary()
    return jsonify({
        "success": True,
        "message": "Expense summary retrieved successfully",
        "data": summary,
    }), 200


@expenses_bp.route("/monthly", methods=["GET"])
@require_authenticated
def get_monthly_expenses():
    """Get daily expense totals for a month.

    Query params:
        year: Year (defaults to current year).
        month: Month number 1-12 (defaults to current month).

    Returns:
        JSON response with daily expense totals.
    """
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    try:
        data = _expense_service.get_monthly(year=year, month=month)
        return jsonify({
            "success": True,
            "message": "Monthly expenses retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@expenses_bp.route("/yearly", methods=["GET"])
@require_authenticated
def get_yearly_expenses():
    """Get monthly expense totals for a year.

    Query params:
        year: Year (defaults to current year).

    Returns:
        JSON response with monthly expense totals.
    """
    year = request.args.get("year", type=int)
    data = _expense_service.get_yearly(year=year)
    return jsonify({
        "success": True,
        "message": "Yearly expenses retrieved successfully",
        "data": data,
    }), 200


@expenses_bp.route("/by-category", methods=["GET"])
@require_authenticated
def get_expenses_by_category():
    """Get expense totals grouped by category for a date range.

    Query params:
        start_date: Start date in YYYY-MM-DD format (optional).
        end_date: End date in YYYY-MM-DD format (optional).

    Returns:
        JSON response with the category breakdown.
    """
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    try:
        data = _expense_service.get_category_breakdown(start_date, end_date)
        return jsonify({
            "success": True,
            "message": "Expense category breakdown retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@expenses_bp.route("/by-payment", methods=["GET"])
@require_authenticated
def get_expenses_by_payment():
    """Get expense totals grouped by payment method for a date range.

    Query params:
        start_date: Start date in YYYY-MM-DD format (optional).
        end_date: End date in YYYY-MM-DD format (optional).

    Returns:
        JSON response with the payment method breakdown.
    """
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    try:
        data = _expense_service.get_payment_method_breakdown(start_date, end_date)
        return jsonify({
            "success": True,
            "message": "Expense payment method breakdown retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@expenses_bp.route("/<int:expense_id>", methods=["GET"])
@require_authenticated
def get_expense(expense_id):
    """Get an expense by ID.

    Args:
        expense_id: The unique identifier of the expense.

    Returns:
        JSON response with expense data.
    """
    try:
        expense = _expense_service.get_expense(expense_id)
        return jsonify({
            "success": True,
            "message": "Expense retrieved successfully",
            "data": expense.to_dict(),
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@expenses_bp.route("/", methods=["POST"])
@require_admin_or_manager
def create_expense():
    """Create a new expense.

    Body:
        title: Required expense title.
        category_id: Required expense category id.
        amount: Required positive amount.
        payment_method: Payment method (default Cash).
        notes: Optional notes.
        expense_date: Required date in YYYY-MM-DD format.

    Returns:
        JSON response with created expense data.
    """
    data = request.get_json(silent=True)
    try:
        user_id = int(get_jwt_identity())
        expense = _expense_service.create_expense(data, user_id)
        return jsonify({
            "success": True,
            "message": "Expense created successfully",
            "data": expense.to_dict(),
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@expenses_bp.route("/<int:expense_id>", methods=["PUT"])
@require_admin_or_manager
def update_expense(expense_id):
    """Update an existing expense.

    Args:
        expense_id: The unique identifier of the expense.

    Returns:
        JSON response with updated expense data.
    """
    data = request.get_json(silent=True)
    try:
        expense = _expense_service.update_expense(expense_id, data)
        return jsonify({
            "success": True,
            "message": "Expense updated successfully",
            "data": expense.to_dict(),
        }), 200
    except ValueError as e:
        if str(e) == "Expense not found":
            return jsonify({"success": False, "message": str(e)}), 404
        return jsonify({"success": False, "message": str(e)}), 400


@expenses_bp.route("/<int:expense_id>", methods=["DELETE"])
@require_admin_or_manager
def delete_expense(expense_id):
    """Delete an expense.

    Args:
        expense_id: The unique identifier of the expense.

    Returns:
        JSON response with result.
    """
    try:
        _expense_service.delete_expense(expense_id)
        return jsonify({"success": True, "message": "Expense deleted successfully"}), 200
    except ValueError as e:
        if str(e) == "Expense not found":
            return jsonify({"success": False, "message": str(e)}), 404
        return jsonify({"success": False, "message": str(e)}), 400
