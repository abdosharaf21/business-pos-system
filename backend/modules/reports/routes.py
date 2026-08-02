"""Report routes for analytics API endpoints."""

from flask import Blueprint, jsonify, request

from backend.modules.reports.service import ReportService
from backend.middleware.rbac import require_authenticated

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

_report_service: ReportService = None


def init_report_service(report_service: ReportService) -> None:
    global _report_service
    _report_service = report_service


@reports_bp.route("/dashboard", methods=["GET"])
@require_authenticated
def get_dashboard():
    """Get dashboard report data.

    Returns:
        JSON response with sales, purchase, inventory summaries,
        top selling products, and recent sales.
    """
    data = _report_service.get_dashboard_data()
    return jsonify({
        "success": True,
        "message": "Dashboard report data retrieved successfully",
        "data": data,
    }), 200


@reports_bp.route("/sales-trend", methods=["GET"])
@require_authenticated
def get_sales_trend():
    """Get daily sales trend data.

    Query params:
        period: last_7_days, last_30_days, custom (default: last_30_days)
        start_date: YYYY-MM-DD (required for custom period)
        end_date: YYYY-MM-DD (required for custom period)

    Returns:
        JSON response with daily sales data array.
    """
    period = request.args.get("period", "last_30_days")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        data = _report_service.get_sales_trend(period, start_date, end_date)
        return jsonify({
            "success": True,
            "message": "Sales trend data retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@reports_bp.route("/profit", methods=["GET"])
@require_authenticated
def get_profit():
    """Get profit analytics.

    Query params:
        period: daily, monthly, custom (default: monthly)
        start_date: YYYY-MM-DD (required for custom period)
        end_date: YYYY-MM-DD (required for custom period)

    Returns:
        JSON response with revenue, cost, profit, and margin.
    """
    period = request.args.get("period", "monthly")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        data = _report_service.get_profit(period, start_date, end_date)
        return jsonify({
            "success": True,
            "message": "Profit data retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@reports_bp.route("/products-performance", methods=["GET"])
@require_authenticated
def get_products_performance():
    """Get product performance data.

    Returns:
        JSON response with top and slow performing products.
    """
    data = _report_service.get_products_performance()
    return jsonify({
        "success": True,
        "message": "Product performance data retrieved successfully",
        "data": data,
    }), 200


@reports_bp.route("/suppliers-performance", methods=["GET"])
@require_authenticated
def get_suppliers_performance():
    """Get supplier performance data.

    Returns:
        JSON response with supplier spending summary.
    """
    data = _report_service.get_suppliers_performance()
    return jsonify({
        "success": True,
        "message": "Supplier performance data retrieved successfully",
        "data": data,
    }), 200


@reports_bp.route("/inventory-report", methods=["GET"])
@require_authenticated
def get_inventory_report():
    """Get per-product stock levels by location.

    Returns:
        JSON response with warehouse/store/total inventory report.
    """
    data = _report_service.get_inventory_report()
    return jsonify({
        "success": True,
        "message": "Inventory report retrieved successfully",
        "data": data,
    }), 200


@reports_bp.route("/movement", methods=["GET"])
@require_authenticated
def get_movement_report():
    """Get stock movement summary for a period.

    Query params:
        period: monthly or yearly (default: monthly)
        year: Year number (defaults to current year)
        month: Month number 1-12 (used for monthly period)

    Returns:
        JSON response with movement summary data.
    """
    period = request.args.get("period", "monthly")
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    try:
        data = _report_service.get_movement_report(
            period=period, year=year, month=month
        )
        return jsonify({
            "success": True,
            "message": "Movement report retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@reports_bp.route("/most-transferred", methods=["GET"])
@require_authenticated
def get_most_transferred():
    """Get products with the highest transfer volume.

    Returns:
        JSON response with most transferred products.
    """
    data = _report_service.get_most_transferred()
    return jsonify({
        "success": True,
        "message": "Most transferred products retrieved successfully",
        "data": data,
    }), 200


@reports_bp.route("/lowest-stock", methods=["GET"])
@require_authenticated
def get_lowest_stock():
    """Get products with the lowest total stock.

    Returns:
        JSON response with lowest stock products.
    """
    data = _report_service.get_lowest_stock()
    return jsonify({
        "success": True,
        "message": "Lowest stock products retrieved successfully",
        "data": data,
    }), 200


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


@reports_bp.route("/inventory-audits", methods=["GET"])
@require_authenticated
def get_inventory_audit_report():
    """Get the inventory audit report summary.

    Returns:
        JSON response with audit metrics, shortages, and overages.
    """
    try:
        data = _report_service.get_inventory_audit_report()
        return jsonify({
            "success": True,
            "message": "Inventory audit report retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@reports_bp.route("/inventory-audits-monthly", methods=["GET"])
@require_authenticated
def get_audits_monthly_summary():
    """Get completed audit counts per month for a year.

    Query params:
        year: Year (defaults to current year).

    Returns:
        JSON response with monthly audit data.
    """
    year = request.args.get("year", type=int)
    try:
        data = _report_service.get_audits_monthly_summary(year)
        return jsonify({
            "success": True,
            "message": "Monthly inventory audit summary retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@reports_bp.route("/inventory-audits-yearly", methods=["GET"])
@require_authenticated
def get_audits_yearly_summary():
    """Get completed audit counts per year across a range.

    Query params:
        from_year: First year (optional).
        to_year: Last year (optional).

    Returns:
        JSON response with yearly audit data.
    """
    from_year = request.args.get("from_year", type=int)
    to_year = request.args.get("to_year", type=int)
    try:
        data = _report_service.get_audits_yearly_summary(from_year, to_year)
        return jsonify({
            "success": True,
            "message": "Yearly inventory audit summary retrieved successfully",
            "data": data,
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
