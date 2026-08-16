"""Report routes for analytics API endpoints (standalone: Worker Management + Expenses only)."""

from flask import Blueprint, jsonify, request

from backend.modules.reports.service import ReportService
from backend.middleware.rbac import require_authenticated

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

_report_service: ReportService = None


def init_report_service(report_service: ReportService) -> None:
    """Initialize the report service dependency.

    Args:
        report_service: Instance of ReportService for dependency injection.
    """
    global _report_service
    _report_service = report_service


@reports_bp.route("/expenses-daily", methods=["GET"])
@require_authenticated
def get_expenses_daily():
    """Get daily expense totals for a date range.

    Query params:
        start_date: Start date in YYYY-MM-DD format (optional).
        end_date: End date in YYYY-MM-DD format (optional).

    Returns:
        JSON response with daily expense data.
    """
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        data = _report_service.get_expenses_daily(start_date, end_date)
        return jsonify({
            "success": True,
            "message": "Daily expenses retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@reports_bp.route("/expenses-category", methods=["GET"])
@require_authenticated
def get_expenses_by_category():
    """Get expense totals grouped by category.

    Query params:
        start_date: Start date in YYYY-MM-DD format (optional).
        end_date: End date in YYYY-MM-DD format (optional).

    Returns:
        JSON response with category breakdown.
    """
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        data = _report_service.get_expenses_by_category(start_date, end_date)
        return jsonify({
            "success": True,
            "message": "Expense category breakdown retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@reports_bp.route("/expenses-payment-method", methods=["GET"])
@require_authenticated
def get_expenses_by_payment_method():
    """Get expense totals grouped by payment method.

    Query params:
        start_date: Start date in YYYY-MM-DD format (optional).
        end_date: End date in YYYY-MM-DD format (optional).

    Returns:
        JSON response with payment method breakdown.
    """
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        data = _report_service.get_expenses_by_payment_method(start_date, end_date)
        return jsonify({
            "success": True,
            "message": "Expense payment method breakdown retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@reports_bp.route("/expenses-monthly-comparison", methods=["GET"])
@require_authenticated
def get_expenses_monthly_comparison():
    """Get monthly expense comparison for a year.

    Query params:
        year: Year (defaults to current year).

    Returns:
        JSON response with monthly comparison data.
    """
    year = request.args.get("year", type=int)

    try:
        data = _report_service.get_expenses_monthly_comparison(year)
        return jsonify({
            "success": True,
            "message": "Monthly expense comparison retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@reports_bp.route("/expenses-yearly-comparison", methods=["GET"])
@require_authenticated
def get_expenses_yearly_comparison():
    """Get yearly expense comparison across a range of years.

    Query params:
        from_year: First year (optional).
        to_year: Last year (optional).

    Returns:
        JSON response with yearly comparison data.
    """
    from_year = request.args.get("from_year", type=int)
    to_year = request.args.get("to_year", type=int)

    try:
        data = _report_service.get_expenses_yearly_comparison(from_year, to_year)
        return jsonify({
            "success": True,
            "message": "Yearly expense comparison retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@reports_bp.route("/expenses-highest-category", methods=["GET"])
@require_authenticated
def get_expenses_highest_categories():
    """Get expense categories with the highest totals.

    Returns:
        JSON response with highest expense categories.
    """
    data = _report_service.get_expenses_highest_categories()
    return jsonify({
        "success": True,
        "message": "Highest expense categories retrieved successfully",
        "data": data,
    }), 200
