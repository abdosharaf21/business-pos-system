"""Report service for analytics business logic (standalone: Expenses only).

Delegates expense reporting to ExpenseRepository. Removes all legacy
POS/sales/purchase/inventory analytics methods.
"""

from datetime import date, timedelta, datetime
from typing import Dict, Any, Optional

from backend.modules.expenses.repository import ExpenseRepository


class ReportService:
    """Service for report and analytics operations.

    Orchestrates expense data from the ExpenseRepository into structured
    report payloads. Handles empty database safely.
    """

    def __init__(
        self,
        expense_repository: Optional[ExpenseRepository] = None,
    ) -> None:
        """Initialize ReportService with repositories.

        Args:
            expense_repository: Repository for expense reports.
        """
        self._expense_repository = expense_repository

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
