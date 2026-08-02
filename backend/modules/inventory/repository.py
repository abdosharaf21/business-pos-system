"""Inventory repository for database operations on inventory and stock_movements."""

from typing import Optional, List, Dict, Any, Tuple

import mysql.connector

from backend.database import Database


class InventoryRepository:
    """Repository for inventory database operations.

    Handles per-location stock queries, transfers, adjustments, and
    stock movement logging using parameterized queries and a shared
    connection pool. Multi-statement operations run in a single
    transaction with commit on success and rollback on error.
    """

    def __init__(self, database: Database) -> None:
        """Initialize InventoryRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a product with its current stock levels.

        Args:
            product_id: The unique identifier of the product.

        Returns:
            Dictionary with product info and stock levels, or None.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT p.id, p.name, p.barcode, p.status, p.minimum_stock, "
                    "p.purchase_price, p.selling_price, "
                    "COALESCE(wh.quantity, 0) AS warehouse_qty, "
                    "COALESCE(st.quantity, 0) AS store_qty "
                    "FROM products p "
                    "LEFT JOIN inventory wh ON wh.product_id = p.id "
                    "AND wh.location = 'warehouse' "
                    "LEFT JOIN inventory st ON st.product_id = p.id "
                    "AND st.location = 'store' "
                    "WHERE p.id = %s",
                    (product_id,),
                )
                row = cursor.fetchone()
                if row:
                    row["total"] = int(row["warehouse_qty"]) + int(row["store_qty"])
                return row
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_inventory_with_stock(
        self, search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve all active products with per-location stock.

        Args:
            search: Optional search term to filter by name or barcode.

        Returns:
            List of product dictionaries with warehouse_qty and store_qty.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = (
                    "SELECT p.id, p.name, p.barcode, p.minimum_stock, "
                    "p.purchase_price, p.selling_price, p.status, p.category_id, "
                    "c.name AS category_name, "
                    "COALESCE(wh.quantity, 0) AS warehouse_qty, "
                    "COALESCE(st.quantity, 0) AS store_qty "
                    "FROM products p "
                    "LEFT JOIN categories c ON c.id = p.category_id "
                    "LEFT JOIN inventory wh ON wh.product_id = p.id "
                    "AND wh.location = 'warehouse' "
                    "LEFT JOIN inventory st ON st.product_id = p.id "
                    "AND st.location = 'store' "
                )
                params: tuple = ()

                if search:
                    query += (
                        "WHERE p.name LIKE %s OR p.barcode LIKE %s "
                    )
                    params = (f"%{search}%", f"%{search}%")

                query += "ORDER BY p.name ASC"
                cursor.execute(query, params)
                rows = cursor.fetchall()
                for row in rows:
                    row["warehouse_qty"] = int(row["warehouse_qty"])
                    row["store_qty"] = int(row["store_qty"])
                    row["total"] = row["warehouse_qty"] + row["store_qty"]
                return rows
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_inventory_summary(self) -> Dict[str, Any]:
        """Get aggregate inventory statistics.

        Returns:
            Dictionary with total_products, total_quantity, warehouse_total,
            store_total, total_value, and low_stock_count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT COUNT(*) AS count FROM products WHERE status = 'active'"
                )
                total_products = cursor.fetchone()["count"]

                cursor.execute(
                    "SELECT COALESCE(SUM(quantity), 0) AS total FROM inventory"
                )
                total_quantity = int(cursor.fetchone()["total"])

                cursor.execute(
                    "SELECT COALESCE(SUM(quantity), 0) AS total FROM inventory "
                    "WHERE location = 'warehouse'"
                )
                warehouse_total = int(cursor.fetchone()["total"])

                cursor.execute(
                    "SELECT COALESCE(SUM(quantity), 0) AS total FROM inventory "
                    "WHERE location = 'store'"
                )
                store_total = int(cursor.fetchone()["total"])

                cursor.execute(
                    "SELECT COALESCE(SUM(p.purchase_price * i.quantity), 0) AS value "
                    "FROM inventory i "
                    "JOIN products p ON p.id = i.product_id "
                    "WHERE p.status = 'active'"
                )
                total_value = float(cursor.fetchone()["value"])

                cursor.execute(
                    "SELECT COUNT(*) AS count FROM ("
                    "SELECT p.id FROM products p "
                    "JOIN inventory i ON i.product_id = p.id "
                    "WHERE p.status = 'active' "
                    "GROUP BY p.id, p.minimum_stock "
                    "HAVING SUM(i.quantity) <= p.minimum_stock"
                    ") AS low"
                )
                low_stock_count = cursor.fetchone()["count"]

                return {
                    "total_products": total_products,
                    "total_quantity": total_quantity,
                    "warehouse_total": warehouse_total,
                    "store_total": store_total,
                    "total_value": total_value,
                    "low_stock_count": low_stock_count,
                }
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_low_stock_products(self) -> List[Dict[str, Any]]:
        """Retrieve active products whose total stock is at or below minimum.

        Returns:
            List of product dictionaries with per-location stock.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT p.id, p.name, p.barcode, p.minimum_stock, "
                    "p.selling_price, c.name AS category_name, "
                    "COALESCE(wh.quantity, 0) AS warehouse_qty, "
                    "COALESCE(st.quantity, 0) AS store_qty, "
                    "(COALESCE(wh.quantity, 0) + COALESCE(st.quantity, 0)) AS total "
                    "FROM products p "
                    "LEFT JOIN categories c ON c.id = p.category_id "
                    "LEFT JOIN inventory wh ON wh.product_id = p.id "
                    "AND wh.location = 'warehouse' "
                    "LEFT JOIN inventory st ON st.product_id = p.id "
                    "AND st.location = 'store' "
                    "WHERE p.status = 'active' "
                    "AND (COALESCE(wh.quantity, 0) + COALESCE(st.quantity, 0)) "
                    "<= p.minimum_stock "
                    "ORDER BY (COALESCE(wh.quantity, 0) + COALESCE(st.quantity, 0) "
                    "- p.minimum_stock) ASC"
                )
                rows = cursor.fetchall()
                for row in rows:
                    row["warehouse_qty"] = int(row["warehouse_qty"])
                    row["store_qty"] = int(row["store_qty"])
                    row["total"] = int(row["total"])
                return rows
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_movements(
        self,
        product_id: Optional[int] = None,
        movement_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Retrieve stock movement records with optional filters.

        Args:
            product_id: Optional filter by product ID.
            movement_type: Optional filter by movement type.
            start_date: Optional start date (YYYY-MM-DD) filter.
            end_date: Optional end date (YYYY-MM-DD) filter.
            limit: Maximum number of records to return.
            offset: Pagination offset.

        Returns:
            List of movement dictionaries with product name.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = (
                    "SELECT m.id, m.product_id, m.from_location, m.to_location, "
                    "m.quantity, m.movement_type, m.reference, m.notes, "
                    "m.user_id, m.created_at, p.name AS product_name "
                    "FROM stock_movements m "
                    "JOIN products p ON p.id = m.product_id "
                )
                conditions: list = []
                params: list = []

                if product_id:
                    conditions.append("m.product_id = %s")
                    params.append(product_id)

                if movement_type:
                    conditions.append("m.movement_type = %s")
                    params.append(movement_type)

                if start_date and end_date:
                    conditions.append("DATE(m.created_at) BETWEEN %s AND %s")
                    params.extend([start_date, end_date])

                if conditions:
                    query += "WHERE " + " AND ".join(conditions) + " "

                query += "ORDER BY m.created_at DESC, m.id DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                cursor.execute(query, tuple(params))
                return cursor.fetchall()
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def ensure_stock_rows(self, product_id: int, cursor=None) -> None:
        """Create warehouse/store stock rows for a product if missing.

        Args:
            product_id: The product to ensure stock rows for.
            cursor: Optional active cursor (used inside a transaction).
        """
        sql = (
            "INSERT IGNORE INTO inventory (product_id, location, quantity) "
            "VALUES (%s, 'warehouse', 0), (%s, 'store', 0)"
        )
        if cursor is not None:
            cursor.execute(sql, (product_id, product_id))
            return

        with self._database.connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute(sql, (product_id, product_id))
                conn.commit()
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cur.close()

    @staticmethod
    def _sync_product_total(cursor, product_id: int) -> None:
        """Sync the products.quantity total from the inventory rows.

        Args:
            cursor: Active database cursor.
            product_id: The product to synchronize.
        """
        cursor.execute(
            "UPDATE products p SET p.quantity = COALESCE(("
            "SELECT SUM(i.quantity) FROM inventory i WHERE i.product_id = %s), 0) "
            "WHERE p.id = %s",
            (product_id, product_id),
        )

    @staticmethod
    def _movement_locations(
        movement_type: str, location: str, delta: int
    ) -> Tuple[Optional[str], Optional[str]]:
        """Determine from/to locations for a movement record.

        Args:
            movement_type: Type of movement (return, damage, adjustment).
            location: Location the movement applies to.
            delta: Signed quantity change.

        Returns:
            Tuple of (from_location, to_location).
        """
        if movement_type == "return":
            return None, "store"
        if movement_type == "damage":
            return location, None
        if delta >= 0:
            return None, location
        return location, None

    def transfer(
        self,
        product_id: int,
        quantity: int,
        user_id: Optional[int] = None,
        reference: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Move stock from the warehouse to the store in one transaction.

        Args:
            product_id: ID of the product to transfer.
            quantity: Units to transfer (must be positive).
            user_id: ID of the user performing the transfer.
            reference: Optional external reference.
            notes: Optional note.

        Returns:
            Dictionary describing the transfer.

        Raises:
            ValueError: If the product has no warehouse record or stock is insufficient.
            mysql.connector.Error: If the database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT id, quantity FROM inventory "
                    "WHERE product_id = %s AND location = 'warehouse' FOR UPDATE",
                    (product_id,),
                )
                warehouse = cursor.fetchone()
                if warehouse is None:
                    raise ValueError("Product has no warehouse stock record")

                if warehouse["quantity"] < quantity:
                    raise ValueError(
                        f"Insufficient warehouse stock: available "
                        f"{warehouse['quantity']}, requested {quantity}"
                    )

                cursor.execute(
                    "UPDATE inventory SET quantity = quantity - %s WHERE id = %s",
                    (quantity, warehouse["id"]),
                )

                cursor.execute(
                    "INSERT INTO inventory (product_id, location, quantity) "
                    "VALUES (%s, 'store', %s) "
                    "ON DUPLICATE KEY UPDATE quantity = quantity + %s",
                    (product_id, quantity, quantity),
                )

                cursor.execute(
                    "INSERT INTO stock_movements "
                    "(product_id, from_location, to_location, quantity, "
                    "movement_type, reference, notes, user_id) "
                    "VALUES (%s, 'warehouse', 'store', %s, 'transfer', %s, %s, %s)",
                    (product_id, quantity, reference, notes, user_id),
                )

                self._sync_product_total(cursor, product_id)
                conn.commit()

                return {
                    "product_id": product_id,
                    "quantity": quantity,
                    "from_location": "warehouse",
                    "to_location": "store",
                    "reference": reference,
                    "notes": notes,
                }
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def adjust(
        self,
        product_id: int,
        location: str,
        quantity: int,
        movement_type: str,
        user_id: Optional[int] = None,
        reference: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Apply a signed quantity change to a location in one transaction.

        Args:
            product_id: ID of the product to adjust.
            location: Location to adjust (warehouse or store).
            quantity: Signed quantity change (positive adds, negative removes).
            movement_type: Type of movement (adjustment, damage, return).
            user_id: ID of the user performing the adjustment.
            reference: Optional external reference.
            notes: Optional note.

        Returns:
            Dictionary describing the adjustment.

        Raises:
            ValueError: If the location has no record or stock would go negative.
            mysql.connector.Error: If the database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT id, quantity FROM inventory "
                    "WHERE product_id = %s AND location = %s FOR UPDATE",
                    (product_id, location),
                )
                stock = cursor.fetchone()
                if stock is None:
                    cursor.execute(
                        "INSERT IGNORE INTO inventory "
                        "(product_id, location, quantity) VALUES (%s, %s, 0)",
                        (product_id, location),
                    )
                    cursor.execute(
                        "SELECT id, quantity FROM inventory "
                        "WHERE product_id = %s AND location = %s FOR UPDATE",
                        (product_id, location),
                    )
                    stock = cursor.fetchone()

                new_quantity = int(stock["quantity"]) + quantity
                if new_quantity < 0:
                    raise ValueError(
                        f"Insufficient {location} stock: current "
                        f"{stock['quantity']}, requested change {quantity}"
                    )

                cursor.execute(
                    "UPDATE inventory SET quantity = %s WHERE id = %s",
                    (new_quantity, stock["id"]),
                )

                from_location, to_location = self._movement_locations(
                    movement_type, location, quantity
                )

                cursor.execute(
                    "INSERT INTO stock_movements "
                    "(product_id, from_location, to_location, quantity, "
                    "movement_type, reference, notes, user_id) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (product_id, from_location, to_location, abs(quantity),
                     movement_type, reference, notes, user_id),
                )

                self._sync_product_total(cursor, product_id)
                conn.commit()

                return {
                    "product_id": product_id,
                    "location": location,
                    "quantity": quantity,
                    "movement_type": movement_type,
                    "reference": reference,
                    "notes": notes,
                    "new_quantity": new_quantity,
                }
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()
