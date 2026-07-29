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
        }
