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
