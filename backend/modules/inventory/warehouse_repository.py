"""Warehouse repository for database operations on warehouses and stock."""

from typing import Optional, List, Dict, Any

import mysql.connector

from backend.database import Database
from backend.shared.database import db_cursor


class WarehouseRepository:
    """Repository for warehouse database operations.

    Handles warehouse CRUD, per-warehouse stock queries, and built-in
    warehouse resolution using parameterized queries and a shared
    connection pool.
    """

    BUILTIN_CODE_BY_LOCATION = {"warehouse": "WH-MAIN", "store": "STORE"}

    def __init__(self, database: Database) -> None:
        """Initialize WarehouseRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def list_warehouses(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """Retrieve all warehouses with their total stock.

        Rows whose warehouse_id predates migration 014 are attributed to
        the matching built-in warehouse by location so stock is never
        hidden from the totals.

        Args:
            active_only: When True, only return active warehouses.

        Returns:
            List of warehouse dictionaries with stock_total.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                query = (
                    "SELECT w.id, w.name, w.code, w.address, w.manager_name, "
                    "w.phone, w.status, w.created_at, w.updated_at, "
                    "COALESCE(SUM(i.quantity), 0) AS stock_total "
                    "FROM warehouses w "
                    "LEFT JOIN inventory i ON i.warehouse_id = w.id "
                    "OR (w.code IN ('WH-MAIN', 'STORE') "
                    "AND i.warehouse_id IS NULL AND i.location = "
                    "CASE w.code WHEN 'STORE' THEN 'store' ELSE 'warehouse' END) "
                )
                params: tuple = ()
                if active_only:
                    query += "WHERE w.status = 'active' "
                query += "GROUP BY w.id ORDER BY w.name ASC"
                cursor.execute(query, params)
                rows = cursor.fetchall()
                for row in rows:
                    row["stock_total"] = int(row["stock_total"])
                return rows
            except mysql.connector.Error:
                raise

    def get_by_id(self, warehouse_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a warehouse by its unique identifier.

        Args:
            warehouse_id: The unique identifier of the warehouse.

        Returns:
            Warehouse dictionary if found, None otherwise.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT w.id, w.name, w.code, w.address, w.manager_name, "
                    "w.phone, w.status, w.created_at, w.updated_at, "
                    "COALESCE(SUM(i.quantity), 0) AS stock_total "
                    "FROM warehouses w "
                    "LEFT JOIN inventory i ON i.warehouse_id = w.id "
                    "OR (w.code IN ('WH-MAIN', 'STORE') "
                    "AND i.warehouse_id IS NULL AND i.location = "
                    "CASE w.code WHEN 'STORE' THEN 'store' ELSE 'warehouse' END) "
                    "WHERE w.id = %s "
                    "GROUP BY w.id",
                    (warehouse_id,),
                )
                row = cursor.fetchone()
                if row:
                    row["stock_total"] = int(row["stock_total"])
                return row
            except mysql.connector.Error:
                raise

    def get_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Retrieve a warehouse by its unique code.

        Args:
            code: The unique warehouse code.

        Returns:
            Warehouse dictionary if found, None otherwise.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT id, name, code, address, manager_name, phone, "
                    "status, created_at, updated_at "
                    "FROM warehouses WHERE code = %s",
                    (code,),
                )
                return cursor.fetchone()
            except mysql.connector.Error:
                raise

    def resolve_builtin_id(self, location: str) -> Optional[int]:
        """Resolve the warehouse id for a built-in location.

        Args:
            location: 'warehouse' (WH-MAIN) or 'store' (STORE).

        Returns:
            Warehouse id if found, None if the warehouses table is empty.
        """
        code = self.BUILTIN_CODE_BY_LOCATION.get(location)
        if code is None:
            return None
        row = self.get_by_code(code)
        return row["id"] if row else None

    def get_stock(
        self, warehouse_id: int, search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve the stock of a warehouse for all active products.

        Args:
            warehouse_id: The unique identifier of the warehouse.
            search: Optional search term for product name or barcode.

        Returns:
            List of product dictionaries with per-warehouse quantity.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                query = (
                    "SELECT p.id, p.name, p.barcode, p.sku, p.minimum_stock, "
                    "p.selling_price, p.purchase_price, p.status, "
                    "c.name AS category_name, "
                    "COALESCE(i.quantity, 0) AS quantity "
                    "FROM products p "
                    "LEFT JOIN categories c ON c.id = p.category_id "
                    "LEFT JOIN inventory i ON i.product_id = p.id "
                    "AND i.warehouse_id = %s "
                    "WHERE p.status = 'active' "
                )
                params: list = [warehouse_id]
                if search:
                    query += "AND (p.name LIKE %s OR p.barcode LIKE %s) "
                    params.extend([f"%{search}%", f"%{search}%"])
                query += "ORDER BY p.name ASC"
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                for row in rows:
                    row["quantity"] = int(row["quantity"])
                return rows
            except mysql.connector.Error:
                raise

    def count_active(self) -> int:
        """Count active warehouses.

        Returns:
            Number of active warehouses.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM warehouses WHERE status = 'active'"
                )
                return cursor.fetchone()[0]
            except mysql.connector.Error:
                raise

    def exists_by_name(
        self, name: str, exclude_id: Optional[int] = None
    ) -> bool:
        """Check whether a warehouse name is already taken.

        Args:
            name: Warehouse name to check.
            exclude_id: Optional warehouse id to exclude from the check
                (used when updating).

        Returns:
            True if another warehouse uses the name, False otherwise.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                if exclude_id is not None:
                    cursor.execute(
                        "SELECT COUNT(*) FROM warehouses WHERE name = %s "
                        "AND id <> %s",
                        (name, exclude_id),
                    )
                else:
                    cursor.execute(
                        "SELECT COUNT(*) FROM warehouses WHERE name = %s",
                        (name,),
                    )
                return cursor.fetchone()[0] > 0
            except mysql.connector.Error:
                raise

    def exists_by_code(
        self, code: str, exclude_id: Optional[int] = None
    ) -> bool:
        """Check whether a warehouse code is already taken.

        Args:
            code: Warehouse code to check.
            exclude_id: Optional warehouse id to exclude from the check
                (used when updating).

        Returns:
            True if another warehouse uses the code, False otherwise.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                if exclude_id is not None:
                    cursor.execute(
                        "SELECT COUNT(*) FROM warehouses WHERE code = %s "
                        "AND id <> %s",
                        (code, exclude_id),
                    )
                else:
                    cursor.execute(
                        "SELECT COUNT(*) FROM warehouses WHERE code = %s",
                        (code,),
                    )
                return cursor.fetchone()[0] > 0
            except mysql.connector.Error:
                raise

    def stock_row_count(self, warehouse_id: int) -> int:
        """Count inventory rows pointing at a warehouse.

        Args:
            warehouse_id: The unique identifier of the warehouse.

        Returns:
            Number of inventory rows referencing the warehouse.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM inventory WHERE warehouse_id = %s",
                    (warehouse_id,),
                )
                return cursor.fetchone()[0]
            except mysql.connector.Error:
                raise

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new warehouse.

        Args:
            data: Dictionary with name, code, address, manager_name, phone.

        Returns:
            Dictionary of the created warehouse with its id.

        Raises:
            mysql.connector.Error: If the database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "INSERT INTO warehouses (name, code, address, manager_name, "
                    "phone, status) VALUES (%s, %s, %s, %s, %s, 'active')",
                    (
                        data["name"],
                        data["code"],
                        data.get("address"),
                        data.get("manager_name"),
                        data.get("phone"),
                    ),
                )
                conn.commit()
                return self.get_by_id(cursor.lastrowid)
            except mysql.connector.Error:
                conn.rollback()
                raise

    def update(self, warehouse_id: int, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update editable fields of an existing warehouse.

        Args:
            warehouse_id: The unique identifier of the warehouse.
            fields: Dictionary with optional name, code, address, manager_name,
                phone keys.

        Returns:
            Updated warehouse dictionary if found, None otherwise.

        Raises:
            mysql.connector.Error: If the database operation fails.
        """
        updates: List[str] = []
        params: List[Any] = []

        if "name" in fields:
            updates.append("name = %s")
            params.append(fields["name"])
        if "code" in fields:
            updates.append("code = %s")
            params.append(fields["code"])
        if "address" in fields:
            updates.append("address = %s")
            params.append(fields["address"])
        if "manager_name" in fields:
            updates.append("manager_name = %s")
            params.append(fields["manager_name"])
        if "phone" in fields:
            updates.append("phone = %s")
            params.append(fields["phone"])

        if not updates:
            return self.get_by_id(warehouse_id)

        params.append(warehouse_id)

        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    f"UPDATE warehouses SET {', '.join(updates)} WHERE id = %s",
                    tuple(params),
                )
                conn.commit()
                if cursor.rowcount == 0 and self.get_by_id(warehouse_id) is None:
                    return None
                return self.get_by_id(warehouse_id)
            except mysql.connector.Error:
                conn.rollback()
                raise

    def set_status(
        self, warehouse_id: int, status: str
    ) -> Optional[Dict[str, Any]]:
        """Set the status (active/inactive) of a warehouse.

        Args:
            warehouse_id: The unique identifier of the warehouse.
            status: active or inactive.

        Returns:
            Updated warehouse dictionary if found, None otherwise.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "UPDATE warehouses SET status = %s WHERE id = %s",
                    (status, warehouse_id),
                )
                conn.commit()
                if cursor.rowcount == 0 and self.get_by_id(warehouse_id) is None:
                    return None
                return self.get_by_id(warehouse_id)
            except mysql.connector.Error:
                conn.rollback()
                raise

    def delete(self, warehouse_id: int) -> bool:
        """Delete a warehouse when it has no stock rows.

        Args:
            warehouse_id: The unique identifier of the warehouse.

        Returns:
            True if the warehouse was deleted, False if not found.

        Raises:
            ValueError: If the warehouse still holds stock rows.
            mysql.connector.Error: If the database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM inventory WHERE warehouse_id = %s",
                    (warehouse_id,),
                )
                if cursor.fetchone()[0] > 0:
                    raise ValueError(
                        "Cannot delete a warehouse that holds stock"
                    )
                cursor.execute(
                    "DELETE FROM warehouses WHERE id = %s",
                    (warehouse_id,),
                )
                conn.commit()
                return cursor.rowcount > 0
            except Exception:
                conn.rollback()
                raise
