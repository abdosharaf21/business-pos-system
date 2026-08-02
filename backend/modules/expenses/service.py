"""Expense service for expense-related business logic."""

from datetime import date, datetime
from typing import Dict, Any, List, Optional, Tuple

from backend.modules.expenses.model import Expense, ExpenseCategory
from backend.modules.expenses.repository import ExpenseRepository
from backend.modules.expenses.validator import ExpenseValidator


class ExpenseService:
    """Service for expense business operations.

    Handles validation, filtering, pagination, and aggregation logic
    for expenses. Communicates only with ExpenseRepository for data
    access and never executes raw SQL.
    """

    MAX_PER_PAGE = 100
    DEFAULT_PER_PAGE = 20

    def __init__(self, expense_repository: ExpenseRepository) -> None:
        """Initialize ExpenseService with an ExpenseRepository.

        Args:
            expense_repository: Repository for expense database operations.
        """
        self._expense_repository = expense_repository

    def create_expense(self, data: dict, user_id: int) -> Expense:
        """Create a new expense.

        Args:
            data: Dictionary containing expense information.
            user_id: ID of the user creating the expense.

        Returns:
            Created Expense instance.

        Raises:
            ValueError: If validation fails.
        """
        validated = ExpenseValidator.validate_create_expense(data)

        self._validate_category_exists(validated["category_id"])

        expense = Expense(
            title=validated["title"],
            category_id=validated["category_id"],
            amount=validated["amount"],
            payment_method=validated["payment_method"],
            notes=validated["notes"],
            expense_date=validated["expense_date"],
            created_by=user_id,
        )

        return self._expense_repository.create(expense)

    def get_expense(self, expense_id: int) -> Expense:
        """Retrieve an expense by its unique identifier.

        Args:
            expense_id: The unique identifier of the expense.

        Returns:
            Expense instance if found.

        Raises:
            ValueError: If expense not found.
        """
        expense = self._expense_repository.get_by_id(expense_id)
        if expense is None:
            raise ValueError("Expense not found")
        return expense

    def list_expenses(self, filters: dict) -> Dict[str, Any]:
        """List expenses with filters, sorting, and pagination.

        Args:
            filters: Dictionary with optional category_id, payment_method,
                start_date, end_date, search, sort, order, page, per_page.

        Returns:
            Dictionary with items, total, page, per_page, and pages.

        Raises:
            ValueError: If a filter value is invalid.
        """
        category_id = self._validate_optional_category_id(filters.get("category_id"))
        payment_method = filters.get("payment_method")
        start_date = self._validate_optional_date(filters.get("start_date"), "start_date")
        end_date = self._validate_optional_date(filters.get("end_date"), "end_date")
        search = filters.get("search")

        sort = filters.get("sort", "expense_date")
        order = filters.get("order", "desc")

        page = self._validate_page(filters.get("page", 1))
        per_page = self._validate_per_page(filters.get("per_page", self.DEFAULT_PER_PAGE))

        offset = (page - 1) * per_page

        items, total = self._expense_repository.list_expenses(
            category_id=category_id,
            payment_method=payment_method,
            start_date=start_date,
            end_date=end_date,
            search=search,
            sort=sort,
            order=order,
            limit=per_page,
            offset=offset,
        )

        pages = (total + per_page - 1) // per_page if total else 0

        return {
            "items": [expense.to_dict() for expense in items],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    def update_expense(self, expense_id: int, data: dict) -> Expense:
        """Update an existing expense.

        Args:
            expense_id: The unique identifier of the expense.
            data: Dictionary containing fields to update.

        Returns:
            Updated Expense instance.

        Raises:
            ValueError: If expense not found or validation fails.
        """
        validated = ExpenseValidator.validate_update_expense(data)

        if "category_id" in validated:
            self._validate_category_exists(validated["category_id"])

        expense = self._expense_repository.get_by_id(expense_id)
        if expense is None:
            raise ValueError("Expense not found")

        if "title" in validated:
            expense.title = validated["title"]
        if "category_id" in validated:
            expense.category_id = validated["category_id"]
        if "amount" in validated:
            expense.amount = validated["amount"]
        if "payment_method" in validated:
            expense.payment_method = validated["payment_method"]
        if "notes" in validated:
            expense.notes = validated["notes"]
        if "expense_date" in validated:
            expense.expense_date = validated["expense_date"]

        updated = self._expense_repository.update(expense)
        if updated is None:
            raise ValueError("Failed to update expense")
        return updated

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense.

        Args:
            expense_id: The unique identifier of the expense.

        Returns:
            True if the expense was deleted successfully.

        Raises:
            ValueError: If expense not found.
        """
        deleted = self._expense_repository.delete(expense_id)
        if not deleted:
            raise ValueError("Expense not found")
        return True

    def get_categories(self) -> List[ExpenseCategory]:
        """Retrieve all expense categories.

        Returns:
            List of ExpenseCategory instances ordered by name.
        """
        return self._expense_repository.get_categories()

    def get_summary(self) -> Dict[str, Any]:
        """Get expense summary metrics.

        Returns:
            Dictionary with totals, today, month, year, average,
            and highest category figures.
        """
        return self._expense_repository.get_summary()

    def get_monthly(self, year: int = None, month: int = None) -> Dict[str, Any]:
        """Get daily expense totals for a given month.

        Args:
            year: Year (defaults to current year).
            month: Month number 1-12 (defaults to current month).

        Returns:
            Dictionary with period, year, month, and data array.

        Raises:
            ValueError: If the month is invalid.
        """
        now = datetime.now()
        year = int(year) if year else now.year
        month = int(month) if month else now.month

        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")

        data = self._expense_repository.get_daily_totals(year, month)
        return {"period": "monthly", "year": year, "month": month, "data": data}

    def get_yearly(self, year: int = None) -> Dict[str, Any]:
        """Get monthly expense totals for a given year.

        Args:
            year: Year (defaults to current year).

        Returns:
            Dictionary with period, year, and data array.
        """
        now = datetime.now()
        year = int(year) if year else now.year

        data = self._expense_repository.get_monthly_totals(year)
        return {"period": "yearly", "year": year, "data": data}

    # ------------------------------------------------------------------
    # Report helpers
    # ------------------------------------------------------------------

    def _resolve_date_range(
        self, start_date: Optional[str], end_date: Optional[str]
    ) -> Tuple[str, str]:
        """Resolve and validate a date range for reports.

        Args:
            start_date: Optional start date in YYYY-MM-DD format.
            end_date: Optional end date in YYYY-MM-DD format.

        Returns:
            Tuple of (start_date, end_date) strings.

        Raises:
            ValueError: If dates are invalid or inconsistent.
        """
        start = self._validate_optional_date(start_date, "start_date") or "1970-01-01"
        end = self._validate_optional_date(end_date, "end_date") or date.today().isoformat()

        if start > end:
            raise ValueError("start_date cannot be after end_date")

        return start, end

    def get_daily_expenses(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get daily expense totals for a date range.

        Args:
            start_date: Optional start date in YYYY-MM-DD format.
            end_date: Optional end date in YYYY-MM-DD format.

        Returns:
            Dictionary with start_date, end_date, total, and data array.
        """
        start, end = self._resolve_date_range(start_date, end_date)

        rows = self._expense_repository.get_daily_series(start, end)
        total = sum(row["total"] for row in rows)

        return {
            "start_date": start,
            "end_date": end,
            "total_expenses": total,
            "data": rows,
        }

    def get_category_breakdown(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get expense totals grouped by category for a date range.

        Args:
            start_date: Optional start date in YYYY-MM-DD format.
            end_date: Optional end date in YYYY-MM-DD format.

        Returns:
            Dictionary with start_date, end_date, total, and data array.
        """
        start, end = self._resolve_date_range(start_date, end_date)

        rows = self._expense_repository.get_category_breakdown(start, end)
        total = sum(row["total"] for row in rows)

        return {
            "start_date": start,
            "end_date": end,
            "total_expenses": total,
            "data": rows,
        }

    def get_payment_method_breakdown(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get expense totals grouped by payment method for a date range.

        Args:
            start_date: Optional start date in YYYY-MM-DD format.
            end_date: Optional end date in YYYY-MM-DD format.

        Returns:
            Dictionary with start_date, end_date, total, and data array.
        """
        start, end = self._resolve_date_range(start_date, end_date)

        rows = self._expense_repository.get_payment_method_breakdown(start, end)
        total = sum(row["total"] for row in rows)

        return {
            "start_date": start,
            "end_date": end,
            "total_expenses": total,
            "data": rows,
        }

    def get_monthly_comparison(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Get monthly expense comparison for a year.

        Args:
            year: Year (defaults to current year).

        Returns:
            Dictionary with period, year, total, and data array.
        """
        now = datetime.now()
        year = int(year) if year else now.year

        rows = self._expense_repository.get_monthly_comparison(year)
        total = sum(row["total"] for row in rows)

        return {"period": "monthly", "year": year, "total_expenses": total, "data": rows}

    def get_yearly_comparison(
        self, from_year: Optional[int] = None, to_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get yearly expense comparison across a range of years.

        Args:
            from_year: First year (defaults to current year - 4).
            to_year: Last year (defaults to current year).

        Returns:
            Dictionary with from_year, to_year, total, and data array.

        Raises:
            ValueError: If the year range is invalid.
        """
        now = datetime.now()
        to = int(to_year) if to_year else now.year
        frm = int(from_year) if from_year else to - 4

        if frm > to:
            raise ValueError("from_year cannot be after to_year")

        rows = self._expense_repository.get_yearly_comparison(frm, to)
        total = sum(row["total"] for row in rows)

        return {
            "from_year": frm,
            "to_year": to,
            "total_expenses": total,
            "data": rows,
        }

    def get_highest_categories(self, limit: int = 10) -> Dict[str, Any]:
        """Get expense categories with the highest totals.

        Args:
            limit: Maximum number of categories.

        Returns:
            Dictionary with a highest_categories array.
        """
        rows = self._expense_repository.get_highest_categories(limit)
        return {"highest_categories": rows}

    # ------------------------------------------------------------------
    # Private validation helpers
    # ------------------------------------------------------------------

    def _validate_category_exists(self, category_id: int) -> None:
        """Ensure the expense category exists in the database.

        Args:
            category_id: The expense category id to check.

        Raises:
            ValueError: If the category does not exist.
        """
        if not self._expense_repository.category_exists(category_id):
            raise ValueError("Expense category does not exist")

    @staticmethod
    def _validate_optional_category_id(value) -> Optional[int]:
        """Validate an optional expense category id filter.

        Args:
            value: Expense category id, or None.

        Returns:
            Validated positive integer or None.

        Raises:
            ValueError: If the value is not a valid id.
        """
        if not value:
            return None
        return ExpenseValidator.validate_category_id(value)

    @staticmethod
    def _validate_optional_date(value: Optional[str], name: str) -> Optional[str]:
        """Validate an optional date string.

        Args:
            value: Date string in YYYY-MM-DD format, or None.
            name: Field name used in error messages.

        Returns:
            Normalized date string or None.

        Raises:
            ValueError: If the date is invalid.
        """
        if not value:
            return None

        value = str(value).strip()

        try:
            parsed = datetime.strptime(value, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            raise ValueError(f"{name} must be a valid date in YYYY-MM-DD format")

        return parsed.isoformat()

    @staticmethod
    def _validate_page(page) -> int:
        """Validate a page number.

        Args:
            page: Page number.

        Returns:
            Validated page number (minimum 1).

        Raises:
            ValueError: If page is invalid.
        """
        try:
            value = int(page)
        except (TypeError, ValueError):
            raise ValueError("page must be a valid number")

        if value < 1:
            raise ValueError("page must be at least 1")

        return value

    @staticmethod
    def _validate_per_page(per_page) -> int:
        """Validate the page size.

        Args:
            per_page: Number of records per page.

        Returns:
            Validated page size within allowed bounds.

        Raises:
            ValueError: If per_page is invalid.
        """
        try:
            value = int(per_page)
        except (TypeError, ValueError):
            raise ValueError("per_page must be a valid number")

        if value < 1:
            raise ValueError("per_page must be at least 1")

        return min(value, ExpenseService.MAX_PER_PAGE)
