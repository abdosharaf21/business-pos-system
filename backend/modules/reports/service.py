"""Report service for analytics business logic."""

from datetime import date, timedelta, datetime
from typing import Dict, Any, Optional

from backend.modules.reports.repository import ReportRepository
from backend.modules.expenses.repository import ExpenseRepository
from backend.modules.inventory_audits.repository import InventoryAuditRepository
from backend.config import Config
from backend.utils.expiration import classify_expiration


class ReportService:
    """Service for report and analytics operations.

    Orchestrates data from the report repository into structured
    dashboard and analytics payloads. Handles empty database safely.
    """

    def __init__(
        self,
        report_repository: ReportRepository,
        expense_repository: Optional[ExpenseRepository] = None,
        audit_repository: Optional[InventoryAuditRepository] = None,
    ) -> None:
        """Initialize ReportService with repositories.

        Args:
            report_repository: Repository for core report analytics.
            expense_repository: Optional repository for expense reports.
            audit_repository: Optional repository for inventory audit reports.
        """
        self._report_repository = report_repository
        self._expense_repository = expense_repository
        self._audit_repository = audit_repository

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

    def get_inventory_report(self) -> Dict[str, Any]:
        """Get per-product stock levels by location with expiration status.

        Returns:
            Dictionary with an inventory array.
        """
        inventory = self._report_repository.get_inventory_report()

        for row in inventory:
            expiration_date = row.get("expiration_date")
            row["expiration_status"] = (
                classify_expiration(
                    expiration_date, expiring_soon_days=Config.EXPIRING_SOON_DAYS
                )
                if expiration_date is not None
                else None
            )

        return {"inventory": inventory}

    def get_movement_report(
        self,
        period: str = "monthly",
        year: Optional[int] = None,
        month: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get stock movement summary for a period.

        Args:
            period: 'monthly' or 'yearly'.
            year: Year number (defaults to current year).
            month: Month number 1-12 (required for monthly period).

        Returns:
            Dictionary with period, year, month, and data array.

        Raises:
            ValueError: If the period is invalid or inputs are missing.
        """
        now = datetime.now()
        year = int(year) if year else now.year

        if period == "monthly":
            if not month:
                month = now.month
            month = int(month)
            if month < 1 or month > 12:
                raise ValueError("Month must be between 1 and 12")
            data = self._report_repository.get_movement_monthly(year, month)
            return {"period": period, "year": year, "month": month, "data": data}

        if period == "yearly":
            data = self._report_repository.get_movement_yearly(year)
            return {"period": period, "year": year, "data": data}

        raise ValueError("Invalid period. Must be 'monthly' or 'yearly'")

    def get_most_transferred(self, limit: int = 10) -> Dict[str, Any]:
        """Get products with the highest transfer volume.

        Args:
            limit: Maximum number of products.

        Returns:
            Dictionary with a most_transferred array.
        """
        data = self._report_repository.get_most_transferred(limit)
        return {"most_transferred": data}

    def get_lowest_stock(self, limit: int = 10) -> Dict[str, Any]:
        """Get products with the lowest total stock.

        Args:
            limit: Maximum number of products.

        Returns:
            Dictionary with a lowest_stock array.
        """
        data = self._report_repository.get_lowest_stock(limit)
        return {"lowest_stock": data}

    # ------------------------------------------------------------------
    # Expense reports
    # ------------------------------------------------------------------

    def _require_expense_repository(self) -> ExpenseRepository:
        """Ensure the expense repository is available.

        Returns:
            The expense repository instance.

        Raises:
            ValueError: If the expense repository was not provided.
        """
        if self._expense_repository is None:
            raise ValueError("Expense reporting is not available")
        return self._expense_repository

    def _resolve_expense_range(
        self, start_date: Optional[str], end_date: Optional[str]
    ) -> Dict[str, str]:
        """Resolve and validate a date range for expense reports.

        Args:
            start_date: Optional start date in YYYY-MM-DD format.
            end_date: Optional end date in YYYY-MM-DD format.

        Returns:
            Dictionary with start_date and end_date strings.

        Raises:
            ValueError: If dates are invalid or inconsistent.
        """
        today = date.today()

        if start_date and end_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            if start > end:
                raise ValueError("start_date cannot be after end_date")
        elif start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = today
        elif end_date:
            start = date(1970, 1, 1)
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            start = today - timedelta(days=29)
            end = today

        return {"start_date": start.isoformat(), "end_date": end.isoformat()}

    def get_expenses_daily(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get daily expense totals for a date range.

        Args:
            start_date: Optional start date in YYYY-MM-DD format.
            end_date: Optional end date in YYYY-MM-DD format.

        Returns:
            Dictionary with date range and daily expense data.
        """
        repo = self._require_expense_repository()
        dates = self._resolve_expense_range(start_date, end_date)
        rows = repo.get_daily_series(dates["start_date"], dates["end_date"])
        return {
            "period": "daily",
            **dates,
            "total_expenses": sum(row["total"] for row in rows),
            "data": rows,
        }

    def get_expenses_by_category(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get expense totals grouped by category.

        Args:
            start_date: Optional start date in YYYY-MM-DD format.
            end_date: Optional end date in YYYY-MM-DD format.

        Returns:
            Dictionary with date range and category breakdown.
        """
        repo = self._require_expense_repository()
        dates = self._resolve_expense_range(start_date, end_date)
        rows = repo.get_category_breakdown(dates["start_date"], dates["end_date"])
        return {
            "period": "category",
            **dates,
            "total_expenses": sum(row["total"] for row in rows),
            "data": rows,
        }

    def get_expenses_by_payment_method(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get expense totals grouped by payment method.

        Args:
            start_date: Optional start date in YYYY-MM-DD format.
            end_date: Optional end date in YYYY-MM-DD format.

        Returns:
            Dictionary with date range and payment method breakdown.
        """
        repo = self._require_expense_repository()
        dates = self._resolve_expense_range(start_date, end_date)
        rows = repo.get_payment_method_breakdown(
            dates["start_date"], dates["end_date"]
        )
        return {
            "period": "payment_method",
            **dates,
            "total_expenses": sum(row["total"] for row in rows),
            "data": rows,
        }

    def get_expenses_monthly_comparison(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Get monthly expense comparison for a year.

        Args:
            year: Year (defaults to current year).

        Returns:
            Dictionary with year and monthly comparison data.
        """
        repo = self._require_expense_repository()
        year = int(year) if year else datetime.now().year
        rows = repo.get_monthly_comparison(year)
        return {
            "period": "monthly",
            "year": year,
            "total_expenses": sum(row["total"] for row in rows),
            "data": rows,
        }

    def get_expenses_yearly_comparison(
        self,
        from_year: Optional[int] = None,
        to_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get yearly expense comparison across a range of years.

        Args:
            from_year: First year (defaults to current year - 4).
            to_year: Last year (defaults to current year).

        Returns:
            Dictionary with year range and yearly comparison data.

        Raises:
            ValueError: If the year range is invalid.
        """
        repo = self._require_expense_repository()
        now = datetime.now()
        to = int(to_year) if to_year else now.year
        frm = int(from_year) if from_year else to - 4

        if frm > to:
            raise ValueError("from_year cannot be after to_year")

        rows = repo.get_yearly_comparison(frm, to)
        return {
            "period": "yearly",
            "from_year": frm,
            "to_year": to,
            "total_expenses": sum(row["total"] for row in rows),
            "data": rows,
        }

    def get_expenses_highest_categories(self, limit: int = 10) -> Dict[str, Any]:
        """Get expense categories with the highest totals.

        Args:
            limit: Maximum number of categories.

        Returns:
            Dictionary with a highest_categories array.
        """
        repo = self._require_expense_repository()
        rows = repo.get_highest_categories(limit)
        return {"highest_categories": rows}

    # ------------------------------------------------------------------
    # Inventory audit reports
    # ------------------------------------------------------------------

    def _require_audit_repository(self) -> InventoryAuditRepository:
        """Ensure the inventory audit repository is available.

        Returns:
            The inventory audit repository instance.

        Raises:
            ValueError: If the audit repository was not provided.
        """
        if self._audit_repository is None:
            raise ValueError("Inventory audit reporting is not available")
        return self._audit_repository

    def get_inventory_audit_report(self) -> Dict[str, Any]:
        """Get the inventory audit report summary.

        Returns:
            Dictionary with audit metrics, largest shortages, and overages.
        """
        repo = self._require_audit_repository()
        return {
            "metrics": repo.get_report_metrics(),
            "largest_shortages": repo.get_largest_shortages(10),
            "largest_overages": repo.get_largest_overages(10),
        }

    def get_audits_monthly_summary(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Get completed audit counts per month for a year.

        Args:
            year: Year (defaults to current year).

        Returns:
            Dictionary with year and monthly audit data.
        """
        repo = self._require_audit_repository()
        year = int(year) if year else datetime.now().year
        rows = repo.get_monthly_summary(year)
        return {
            "period": "monthly",
            "year": year,
            "total_audits": sum(row["audits"] for row in rows),
            "data": rows,
        }

    def get_audits_yearly_summary(
        self,
        from_year: Optional[int] = None,
        to_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get completed audit counts per year across a range.

        Args:
            from_year: First year (defaults to current year - 4).
            to_year: Last year (defaults to current year).

        Returns:
            Dictionary with year range and yearly audit data.

        Raises:
            ValueError: If the year range is invalid.
        """
        repo = self._require_audit_repository()
        now = datetime.now()
        to = int(to_year) if to_year else now.year
        frm = int(from_year) if from_year else to - 4

        if frm > to:
            raise ValueError("from_year cannot be after to_year")

        rows = repo.get_yearly_summary(frm, to)
        return {
            "period": "yearly",
            "from_year": frm,
            "to_year": to,
            "total_audits": sum(row["audits"] for row in rows),
            "data": rows,
        }

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
