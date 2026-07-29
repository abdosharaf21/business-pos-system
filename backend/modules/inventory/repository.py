"""Inventory repository for database operations on products and inventory_transactions."""

from datetime import datetime
from typing import Optional, List, Dict, Any

import mysql.connector

from backend.database import Database
from backend.modules.inventory.model import InventoryTransaction


class InventoryRepository:
    """Repository for inventory database operations.

    Handles queries against the products and inventory_transactions
    tables using parameterized queries and a shared connection pool.
    """

    def __init__(self, database: Database) -> None:
        self._database = database

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a product by its unique identifier.

        Args:
            product_id: The unique identifier of the product.

        Returns:
            Dictionary of product data if found, None otherwise.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT id, name, barcode, quantity, minimum_stock, "
                    "purchase_price, selling_price, status, category_id "
                    "FROM products WHERE id = %s",
                    (product_id,),
                )
                return cursor.fetchone()
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_products_with_stock(
        self, search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve all products with stock information.

        Args:
            search: Optional search term to filter by name or barcode.

        Returns:
            List of product dictionaries with stock info.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = (
                    "SELECT p.id, p.name, p.barcode, p.quantity, "
                    "p.minimum_stock, p.purchase_price, p.selling_price, "
                    "p.status, p.category_id, c.name AS category_name "
                    "FROM products p "
                    "LEFT JOIN categories c ON c.id = p.category_id "
                )
                params: tuple = ()

                if search:
                    query += "WHERE p.name LIKE %s OR p.barcode LIKE %s "
                    params = (f"%{search}%", f"%{search}%")

                query += "ORDER BY p.name ASC"
                cursor.execute(query, params)
                return cursor.fetchall()
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_inventory_summary(self) -> Dict[str, Any]:
        """Get aggregate inventory statistics.

        Returns:
            Dictionary with total_products, total_quantity, total_value,
            low_stock_count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("SELECT COUNT(*) AS count FROM products")
                total_products = cursor.fetchone()["count"]

                cursor.execute(
                    "SELECT COALESCE(SUM(quantity), 0) AS total FROM products"
                )
                total_quantity = int(cursor.fetchone()["total"])

                cursor.execute(
                    "SELECT COALESCE(SUM(purchase_price * quantity), 0) "
                    "AS value FROM products"
                )
                total_value = float(cursor.fetchone()["value"])

                cursor.execute(
                    "SELECT COUNT(*) AS count FROM products "
                    "WHERE quantity <= minimum_stock"
                )
                low_stock_count = cursor.fetchone()["count"]

                return {
                    "total_products": total_products,
                    "total_quantity": total_quantity,
                    "total_value": total_value,
                    "low_stock_count": low_stock_count,
                }
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_low_stock_products(self) -> List[Dict[str, Any]]:
        """Retrieve products where stock is at or below minimum.

        Returns:
            List of product dictionaries with low stock.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT p.id, p.name, p.barcode, p.quantity, "
                    "p.minimum_stock, p.selling_price, c.name AS category_name "
                    "FROM products p "
                    "LEFT JOIN categories c ON c.id = p.category_id "
                    "WHERE p.quantity <= p.minimum_stock "
                    "ORDER BY (p.quantity - p.minimum_stock) ASC"
                )
                return cursor.fetchall()
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def create_transaction(
        self,
        product_id: int,
        transaction_type: str,
        quantity: int,
        reference_id: Optional[int] = None,
    ) -> InventoryTransaction:
        """Create an inventory transaction record.

        Args:
            product_id: ID of the product.
            transaction_type: Type of transaction.
            quantity: Quantity change.
            reference_id: Optional reference ID.

        Returns:
            Created InventoryTransaction instance.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO inventory_transactions "
                    "(product_id, transaction_type, quantity, reference_id) "
                    "VALUES (%s, %s, %s, %s)",
                    (product_id, transaction_type, quantity, reference_id),
                )
                conn.commit()
                transaction = InventoryTransaction(
                    id=cursor.lastrowid,
                    product_id=product_id,
                    transaction_type=transaction_type,
                    quantity=quantity,
                    reference_id=reference_id,
                    created_at=datetime.now(),
                )
                return transaction
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def update_product_stock(self, product_id: int, new_quantity: int) -> bool:
        """Update the stock quantity of a product.

        Args:
            product_id: ID of the product.
            new_quantity: The new stock quantity.

        Returns:
            True if updated, False if product not found.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE products SET quantity = %s WHERE id = %s",
                    (new_quantity, product_id),
                )
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def get_transactions(
        self, product_id: Optional[int] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve inventory transaction records.

        Args:
            product_id: Optional filter by product ID.
            limit: Maximum number of records to return.

        Returns:
            List of transaction dictionaries with product name.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = (
                    "SELECT t.id, t.product_id, t.transaction_type, "
                    "t.quantity, t.reference_id, t.created_at, "
                    "p.name AS product_name "
                    "FROM inventory_transactions t "
                    "JOIN products p ON p.id = t.product_id "
                )
                params: list = []

                if product_id:
                    query += "WHERE t.product_id = %s "
                    params.append(product_id)

                query += "ORDER BY t.created_at DESC LIMIT %s"
                params.append(limit)

                cursor.execute(query, tuple(params))
                return cursor.fetchall()
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()
