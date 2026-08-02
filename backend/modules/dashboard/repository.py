"""Dashboard repository for POS statistics queries."""

from typing import Dict, Any

from backend.database.connection import Database


class DashboardRepository:
    """Repository for dashboard statistics.

    Aggregates data across multiple POS tables using raw SQL
    queries. Returns zero values for empty tables instead of
    raising exceptions.
    """

    def __init__(self, database: Database) -> None:
        """Initialize DashboardRepository.

        Args:
            database: Database instance for connection management.
        """
        self._database = database

    def get_statistics(self) -> Dict[str, Any]:
        """Collect all POS dashboard statistics.

        Returns:
            Dictionary with total counts and today's figures.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT COUNT(*) AS count FROM products")
            total_products = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM categories")
            total_categories = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM customers")
            total_customers = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM suppliers")
            total_suppliers = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM sales")
            total_sales = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM purchases")
            total_purchases = cursor.fetchone()["count"]

            cursor.execute(
                "SELECT COUNT(*) AS count FROM products "
                "WHERE quantity <= minimum_stock"
            )
            low_stock_products = cursor.fetchone()["count"]

            cursor.execute(
                "SELECT COALESCE(SUM(purchase_price * quantity), 0) "
                "AS value FROM products"
            )
            inventory_value = float(cursor.fetchone()["value"])

            cursor.execute(
                "SELECT COUNT(*) AS count FROM sales "
                "WHERE DATE(created_at) = CURDATE()"
            )
            todays_sales = cursor.fetchone()["count"]

            cursor.execute(
                "SELECT COALESCE(SUM(paid_amount), 0) AS revenue "
                "FROM sales WHERE DATE(created_at) = CURDATE()"
            )
            todays_revenue = float(cursor.fetchone()["revenue"])

            cursor.execute(
                "SELECT COALESCE(SUM(amount), 0) AS total "
                "FROM expenses WHERE expense_date = CURDATE()"
            )
            today_expenses = float(cursor.fetchone()["total"])

            cursor.execute(
                "SELECT COALESCE(SUM(amount), 0) AS total "
                "FROM expenses WHERE DATE_FORMAT(expense_date, '%Y-%m') = "
                "DATE_FORMAT(CURDATE(), '%Y-%m')"
            )
            month_expenses = float(cursor.fetchone()["total"])

            cursor.execute(
                "SELECT COALESCE(SUM(amount), 0) AS total "
                "FROM expenses WHERE YEAR(expense_date) = YEAR(CURDATE())"
            )
            year_expenses = float(cursor.fetchone()["total"])

            cursor.execute(
                "SELECT COALESCE(AVG(monthly.total), 0) AS avg_monthly "
                "FROM ("
                "  SELECT SUM(amount) AS total "
                "  FROM expenses "
                "  WHERE expense_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) "
                "  GROUP BY DATE_FORMAT(expense_date, '%Y-%m')"
                ") monthly"
            )
            avg_month_expenses = float(cursor.fetchone()["avg_monthly"])

            cursor.execute(
                "SELECT ec.name AS category FROM expenses e "
                "JOIN expense_categories ec ON ec.id = e.category_id "
                "WHERE e.expense_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) "
                "GROUP BY ec.id, ec.name "
                "ORDER BY SUM(e.amount) DESC LIMIT 1"
            )
            row = cursor.fetchone()
            highest_expense_category = row["category"] if row else None

            cursor.execute(
                "SELECT COUNT(*) AS count FROM inventory_audits "
                "WHERE status = 'open'"
            )
            open_audits = cursor.fetchone()["count"]

            cursor.execute(
                "SELECT COUNT(*) AS count FROM inventory_audits "
                "WHERE status = 'completed'"
            )
            completed_audits = cursor.fetchone()["count"]

            cursor.close()

        return {
            "total_products": total_products,
            "total_categories": total_categories,
            "total_customers": total_customers,
            "total_suppliers": total_suppliers,
            "total_sales": total_sales,
            "total_purchases": total_purchases,
            "low_stock_products": low_stock_products,
            "inventory_value": inventory_value,
            "todays_sales": todays_sales,
            "todays_revenue": todays_revenue,
            "today_expenses": today_expenses,
            "month_expenses": month_expenses,
            "year_expenses": year_expenses,
            "avg_month_expenses": avg_month_expenses,
            "highest_expense_category": highest_expense_category,
            "open_audits": open_audits,
            "completed_audits": completed_audits,
        }
