"""Report service for analytics business logic."""

from datetime import date, timedelta, datetime
from typing import Dict, Any

from backend.modules.reports.repository import ReportRepository


class ReportService:
    """Service for report and analytics operations.

    Orchestrates data from the report repository into structured
    dashboard and analytics payloads. Handles empty database safely.
    """

    def __init__(self, report_repository: ReportRepository) -> None:
        self._report_repository = report_repository

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all dashboard report data.

        Collects sales, purchase, and inventory summaries along
        with top products and recent sales.

        Returns:
            Dictionary with sales, purchases, inventory sections
            plus top products and recent sales arrays.
        """
        sales = self._report_repository.get_sales_summary()
        purchases = self._report_repository.get_purchase_summary()
        inventory = self._report_repository.get_inventory_summary()
        top_products = self._report_repository.get_top_selling_products(5)
        recent_sales = self._report_repository.get_recent_sales(5)

        return {
            "sales": sales,
            "purchases": purchases,
            "inventory": inventory,
            "top_selling_products": top_products,
            "recent_sales": recent_sales,
        }

    def get_sales_trend(self, period: str = "last_30_days",
                        start_date: str = None,
                        end_date: str = None) -> Dict[str, Any]:
        """Get sales trend data for a given period or date range.

        Args:
            period: 'last_7_days', 'last_30_days', or 'custom'.
            start_date: Start date in YYYY-MM-DD (required for custom).
            end_date: End date in YYYY-MM-DD (required for custom).

        Returns:
            Dictionary with period info and daily sales data array.
        """
        today = date.today()

        if period == "last_7_days":
            start = today - timedelta(days=6)
            end = today
        elif period == "last_30_days":
            start = today - timedelta(days=29)
            end = today
        elif period == "custom":
            if not start_date or not end_date:
                raise ValueError("start_date and end_date are required for custom period")
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            raise ValueError(f"Invalid period: {period}")

        start_str = start.isoformat()
        end_str = end.isoformat()

        rows = self._report_repository.get_sales_trend(start_str, end_str)

        filled = self._fill_date_gaps(rows, start, end)

        return {
            "period": period,
            "start_date": start_str,
            "end_date": end_str,
            "data": filled,
        }

    def get_profit(self, period: str = "monthly",
                   start_date: str = None,
                   end_date: str = None) -> Dict[str, Any]:
        """Get profit analytics for a given period or date range.

        Args:
            period: 'daily', 'monthly', or 'custom'.
            start_date: Start date in YYYY-MM-DD (required for custom).
            end_date: End date in YYYY-MM-DD (required for custom).

        Returns:
            Dictionary with period info and profit metrics.
        """
        today = date.today()

        if period == "daily":
            start = today
            end = today
        elif period == "monthly":
            start = today.replace(day=1)
            end = today
        elif period == "custom":
            if not start_date or not end_date:
                raise ValueError("start_date and end_date are required for custom period")
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            raise ValueError(f"Invalid period: {period}")

        start_str = start.isoformat()
        end_str = end.isoformat()

        data = self._report_repository.get_profit_data(start_str, end_str)

        return {
            "period": period,
            "start_date": start_str,
            "end_date": end_str,
            **data,
        }

    def get_products_performance(self) -> Dict[str, Any]:
        """Get product performance data.

        Returns:
            Dictionary with top_products and slow_products arrays.
        """
        return self._report_repository.get_products_performance()

    def get_suppliers_performance(self) -> Dict[str, Any]:
        """Get supplier performance data.

        Returns:
            Dictionary with suppliers array.
        """
        suppliers = self._report_repository.get_suppliers_performance()
        return {"suppliers": suppliers}

    @staticmethod
    def _fill_date_gaps(rows: list, start: date, end: date) -> list:
        """Fill missing dates with zero values in a date series.

        Args:
            rows: List of dicts with 'date' key in ISO format.
            start: Start date.
            end: End date.

        Returns:
            Complete list with all dates in range filled.
        """
        data_map = {}
        for row in rows:
            data_map[row["date"]] = row

        result = []
        current = start
        while current <= end:
            key = current.isoformat()
            if key in data_map:
                result.append(data_map[key])
            else:
                result.append({
                    "date": key,
                    "total_sales": 0.0,
                    "invoice_count": 0,
                })
            current += timedelta(days=1)

        return result
