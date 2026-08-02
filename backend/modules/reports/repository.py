"""Report repository for read-only analytics queries."""

from datetime import date, timedelta
from typing import Dict, Any, List

from backend.database.connection import Database


class ReportRepository:
    """Repository for report and analytics data.

    Performs read-only aggregation queries across multiple POS tables.
    All methods use COALESCE to return zero values for empty tables.
    """

    def __init__(self, database: Database) -> None:
        self._database = database

    def get_sales_summary(self) -> Dict[str, Any]:
        """Calculate sales summary metrics.

        Returns:
            Dictionary with today_sales, monthly_sales, total_invoices,
            and average_invoice_value.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT COUNT(*) AS count, "
                "COALESCE(SUM(paid_amount), 0) AS total "
                "FROM sales WHERE DATE(created_at) = CURDATE() "
                "AND status = 'completed'"
            )
            today = cursor.fetchone()
            today_sales = float(today["total"])
            today_invoices = today["count"]

            cursor.execute(
                "SELECT COUNT(*) AS count, "
                "COALESCE(SUM(paid_amount), 0) AS total "
                "FROM sales WHERE DATE_FORMAT(created_at, '%Y-%m') = "
                "DATE_FORMAT(CURDATE(), '%Y-%m') AND status = 'completed'"
            )
            monthly = cursor.fetchone()
            monthly_sales = float(monthly["total"])
            monthly_invoices = monthly["count"]

            cursor.execute(
                "SELECT COUNT(*) AS count FROM sales WHERE status = 'completed'"
            )
            total_invoices = cursor.fetchone()["count"]

            cursor.execute(
                "SELECT COALESCE(AVG(paid_amount), 0) AS avg_value "
                "FROM sales WHERE status = 'completed'"
            )
            avg_value = float(cursor.fetchone()["avg_value"])

            cursor.close()

        return {
            "today_sales": today_sales,
            "today_invoices": today_invoices,
            "monthly_sales": monthly_sales,
            "monthly_invoices": monthly_invoices,
            "total_invoices": total_invoices,
            "average_invoice_value": avg_value,
        }

    def get_purchase_summary(self) -> Dict[str, Any]:
        """Calculate purchase summary metrics.

        Returns:
            Dictionary with today_purchases, monthly_purchases,
            and total_purchase_invoices.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT COUNT(*) AS count, "
                "COALESCE(SUM(total_amount), 0) AS total "
                "FROM purchases WHERE DATE(created_at) = CURDATE() "
                "AND status = 'completed'"
            )
            today = cursor.fetchone()
            today_purchases = float(today["total"])
            today_invoices = today["count"]

            cursor.execute(
                "SELECT COUNT(*) AS count, "
                "COALESCE(SUM(total_amount), 0) AS total "
                "FROM purchases WHERE DATE_FORMAT(created_at, '%Y-%m') = "
                "DATE_FORMAT(CURDATE(), '%Y-%m') AND status = 'completed'"
            )
            monthly = cursor.fetchone()
            monthly_purchases = float(monthly["total"])
            monthly_invoices = monthly["count"]

            cursor.execute(
                "SELECT COUNT(*) AS count FROM purchases WHERE status = 'completed'"
            )
            total_purchase_invoices = cursor.fetchone()["count"]

            cursor.close()

        return {
            "today_purchases": today_purchases,
            "today_invoices": today_invoices,
            "monthly_purchases": monthly_purchases,
            "monthly_invoices": monthly_invoices,
            "total_purchase_invoices": total_purchase_invoices,
        }

    def get_inventory_summary(self) -> Dict[str, Any]:
        """Calculate inventory summary metrics.

        Returns:
            Dictionary with total_products, inventory_value,
            and low_stock_count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT COUNT(*) AS count FROM products WHERE status = 'active'")
            total_products = cursor.fetchone()["count"]

            cursor.execute(
                "SELECT COALESCE(SUM(purchase_price * quantity), 0) AS value "
                "FROM products WHERE status = 'active'"
            )
            inventory_value = float(cursor.fetchone()["value"])

            cursor.execute(
                "SELECT COUNT(*) AS count FROM products "
                "WHERE quantity <= minimum_stock AND status = 'active'"
            )
            low_stock_count = cursor.fetchone()["count"]

            cursor.close()

        return {
            "total_products": total_products,
            "inventory_value": inventory_value,
            "low_stock_count": low_stock_count,
        }

    def get_top_selling_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top selling products by quantity sold.

        Args:
            limit: Maximum number of products to return.

        Returns:
            List of dicts with product id, name, total quantity sold,
            and total revenue.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT p.id, p.name, "
                "SUM(si.quantity) AS total_quantity, "
                "COALESCE(SUM(si.subtotal), 0) AS total_revenue "
                "FROM sale_items si "
                "JOIN products p ON p.id = si.product_id "
                "JOIN sales s ON s.id = si.sale_id "
                "WHERE s.status = 'completed' "
                "GROUP BY p.id, p.name "
                "ORDER BY total_quantity DESC LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()
            cursor.close()

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "total_quantity": row["total_quantity"],
                "total_revenue": float(row["total_revenue"]),
            }
            for row in rows
        ]

    def get_recent_sales(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent completed sales.

        Args:
            limit: Maximum number of sales to return.

        Returns:
            List of dicts with sale id, invoice_number, total_amount,
            and created_at.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT id, invoice_number, paid_amount, created_at "
                "FROM sales WHERE status = 'completed' "
                "ORDER BY created_at DESC LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()
            cursor.close()

        return [
            {
                "id": row["id"],
                "invoice_number": row["invoice_number"],
                "total_amount": float(row["paid_amount"]),
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in rows
        ]

    def get_sales_trend(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get daily sales data for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.

        Returns:
            List of dicts with date, total_sales, invoice_count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT DATE(created_at) AS date, "
                "COUNT(*) AS invoice_count, "
                "COALESCE(SUM(paid_amount), 0) AS total_sales "
                "FROM sales "
                "WHERE status = 'completed' "
                "AND DATE(created_at) BETWEEN %s AND %s "
                "GROUP BY DATE(created_at) "
                "ORDER BY date",
                (start_date, end_date),
            )
            rows = cursor.fetchall()
            cursor.close()

        return [
            {
                "date": row["date"].isoformat() if row["date"] else None,
                "total_sales": float(row["total_sales"]),
                "invoice_count": row["invoice_count"],
            }
            for row in rows
        ]

    def get_profit_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Calculate profit metrics for a date range.

        Revenue = SUM of sale_items.subtotal for completed sales.
        Cost = SUM of sale_items.quantity * products.purchase_price for completed sales.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.

        Returns:
            Dictionary with total_revenue, total_purchase_cost,
            gross_profit, and profit_margin.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT COALESCE(SUM(si.subtotal), 0) AS revenue, "
                "COALESCE(SUM(si.quantity * p.purchase_price), 0) AS cost "
                "FROM sale_items si "
                "JOIN products p ON p.id = si.product_id "
                "JOIN sales s ON s.id = si.sale_id "
                "WHERE s.status = 'completed' "
                "AND DATE(s.created_at) BETWEEN %s AND %s",
                (start_date, end_date),
            )
            row = cursor.fetchone()
            cursor.close()

        revenue = float(row["revenue"])
        cost = float(row["cost"])
        gross_profit = revenue - cost
        profit_margin = (gross_profit / revenue * 100) if revenue > 0 else 0.0

        return {
            "total_revenue": revenue,
            "total_purchase_cost": cost,
            "gross_profit": gross_profit,
            "profit_margin": round(profit_margin, 2),
        }

    def get_products_performance(self) -> Dict[str, Any]:
        """Get top and slow performing products.

        Returns:
            Dictionary with top_products (highest revenue) and
            slow_products (lowest quantity sold).
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT p.id, p.name, "
                "COALESCE(SUM(si.quantity), 0) AS quantity_sold, "
                "COALESCE(SUM(si.subtotal), 0) AS revenue "
                "FROM products p "
                "LEFT JOIN sale_items si ON si.product_id = p.id "
                "LEFT JOIN sales s ON s.id = si.sale_id AND s.status = 'completed' "
                "WHERE p.status = 'active' "
                "GROUP BY p.id, p.name "
                "ORDER BY revenue DESC"
            )
            all_products = cursor.fetchall()
            cursor.close()

        formatted = [
            {
                "id": row["id"],
                "name": row["name"],
                "quantity_sold": row["quantity_sold"],
                "revenue": float(row["revenue"]),
            }
            for row in all_products
        ]

        top_products = [p for p in formatted if p["quantity_sold"] > 0][:10]
        products_with_sales = [p for p in formatted if p["quantity_sold"] > 0]
        slow_products = sorted(products_with_sales, key=lambda x: x["quantity_sold"])[:5]

        return {
            "top_products": top_products,
            "slow_products": slow_products,
        }

    def get_suppliers_performance(self) -> List[Dict[str, Any]]:
        """Get supplier spending summary.

        Returns:
            List of dicts with supplier id, name, total purchases amount,
            and purchase count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT s.id, s.name, "
                "COALESCE(SUM(p.total_amount), 0) AS total_purchases, "
                "COUNT(p.id) AS purchase_count "
                "FROM suppliers s "
                "LEFT JOIN purchases p ON p.supplier_id = s.id "
                "AND p.status = 'completed' "
                "GROUP BY s.id, s.name "
                "ORDER BY total_purchases DESC"
            )
            rows = cursor.fetchall()
            cursor.close()

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "total_purchases": float(row["total_purchases"]),
                "purchase_count": row["purchase_count"],
            }
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Inventory reports
    # ------------------------------------------------------------------

    def get_inventory_report(self) -> List[Dict[str, Any]]:
        """Get per-product stock levels by location.

        Returns:
            List of dicts with product info, warehouse_qty, store_qty,
            total, and stock value.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT p.id, p.name, p.sku, p.barcode, p.minimum_stock, "
                "p.purchase_price, c.name AS category_name, "
                "COALESCE(wh.quantity, 0) AS warehouse_qty, "
                "COALESCE(st.quantity, 0) AS store_qty "
                "FROM products p "
                "LEFT JOIN categories c ON c.id = p.category_id "
                "LEFT JOIN inventory wh ON wh.product_id = p.id "
                "AND wh.location = 'warehouse' "
                "LEFT JOIN inventory st ON st.product_id = p.id "
                "AND st.location = 'store' "
                "WHERE p.status = 'active' "
                "ORDER BY p.name ASC"
            )
            rows = cursor.fetchall()
            cursor.close()

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "sku": row["sku"],
                "barcode": row["barcode"],
                "category_name": row["category_name"],
                "minimum_stock": int(row["minimum_stock"]),
                "purchase_price": float(row["purchase_price"]),
                "warehouse_qty": int(row["warehouse_qty"]),
                "store_qty": int(row["store_qty"]),
                "total": int(row["warehouse_qty"]) + int(row["store_qty"]),
            }
            for row in rows
        ]

    def get_movement_monthly(self, year: int, month: int) -> List[Dict[str, Any]]:
        """Get movement summary grouped by type for a month.

        Args:
            year: Year (e.g. 2026).
            month: Month number 1-12.

        Returns:
            List of dicts with movement_type, quantity, and count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT movement_type, "
                "COALESCE(SUM(quantity), 0) AS quantity, "
                "COUNT(*) AS count "
                "FROM stock_movements "
                "WHERE YEAR(created_at) = %s AND MONTH(created_at) = %s "
                "GROUP BY movement_type "
                "ORDER BY quantity DESC",
                (year, month),
            )
            rows = cursor.fetchall()
            cursor.close()

        return [
            {
                "movement_type": row["movement_type"],
                "quantity": int(row["quantity"]),
                "count": int(row["count"]),
            }
            for row in rows
        ]

    def get_movement_yearly(self, year: int) -> List[Dict[str, Any]]:
        """Get movement summary grouped by month for a year.

        Args:
            year: Year (e.g. 2026).

        Returns:
            List of dicts with month (1-12), quantity, and count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT MONTH(created_at) AS month, "
                "COALESCE(SUM(quantity), 0) AS quantity, "
                "COUNT(*) AS count "
                "FROM stock_movements "
                "WHERE YEAR(created_at) = %s "
                "GROUP BY MONTH(created_at) "
                "ORDER BY month",
                (year,),
            )
            rows = cursor.fetchall()
            cursor.close()

        return [
            {
                "month": int(row["month"]),
                "quantity": int(row["quantity"]),
                "count": int(row["count"]),
            }
            for row in rows
        ]

    def get_most_transferred(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get products with the highest total transfer volume.

        Args:
            limit: Maximum number of products to return.

        Returns:
            List of dicts with product id, name, total quantity,
            and transfer count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT m.product_id, p.name, "
                "COALESCE(SUM(m.quantity), 0) AS total_quantity, "
                "COUNT(*) AS transfer_count "
                "FROM stock_movements m "
                "JOIN products p ON p.id = m.product_id "
                "WHERE m.movement_type = 'transfer' "
                "GROUP BY m.product_id, p.name "
                "ORDER BY total_quantity DESC LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()
            cursor.close()

        return [
            {
                "product_id": row["product_id"],
                "name": row["name"],
                "total_quantity": int(row["total_quantity"]),
                "transfer_count": int(row["transfer_count"]),
            }
            for row in rows
        ]

    def get_lowest_stock(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get products with the lowest total stock.

        Args:
            limit: Maximum number of products to return.

        Returns:
            List of dicts with product info and stock levels.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT p.id, p.name, p.sku, p.minimum_stock, "
                "p.selling_price, c.name AS category_name, "
                "COALESCE(wh.quantity, 0) AS warehouse_qty, "
                "COALESCE(st.quantity, 0) AS store_qty "
                "FROM products p "
                "LEFT JOIN categories c ON c.id = p.category_id "
                "LEFT JOIN inventory wh ON wh.product_id = p.id "
                "AND wh.location = 'warehouse' "
                "LEFT JOIN inventory st ON st.product_id = p.id "
                "AND st.location = 'store' "
                "WHERE p.status = 'active' "
                "ORDER BY (COALESCE(wh.quantity, 0) + COALESCE(st.quantity, 0)) ASC "
                "LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()
            cursor.close()

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "sku": row["sku"],
                "category_name": row["category_name"],
                "minimum_stock": int(row["minimum_stock"]),
                "selling_price": float(row["selling_price"]),
                "warehouse_qty": int(row["warehouse_qty"]),
                "store_qty": int(row["store_qty"]),
                "total": int(row["warehouse_qty"]) + int(row["store_qty"]),
            }
            for row in rows
        ]
