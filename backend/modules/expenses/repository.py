"""Expense repository for database operations on the expenses table."""

from typing import Optional, List, Dict, Any, Tuple

import mysql.connector

from backend.database import Database
from backend.modules.expenses.model import Expense, ExpenseCategory


class ExpenseRepository:
    """Repository for expense database operations.

    Handles CRUD operations, filtered listing, pagination, category
    lookup, and read-only aggregation queries using a shared connection
    pool.
    """

    SORTABLE_COLUMNS = {
        "title": "e.title",
        "category": "ec.name",
        "amount": "e.amount",
        "payment_method": "e.payment_method",
        "expense_date": "e.expense_date",
        "created_at": "e.created_at",
    }

    def __init__(self, database: Database) -> None:
        """Initialize ExpenseRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def _row_to_expense(self, row: tuple) -> Expense:
        """Convert a database row tuple to an Expense instance.

        Args:
            row: Database row as a tuple.

        Returns:
            Expense instance populated from the row data.
        """
        expense = Expense(
            id=row[0],
            title=row[1],
            category_id=row[2],
            amount=row[3],
            payment_method=row[4],
            notes=row[5],
            expense_date=row[6],
            created_by=row[7],
            created_at=row[8],
            updated_at=row[9],
        )
        if len(row) > 10:
            expense.created_by_name = row[10]
        if len(row) > 11:
            expense.category_name = row[11]
        return expense

    def category_exists(self, category_id: int) -> bool:
        """Check whether an expense category exists.

        Args:
            category_id: The expense category id.

        Returns:
            True if the category exists, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT 1 FROM expense_categories WHERE id = %s",
                    (category_id,),
                )
                return cursor.fetchone() is not None
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_categories(self) -> List[ExpenseCategory]:
        """Retrieve all expense categories.

        Returns:
            List of ExpenseCategory instances ordered by name.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT id, name, description, created_at "
                    "FROM expense_categories ORDER BY name"
                )
                rows = cursor.fetchall()
                return [
                    ExpenseCategory(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        created_at=row[3],
                    )
                    for row in rows
                ]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def create(self, expense: Expense) -> Expense:
        """Insert a new expense record into the database.

        Args:
            expense: Expense instance to insert.

        Returns:
            Expense instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    INSERT INTO expenses
                        (title, category_id, amount, payment_method, notes,
                         expense_date, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    expense.title,
                    expense.category_id,
                    expense.amount,
                    expense.payment_method,
                    expense.notes,
                    expense.expense_date,
                    expense.created_by,
                ))
                conn.commit()
                expense.id = cursor.lastrowid
                return self.get_by_id(expense.id)
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def get_by_id(self, expense_id: int) -> Optional[Expense]:
        """Retrieve an expense by its unique identifier.

        Args:
            expense_id: The unique identifier of the expense.

        Returns:
            Expense instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = (
                    "SELECT e.*, u.full_name AS created_by_name, "
                    "ec.name AS category_name "
                    "FROM expenses e "
                    "LEFT JOIN users u ON u.id = e.created_by "
                    "LEFT JOIN expense_categories ec ON ec.id = e.category_id "
                    "WHERE e.id = %s"
                )
                cursor.execute(query, (expense_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_expense(row)
                return None
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def list_expenses(
        self,
        category_id: Optional[int] = None,
        payment_method: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
        sort: str = "expense_date",
        order: str = "desc",
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Expense], int]:
        """Retrieve expenses with filters, sorting, and pagination.

        Args:
            category_id: Optional expense category id filter.
            payment_method: Optional payment method filter.
            start_date: Optional start date in YYYY-MM-DD format.
            end_date: Optional end date in YYYY-MM-DD format.
            search: Optional search term for title or notes.
            sort: Column to sort by (title, category, amount, ...).
            order: Sort direction ('asc' or 'desc').
            limit: Maximum number of records.
            offset: Pagination offset.

        Returns:
            Tuple of (list of Expense instances, total count).

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        where = []
        params: List[Any] = []

        if category_id:
            where.append("e.category_id = %s")
            params.append(category_id)

        if payment_method:
            where.append("e.payment_method = %s")
            params.append(payment_method)

        if start_date:
            where.append("e.expense_date >= %s")
            params.append(start_date)

        if end_date:
            where.append("e.expense_date <= %s")
            params.append(end_date)

        if search:
            where.append("(e.title LIKE %s OR e.notes LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])

        where_clause = ("WHERE " + " AND ".join(where)) if where else ""

        sort_column = self.SORTABLE_COLUMNS.get(sort, "e.expense_date")
        sort_order = "ASC" if str(order).lower() == "asc" else "DESC"

        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                count_query = (
                    f"SELECT COUNT(*) FROM expenses e {where_clause}"
                )
                cursor.execute(count_query, tuple(params))
                total = cursor.fetchone()[0]

                query = (
                    "SELECT e.*, u.full_name AS created_by_name, "
                    "ec.name AS category_name "
                    "FROM expenses e "
                    "LEFT JOIN users u ON u.id = e.created_by "
                    "LEFT JOIN expense_categories ec ON ec.id = e.category_id "
                    f"{where_clause} "
                    f"ORDER BY {sort_column} {sort_order}, e.id DESC "
                    "LIMIT %s OFFSET %s"
                )
                cursor.execute(query, tuple(params + [limit, offset]))
                rows = cursor.fetchall()

                expenses = [self._row_to_expense(row) for row in rows]
                return expenses, total

            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def update(self, expense: Expense) -> Optional[Expense]:
        """Update an existing expense record in the database.

        Args:
            expense: Expense instance with updated fields.

        Returns:
            Updated Expense instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    UPDATE expenses
                    SET title = %s, category_id = %s, amount = %s,
                        payment_method = %s, notes = %s, expense_date = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    expense.title,
                    expense.category_id,
                    expense.amount,
                    expense.payment_method,
                    expense.notes,
                    expense.expense_date,
                    expense.id,
                ))
                conn.commit()
                if cursor.rowcount > 0:
                    return self.get_by_id(expense.id)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def delete(self, expense_id: int) -> bool:
        """Delete an expense record from the database.

        Args:
            expense_id: The unique identifier of the expense to delete.

        Returns:
            True if the expense was deleted, False if not found.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "DELETE FROM expenses WHERE id = %s"
                cursor.execute(query, (expense_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def get_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calculate expense summary metrics.

        Args:
            start_date: Optional start date in YYYY-MM-DD format.
            end_date: Optional end date in YYYY-MM-DD format.

        Returns:
            Dictionary with totals, today, month, year, average,
            and highest category figures.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            where = []
            params: List[Any] = []
            if start_date:
                where.append("expense_date >= %s")
                params.append(start_date)
            if end_date:
                where.append("expense_date <= %s")
                params.append(end_date)
            where_clause = ("WHERE " + " AND ".join(where)) if where else ""

            cursor.execute(
                f"SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total "
                f"FROM expenses {where_clause}",
                tuple(params),
            )
            filtered = cursor.fetchone()

            cursor.execute(
                "SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total "
                "FROM expenses WHERE expense_date = CURDATE()"
            )
            today = cursor.fetchone()

            cursor.execute(
                "SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total "
                "FROM expenses WHERE DATE_FORMAT(expense_date, '%Y-%m') = "
                "DATE_FORMAT(CURDATE(), '%Y-%m')"
            )
            this_month = cursor.fetchone()

            cursor.execute(
                "SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total "
                "FROM expenses WHERE YEAR(expense_date) = YEAR(CURDATE())"
            )
            this_year = cursor.fetchone()

            cursor.execute(
                "SELECT COALESCE(AVG(monthly.total), 0) AS avg_monthly "
                "FROM ("
                "  SELECT SUM(amount) AS total "
                "  FROM expenses "
                "  WHERE expense_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) "
                "  GROUP BY DATE_FORMAT(expense_date, '%Y-%m')"
                ") monthly"
            )
            avg_monthly = float(cursor.fetchone()["avg_monthly"])

            cursor.execute(
                "SELECT ec.name AS category, ec.id AS category_id, "
                "COALESCE(SUM(e.amount), 0) AS total "
                "FROM expenses e "
                "JOIN expense_categories ec ON ec.id = e.category_id "
                "WHERE e.expense_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) "
                "GROUP BY ec.id, ec.name "
                "ORDER BY total DESC LIMIT 1"
            )
            highest = cursor.fetchone()

            cursor.close()

        return {
            "total_count": filtered["count"],
            "total_expenses": float(filtered["total"]),
            "today_count": today["count"],
            "today_total": float(today["total"]),
            "this_month_count": this_month["count"],
            "this_month_total": float(this_month["total"]),
            "this_year_count": this_year["count"],
            "this_year_total": float(this_year["total"]),
            "avg_monthly_total": avg_monthly,
            "highest_category": highest["category"] if highest else None,
            "highest_category_id": highest["category_id"] if highest else None,
            "highest_category_total": float(highest["total"]) if highest else 0.0,
        }

    def get_daily_totals(self, year: int, month: int) -> List[Dict[str, Any]]:
        """Get daily expense totals for a given month.

        Args:
            year: Year (e.g. 2026).
            month: Month number 1-12.

        Returns:
            List of dicts with day, total, and count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT DAY(expense_date) AS day, "
                    "COALESCE(SUM(amount), 0) AS total, "
                    "COUNT(*) AS count "
                    "FROM expenses "
                    "WHERE YEAR(expense_date) = %s AND MONTH(expense_date) = %s "
                    "GROUP BY DAY(expense_date) "
                    "ORDER BY day",
                    (year, month),
                )
                rows = cursor.fetchall()
                return [
                    {
                        "day": int(row["day"]),
                        "total": float(row["total"]),
                        "count": int(row["count"]),
                    }
                    for row in rows
                ]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_monthly_totals(self, year: int) -> List[Dict[str, Any]]:
        """Get monthly expense totals for a given year.

        Args:
            year: Year (e.g. 2026).

        Returns:
            List of dicts with month (1-12), total, and count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT MONTH(expense_date) AS month, "
                    "COALESCE(SUM(amount), 0) AS total, "
                    "COUNT(*) AS count "
                    "FROM expenses "
                    "WHERE YEAR(expense_date) = %s "
                    "GROUP BY MONTH(expense_date) "
                    "ORDER BY month",
                    (year,),
                )
                rows = cursor.fetchall()
                return [
                    {
                        "month": int(row["month"]),
                        "total": float(row["total"]),
                        "count": int(row["count"]),
                    }
                    for row in rows
                ]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_daily_series(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get daily expense totals for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.

        Returns:
            List of dicts with date, total, and count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT expense_date AS date, "
                    "COALESCE(SUM(amount), 0) AS total, "
                    "COUNT(*) AS count "
                    "FROM expenses "
                    "WHERE expense_date BETWEEN %s AND %s "
                    "GROUP BY expense_date "
                    "ORDER BY date",
                    (start_date, end_date),
                )
                rows = cursor.fetchall()
                return [
                    {
                        "date": row["date"].isoformat() if row["date"] else None,
                        "total": float(row["total"]),
                        "count": int(row["count"]),
                    }
                    for row in rows
                ]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_category_breakdown(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get expense totals grouped by category for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.

        Returns:
            List of dicts with category_id, category, total, and count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT ec.id AS category_id, ec.name AS category, "
                    "COALESCE(SUM(e.amount), 0) AS total, "
                    "COUNT(*) AS count "
                    "FROM expenses e "
                    "JOIN expense_categories ec ON ec.id = e.category_id "
                    "WHERE e.expense_date BETWEEN %s AND %s "
                    "GROUP BY ec.id, ec.name "
                    "ORDER BY total DESC",
                    (start_date, end_date),
                )
                rows = cursor.fetchall()
                return [
                    {
                        "category_id": row["category_id"],
                        "category": row["category"],
                        "total": float(row["total"]),
                        "count": int(row["count"]),
                    }
                    for row in rows
                ]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_payment_method_breakdown(
        self, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """Get expense totals grouped by payment method for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.

        Returns:
            List of dicts with payment_method, total, and count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT payment_method, COALESCE(SUM(amount), 0) AS total, "
                    "COUNT(*) AS count "
                    "FROM expenses "
                    "WHERE expense_date BETWEEN %s AND %s "
                    "GROUP BY payment_method "
                    "ORDER BY total DESC",
                    (start_date, end_date),
                )
                rows = cursor.fetchall()
                return [
                    {
                        "payment_method": row["payment_method"],
                        "total": float(row["total"]),
                        "count": int(row["count"]),
                    }
                    for row in rows
                ]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_monthly_comparison(self, year: int) -> List[Dict[str, Any]]:
        """Get monthly expense comparison for a year.

        Returns a row for every month 1-12, with zeroes for months
        that have no expenses.

        Args:
            year: Year (e.g. 2026).

        Returns:
            List of dicts with month (1-12), total, and count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT MONTH(expense_date) AS month, "
                    "COALESCE(SUM(amount), 0) AS total, "
                    "COUNT(*) AS count "
                    "FROM expenses "
                    "WHERE YEAR(expense_date) = %s "
                    "GROUP BY MONTH(expense_date) "
                    "ORDER BY month",
                    (year,),
                )
                rows = cursor.fetchall()
                by_month = {
                    int(row["month"]): {
                        "month": int(row["month"]),
                        "total": float(row["total"]),
                        "count": int(row["count"]),
                    }
                    for row in rows
                }
                return [
                    by_month.get(month, {
                        "month": month,
                        "total": 0.0,
                        "count": 0,
                    })
                    for month in range(1, 13)
                ]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_yearly_comparison(
        self, from_year: int, to_year: int
    ) -> List[Dict[str, Any]]:
        """Get yearly expense comparison across a range of years.

        Returns a row for every year in the range, with zeroes for
        years that have no expenses.

        Args:
            from_year: First year (inclusive).
            to_year: Last year (inclusive).

        Returns:
            List of dicts with year, total, and count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT YEAR(expense_date) AS year, "
                    "COALESCE(SUM(amount), 0) AS total, "
                    "COUNT(*) AS count "
                    "FROM expenses "
                    "WHERE YEAR(expense_date) BETWEEN %s AND %s "
                    "GROUP BY YEAR(expense_date) "
                    "ORDER BY year",
                    (from_year, to_year),
                )
                rows = cursor.fetchall()
                by_year = {
                    int(row["year"]): {
                        "year": int(row["year"]),
                        "total": float(row["total"]),
                        "count": int(row["count"]),
                    }
                    for row in rows
                }
                return [
                    by_year.get(year, {
                        "year": year,
                        "total": 0.0,
                        "count": 0,
                    })
                    for year in range(from_year, to_year + 1)
                ]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_highest_categories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get expense categories with the highest totals.

        Args:
            limit: Maximum number of categories to return.

        Returns:
            List of dicts with category_id, category, total, and count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT ec.id AS category_id, ec.name AS category, "
                    "COALESCE(SUM(e.amount), 0) AS total, "
                    "COUNT(*) AS count "
                    "FROM expenses e "
                    "JOIN expense_categories ec ON ec.id = e.category_id "
                    "GROUP BY ec.id, ec.name "
                    "ORDER BY total DESC LIMIT %s",
                    (limit,),
                )
                rows = cursor.fetchall()
                return [
                    {
                        "category_id": row["category_id"],
                        "category": row["category"],
                        "total": float(row["total"]),
                        "count": int(row["count"]),
                    }
                    for row in rows
                ]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()
