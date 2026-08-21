"""Inventory repository for database operations on inventory and stock_movements."""

from typing import Optional, List, Dict, Any

import mysql.connector

from backend.database import Database
from backend.shared.expiration import normalize_expiration_date
from backend.shared.database import db_cursor


class InventoryRepository:
    """Repository for inventory database operations.

    Handles per-location stock queries, transfers, and
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
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT p.id, p.name, p.barcode, p.status, p.minimum_stock, "
                    "p.purchase_price, p.selling_price, "
                    "COALESCE(SUM(wh.quantity), 0) AS warehouse_qty, "
                    "COALESCE(st.quantity, 0) AS store_qty, "
                    "e.expiration_date "
                    "FROM products p "
                    "LEFT JOIN inventory wh ON wh.product_id = p.id "
                    "AND wh.location = 'warehouse' "
                    "LEFT JOIN inventory st ON st.product_id = p.id "
                    "AND st.location = 'store' "
                    "LEFT JOIN ("
                    "SELECT product_id, MIN(expiration_date) AS expiration_date "
                    "FROM purchase_items WHERE expiration_date IS NOT NULL "
                    "GROUP BY product_id"
                    ") e ON e.product_id = p.id "
                    "WHERE p.id = %s "
                    "GROUP BY p.id, p.name, p.barcode, p.status, p.minimum_stock, "
                    "p.purchase_price, p.selling_price, st.quantity, "
                    "e.expiration_date",
                    (product_id,),
                )
                row = cursor.fetchone()
                if row:
                    row["total"] = int(row["warehouse_qty"]) + int(row["store_qty"])
                    row["expiration_date"] = normalize_expiration_date(
                        row.get("expiration_date")
                    )
                return row
            except mysql.connector.Error:
                raise

    def get_inventory_with_stock(
        self, search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve all active products with per-location stock.

        Args:
            search: Optional search term to filter by name or barcode.

        Returns:
            List of product dictionaries with warehouse_qty and store_qty.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                query = (
                    "SELECT p.id, p.name, p.barcode, p.minimum_stock, "
                    "p.purchase_price, p.selling_price, p.status, p.category_id, "
                    "c.name AS category_name, "
                    "COALESCE(SUM(wh.quantity), 0) AS warehouse_qty, "
                    "COALESCE(st.quantity, 0) AS store_qty, "
                    "e.expiration_date "
                    "FROM products p "
                    "LEFT JOIN categories c ON c.id = p.category_id "
                    "LEFT JOIN inventory wh ON wh.product_id = p.id "
                    "AND wh.location = 'warehouse' "
                    "LEFT JOIN inventory st ON st.product_id = p.id "
                    "AND st.location = 'store' "
                    "LEFT JOIN ("
                    "SELECT product_id, MIN(expiration_date) AS expiration_date "
                    "FROM purchase_items WHERE expiration_date IS NOT NULL "
                    "GROUP BY product_id"
                    ") e ON e.product_id = p.id "
                )
                params: tuple = ()

                if search:
                    query += (
                        "WHERE p.name LIKE %s OR p.barcode LIKE %s "
                    )
                    params = (f"%{search}%", f"%{search}%")

                query += (
                    "GROUP BY p.id, p.name, p.barcode, p.minimum_stock, "
                    "p.purchase_price, p.selling_price, p.status, p.category_id, "
                    "c.name, st.quantity, e.expiration_date "
                    "ORDER BY p.name ASC"
                )
                cursor.execute(query, params)
                rows = cursor.fetchall()
                for row in rows:
                    row["warehouse_qty"] = int(row["warehouse_qty"])
                    row["store_qty"] = int(row["store_qty"])
                    row["total"] = row["warehouse_qty"] + row["store_qty"]
                    row["expiration_date"] = normalize_expiration_date(
                        row.get("expiration_date")
                    )
                return rows
            except mysql.connector.Error:
                raise

    def get_inventory_summary(self) -> Dict[str, Any]:
        """Get aggregate inventory statistics.

        Returns:
            Dictionary with total_products, total_quantity, warehouse_total,
            store_total, total_value, and low_stock_count.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
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

    def get_low_stock_products(self) -> List[Dict[str, Any]]:
        """Retrieve active products whose total stock is at or below minimum.

        Returns:
            List of product dictionaries with per-location stock.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT p.id, p.name, p.barcode, p.minimum_stock, "
                    "p.selling_price, c.name AS category_name, "
                    "COALESCE(SUM(wh.quantity), 0) AS warehouse_qty, "
                    "COALESCE(st.quantity, 0) AS store_qty, "
                    "(COALESCE(SUM(wh.quantity), 0) + COALESCE(st.quantity, 0)) AS total "
                    "FROM products p "
                    "LEFT JOIN categories c ON c.id = p.category_id "
                    "LEFT JOIN inventory wh ON wh.product_id = p.id "
                    "AND wh.location = 'warehouse' "
                    "LEFT JOIN inventory st ON st.product_id = p.id "
                    "AND st.location = 'store' "
                    "WHERE p.status = 'active' "
                    "GROUP BY p.id, p.name, p.barcode, p.minimum_stock, "
                    "p.selling_price, c.name, st.quantity "
                    "HAVING (COALESCE(SUM(wh.quantity), 0) + COALESCE(st.quantity, 0)) "
                    "<= p.minimum_stock "
                    "ORDER BY (COALESCE(SUM(wh.quantity), 0) + COALESCE(st.quantity, 0) "
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

    def _movements_query(
        self,
        product_id: Optional[int] = None,
        movement_type: Optional[str] = None,
        warehouse_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> tuple:
        """Build the shared movements WHERE clause.

        Args:
            product_id: Optional filter by product ID.
            movement_type: Optional filter by movement type.
            warehouse_id: Optional filter by warehouse ID.
            start_date: Optional start date (YYYY-MM-DD) filter.
            end_date: Optional end date (YYYY-MM-DD) filter.

        Returns:
            Tuple of (conditions list, params list).
        """
        conditions: list = []
        params: list = []

        if product_id:
            conditions.append("m.product_id = %s")
            params.append(product_id)

        if movement_type:
            conditions.append("m.movement_type = %s")
            params.append(movement_type)

        if warehouse_id:
            conditions.append("m.warehouse_id = %s")
            params.append(warehouse_id)

        if start_date and end_date:
            conditions.append("DATE(m.created_at) BETWEEN %s AND %s")
            params.extend([start_date, end_date])

        return conditions, params

    def count_movements(
        self,
        product_id: Optional[int] = None,
        movement_type: Optional[str] = None,
        warehouse_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> int:
        """Count stock movement records matching the given filters.

        Args:
            product_id: Optional filter by product ID.
            movement_type: Optional filter by movement type.
            warehouse_id: Optional filter by warehouse ID.
            start_date: Optional start date (YYYY-MM-DD) filter.
            end_date: Optional end date (YYYY-MM-DD) filter.

        Returns:
            Total number of matching movement records.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                conditions, params = self._movements_query(
                    product_id=product_id,
                    movement_type=movement_type,
                    warehouse_id=warehouse_id,
                    start_date=start_date,
                    end_date=end_date,
                )
                query = "SELECT COUNT(*) AS total FROM stock_movements m "
                if conditions:
                    query += "WHERE " + " AND ".join(conditions) + " "
                cursor.execute(query, tuple(params))
                return int(cursor.fetchone()["total"])
            except mysql.connector.Error:
                raise

    def get_movements(
        self,
        product_id: Optional[int] = None,
        movement_type: Optional[str] = None,
        warehouse_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Retrieve stock movement records with optional filters.

        Args:
            product_id: Optional filter by product ID.
            movement_type: Optional filter by movement type.
            warehouse_id: Optional filter by warehouse ID.
            start_date: Optional start date (YYYY-MM-DD) filter.
            end_date: Optional end date (YYYY-MM-DD) filter.
            limit: Maximum number of records to return.
            offset: Pagination offset.

        Returns:
            List of movement dictionaries with product, warehouse, and
            user name enrichment.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                query = (
                    "SELECT m.id, m.product_id, m.from_location, m.to_location, "
                    "m.warehouse_id, m.quantity, m.movement_type, m.reference, "
                    "m.notes, m.user_id, m.created_at, "
                    "p.name AS product_name, "
                    "w.name AS warehouse_name, "
                    "u.full_name AS user_name "
                    "FROM stock_movements m "
                    "JOIN products p ON p.id = m.product_id "
                    "LEFT JOIN warehouses w ON w.id = m.warehouse_id "
                    "LEFT JOIN users u ON u.id = m.user_id "
                )
                conditions, params = self._movements_query(
                    product_id=product_id,
                    movement_type=movement_type,
                    warehouse_id=warehouse_id,
                    start_date=start_date,
                    end_date=end_date,
                )

                if conditions:
                    query += "WHERE " + " AND ".join(conditions) + " "

                query += "ORDER BY m.created_at DESC, m.id DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                cursor.execute(query, tuple(params))
                return cursor.fetchall()
            except mysql.connector.Error:
                raise

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def update_product_expiration(
        self, product_id: int, expiration_date: str
    ) -> Dict[str, Any]:
        """Set the expiration date on a product's active purchase batch.

        Updates only when the product has exactly one purchase batch, so
        an unambiguous current batch exists. The date is applied whether
        that batch already has an expiration date or not; it never filters
        on ``expiration_date IS NULL``. When the product has multiple
        purchase batches, no row is updated because the schema has no
        batch-tracking information to determine which historical batch
        represents the current inventory; the batch count is returned so
        the caller can require explicit batch selection. Runs in a single
        transaction and returns the product's resulting effective
        expiration date.

        Args:
            product_id: ID of the product whose stock expiration is set.
            expiration_date: Expiration date as a YYYY-MM-DD string.

        Returns:
            Dictionary with the number of updated rows (1 for a single
            batch, otherwise 0), the number of purchase batches found for
            the product, and the product's effective expiration date (MIN
            of non-NULL dates, or None).

        Raises:
            mysql.connector.Error: If the database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT id FROM purchase_items "
                    "WHERE product_id = %s FOR UPDATE",
                    (product_id,),
                )
                batch_rows = cursor.fetchall()

                updated_rows = 0
                if len(batch_rows) == 1:
                    cursor.execute(
                        "UPDATE purchase_items SET expiration_date = %s "
                        "WHERE id = %s",
                        (expiration_date, batch_rows[0]["id"]),
                    )
                    updated_rows = 1

                cursor.execute(
                    "SELECT MIN(expiration_date) AS min_date FROM purchase_items "
                    "WHERE product_id = %s AND expiration_date IS NOT NULL",
                    (product_id,),
                )
                min_row = cursor.fetchone()
                conn.commit()

                return {
                    "updated_rows": updated_rows,
                    "batch_count": len(batch_rows),
                    "expiration_date": normalize_expiration_date(
                        min_row["min_date"] if min_row else None
                    ),
                }
            except mysql.connector.Error:
                conn.rollback()
                raise

    def ensure_stock_rows(self, product_id: int, cursor=None) -> None:
        """Create warehouse/store stock rows for a product if missing.

        Args:
            product_id: The product to ensure stock rows for.
            cursor: Optional active cursor (used inside a transaction).
        """
        sql = (
            "INSERT IGNORE INTO inventory (product_id, location, quantity, warehouse_id) "
            "VALUES (%s, 'warehouse', 0, "
            "(SELECT id FROM warehouses WHERE code = 'WH-MAIN')), "
            "(%s, 'store', 0, (SELECT id FROM warehouses WHERE code = 'STORE'))"
        )
        if cursor is not None:
            cursor.execute(sql, (product_id, product_id))
            return

        with self._database.connection() as conn, db_cursor(conn) as cur:
            try:
                cur.execute(sql, (product_id, product_id))
                conn.commit()
            except mysql.connector.Error:
                conn.rollback()
                raise

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
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT id, quantity FROM inventory "
                    "WHERE product_id = %s AND location = 'warehouse' "
                    "AND (warehouse_id = (SELECT id FROM warehouses "
                    "WHERE code = 'WH-MAIN') OR warehouse_id IS NULL) "
                    "ORDER BY warehouse_id IS NULL ASC LIMIT 1 FOR UPDATE",
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
                    "INSERT INTO inventory "
                    "(product_id, location, warehouse_id, quantity) "
                    "VALUES (%s, 'store', "
                    "(SELECT id FROM warehouses WHERE code = 'STORE'), %s) "
                    "ON DUPLICATE KEY UPDATE quantity = quantity + %s",
                    (product_id, quantity, quantity),
                )

                cursor.execute(
                    "INSERT INTO stock_movements "
                    "(product_id, from_location, to_location, warehouse_id, "
                    "quantity, movement_type, reference, notes, user_id) "
                    "VALUES (%s, 'warehouse', 'store', "
                    "(SELECT id FROM warehouses WHERE code = 'STORE'), %s, "
                    "'transfer', %s, %s, %s)",
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
