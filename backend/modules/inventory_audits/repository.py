"""Inventory audit repository for database operations on audit tables."""

from typing import Optional, List, Dict, Any, Tuple

import mysql.connector

from backend.database import Database
from backend.modules.inventory_audits.model import InventoryAudit


class InventoryAuditRepository:
    """Repository for inventory audit database operations.

    Handles audit CRUD, per-location product snapshots, counted quantity
    updates, and the completion transaction that applies adjustments to
    the inventory tables while logging stock movements. All multi-statement
    operations run in a single transaction with commit on success and
    rollback on error.
    """

    SORTABLE_COLUMNS = {
        "name": "a.name",
        "location": "a.location",
        "status": "a.status",
        "created_by_name": "u.full_name",
        "total_items": "total_items",
        "counted_items": "counted_items",
        "adjusted_items": "adjusted_items",
        "total_difference": "total_difference",
        "started_at": "a.started_at",
        "completed_at": "a.completed_at",
        "created_at": "a.created_at",
    }

    MOVEMENT_TYPE = "adjustment"
    MOVEMENT_NOTES = "Inventory Audit"

    def __init__(self, database: Database) -> None:
        """Initialize InventoryAuditRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def get_products_for_audit(self, location: str) -> List[Dict[str, Any]]:
        """Retrieve active products with their stock at a location.

        Args:
            location: Location to snapshot (warehouse or store).

        Returns:
            List of product dictionaries with product_id, product_name,
            barcode, and system_quantity for the location.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT p.id AS product_id, p.name AS product_name, "
                    "p.barcode, COALESCE(i.bucket_quantity, 0) AS system_quantity "
                    "FROM products p "
                    "LEFT JOIN ("
                    "SELECT product_id, SUM(quantity) AS bucket_quantity "
                    "FROM inventory WHERE location = %s GROUP BY product_id"
                    ") i ON i.product_id = p.id "
                    "WHERE p.status = 'active' "
                    "ORDER BY p.name ASC",
                    (location,),
                )
                rows = cursor.fetchall()
                for row in rows:
                    row["system_quantity"] = int(row["system_quantity"])
                return rows
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def _row_to_audit(self, row: Dict[str, Any]) -> InventoryAudit:
        """Convert a database row dictionary to an InventoryAudit instance.

        Args:
            row: Database row as a dictionary.

        Returns:
            InventoryAudit instance populated from the row data.
        """
        return InventoryAudit.from_dict(row)

    def list_audits(self, filters: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], int]:
        """List audits with filters, sorting, and pagination.

        Args:
            filters: Dictionary with search, location, status, sort, order,
                page, and per_page keys.

        Returns:
            Tuple of (items list, total count).

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        search = filters.get("search")
        location = filters.get("location")
        status = filters.get("status")
        sort = filters.get("sort", "created_at")
        order = filters.get("order", "desc")
        page = int(filters.get("page", 1))
        per_page = int(filters.get("per_page", 20))

        sort_column = self.SORTABLE_COLUMNS.get(
            sort, self.SORTABLE_COLUMNS["created_at"]
        )
        order_sql = "ASC" if order == "asc" else "DESC"
        offset = (page - 1) * per_page

        conditions: List[str] = []
        params: List[Any] = []

        if search:
            conditions.append("a.name LIKE %s")
            params.append(f"%{search}%")

        if location:
            conditions.append("a.location = %s")
            params.append(location)

        if status:
            conditions.append("a.status = %s")
            params.append(status)

        where_sql = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    f"SELECT COUNT(*) AS total FROM inventory_audits a {where_sql}",
                    tuple(params),
                )
                total = int(cursor.fetchone()["total"])

                query = (
                    "SELECT a.id, a.name, a.location, a.status, a.created_by, "
                    "u.full_name AS created_by_name, "
                    "a.started_at, a.completed_at, a.created_at, "
                    "COUNT(ai.id) AS total_items, "
                    "COALESCE(SUM(ai.counted_quantity IS NOT NULL), 0) "
                    "AS counted_items, "
                    "COALESCE(SUM(ai.difference <> 0), 0) AS adjusted_items, "
                    "COALESCE(SUM(ai.difference), 0) AS total_difference "
                    "FROM inventory_audits a "
                    "JOIN users u ON u.id = a.created_by "
                    "LEFT JOIN inventory_audit_items ai ON ai.audit_id = a.id "
                    f"{where_sql} "
                    "GROUP BY a.id, a.name, a.location, a.status, a.created_by, "
                    "u.full_name, a.started_at, a.completed_at, a.created_at "
                    f"ORDER BY {sort_column} {order_sql} "
                    "LIMIT %s OFFSET %s"
                )
                params.extend([per_page, offset])
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                for row in rows:
                    row["total_items"] = int(row["total_items"])
                    row["counted_items"] = int(row["counted_items"])
                    row["adjusted_items"] = int(row["adjusted_items"])
                    row["total_difference"] = int(row["total_difference"])
                return rows, total
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_audit(self, audit_id: int) -> Optional[InventoryAudit]:
        """Retrieve a single audit with its aggregate stats.

        Args:
            audit_id: The unique identifier of the audit.

        Returns:
            InventoryAudit instance or None if not found.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT a.id, a.name, a.location, a.status, a.created_by, "
                    "u.full_name AS created_by_name, "
                    "a.started_at, a.completed_at, a.created_at, "
                    "COUNT(ai.id) AS total_items, "
                    "COALESCE(SUM(ai.counted_quantity IS NOT NULL), 0) "
                    "AS counted_items, "
                    "COALESCE(SUM(ai.difference <> 0), 0) AS adjusted_items, "
                    "COALESCE(SUM(ai.difference), 0) AS total_difference "
                    "FROM inventory_audits a "
                    "JOIN users u ON u.id = a.created_by "
                    "LEFT JOIN inventory_audit_items ai ON ai.audit_id = a.id "
                    "WHERE a.id = %s "
                    "GROUP BY a.id, a.name, a.location, a.status, a.created_by, "
                    "u.full_name, a.started_at, a.completed_at, a.created_at",
                    (audit_id,),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                row["total_items"] = int(row["total_items"])
                row["counted_items"] = int(row["counted_items"])
                row["adjusted_items"] = int(row["adjusted_items"])
                row["total_difference"] = int(row["total_difference"])
                return self._row_to_audit(row)
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_items(self, audit_id: int) -> List[Dict[str, Any]]:
        """Retrieve the items of an audit joined with product names.

        Args:
            audit_id: The unique identifier of the audit.

        Returns:
            List of audit item dictionaries ordered by product name.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT ai.id, ai.audit_id, ai.product_id, "
                    "ai.system_quantity, ai.counted_quantity, "
                    "ai.difference, ai.notes, p.name AS product_name, "
                    "p.barcode "
                    "FROM inventory_audit_items ai "
                    "JOIN products p ON p.id = ai.product_id "
                    "WHERE ai.audit_id = %s "
                    "ORDER BY p.name ASC",
                    (audit_id,),
                )
                rows = cursor.fetchall()
                for row in rows:
                    row["system_quantity"] = int(row["system_quantity"])
                    row["counted_quantity"] = (
                        int(row["counted_quantity"])
                        if row["counted_quantity"] is not None
                        else None
                    )
                    row["difference"] = int(row["difference"])
                return rows
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create_with_items(
        self, audit: InventoryAudit, products: List[Dict[str, Any]]
    ) -> InventoryAudit:
        """Create an audit and its snapshot items in one transaction.

        Args:
            audit: InventoryAudit instance without an id yet.
            products: List of product dictionaries from get_products_for_audit.

        Returns:
            The created InventoryAudit instance with its id.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO inventory_audits "
                    "(name, location, status, created_by) "
                    "VALUES (%s, %s, 'open', %s)",
                    (audit.name, audit.location, audit.created_by),
                )
                audit.id = cursor.lastrowid

                if products:
                    cursor.executemany(
                        "INSERT INTO inventory_audit_items "
                        "(audit_id, product_id, system_quantity, counted_quantity, "
                        "difference) "
                        "VALUES (%s, %s, %s, NULL, 0)",
                        [
                            (
                                audit.id,
                                product["product_id"],
                                product["system_quantity"],
                            )
                            for product in products
                        ],
                    )

                conn.commit()
                return audit
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def update_audit(self, audit_id: int, fields: Dict[str, Any]) -> None:
        """Update the name and/or status of an audit.

        Args:
            audit_id: The unique identifier of the audit.
            fields: Dictionary with optional name and status keys.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        updates: List[str] = []
        params: List[Any] = []

        if "name" in fields:
            updates.append("name = %s")
            params.append(fields["name"])

        if "status" in fields:
            updates.append("status = %s")
            params.append(fields["status"])

        if not updates:
            return

        params.append(audit_id)

        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    f"UPDATE inventory_audits SET {', '.join(updates)} "
                    "WHERE id = %s",
                    tuple(params),
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def update_items(
        self, audit_id: int, items: Dict[int, Dict[str, Any]]
    ) -> None:
        """Update counted quantities and notes for audit items.

        Args:
            audit_id: The unique identifier of the audit.
            items: Dictionary mapping product_id to validated item data.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                for item in items.values():
                    cursor.execute(
                        "UPDATE inventory_audit_items "
                        "SET counted_quantity = %s, "
                        "difference = %s - system_quantity, "
                        "notes = %s "
                        "WHERE audit_id = %s AND product_id = %s",
                        (
                            item["counted_quantity"],
                            item["counted_quantity"],
                            item["notes"],
                            audit_id,
                            item["product_id"],
                        ),
                    )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()

    @staticmethod
    def _movement_locations(difference: int, location: str) -> Tuple[Optional[str], Optional[str]]:
        """Determine from/to locations for an adjustment movement.

        Args:
            difference: Signed quantity difference (counted - system).
            location: Location the audit applies to.

        Returns:
            Tuple of (from_location, to_location).
        """
        if difference >= 0:
            return None, location
        return location, None

    def complete_audit(self, audit_id: int, user_id: Optional[int]) -> int:
        """Complete an open audit applying adjustments to inventory.

        Locks the audit and its items, then for every item with a non-zero
        difference writes the counted quantity into the inventory row for
        the audit location and logs a stock movement of type 'adjustment'
        referencing the audit id. Syncs the denormalized products.quantity
        total for every adjusted product.

        Args:
            audit_id: The unique identifier of the audit.
            user_id: ID of the user completing the audit.

        Returns:
            The number of items that were adjusted.

        Raises:
            ValueError: If the audit is not open.
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT id, location, status FROM inventory_audits "
                    "WHERE id = %s FOR UPDATE",
                    (audit_id,),
                )
                audit = cursor.fetchone()
                if audit is None:
                    raise ValueError("Audit not found")
                if audit["status"] != "open":
                    raise ValueError("Only open audits can be completed")

                cursor.execute(
                    "SELECT id, product_id, system_quantity, counted_quantity, "
                    "difference FROM inventory_audit_items "
                    "WHERE audit_id = %s FOR UPDATE",
                    (audit_id,),
                )
                items = cursor.fetchall()

                adjusted_items = 0
                for item in items:
                    difference = int(item["difference"])
                    counted = item["counted_quantity"]
                    if counted is None or difference == 0:
                        continue

                    location = audit["location"]
                    cursor.execute(
                        "INSERT INTO inventory "
                        "(product_id, location, warehouse_id, quantity) "
                        "VALUES (%s, %s, "
                        "(SELECT id FROM warehouses WHERE code = "
                        "IF(%s = 'store', 'STORE', 'WH-MAIN')), %s) "
                        "ON DUPLICATE KEY UPDATE quantity = VALUES(quantity)",
                        (
                            item["product_id"],
                            location,
                            location,
                            counted,
                        ),
                    )

                    from_location, to_location = self._movement_locations(
                        difference, location
                    )

                    cursor.execute(
                        "INSERT INTO stock_movements "
                        "(product_id, from_location, to_location, warehouse_id, "
                        "quantity, movement_type, reference, notes, user_id) "
                        "VALUES (%s, %s, %s, "
                        "(SELECT id FROM warehouses WHERE code = "
                        "IF(%s = 'store', 'STORE', 'WH-MAIN')), "
                        "%s, %s, %s, %s, %s)",
                        (
                            item["product_id"],
                            from_location,
                            to_location,
                            location,
                            abs(difference),
                            self.MOVEMENT_TYPE,
                            str(audit_id),
                            self.MOVEMENT_NOTES,
                            user_id,
                        ),
                    )

                    cursor.execute(
                        "UPDATE products p SET p.quantity = COALESCE(("
                        "SELECT SUM(i.quantity) FROM inventory i "
                        "WHERE i.product_id = %s), 0) "
                        "WHERE p.id = %s",
                        (item["product_id"], item["product_id"]),
                    )
                    adjusted_items += 1

                cursor.execute(
                    "UPDATE inventory_audits SET status = 'completed', "
                    "completed_at = CURRENT_TIMESTAMP WHERE id = %s",
                    (audit_id,),
                )

                conn.commit()
                return adjusted_items
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def delete_audit(self, audit_id: int) -> None:
        """Delete an audit. Audit items are removed via cascade.

        Args:
            audit_id: The unique identifier of the audit.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "DELETE FROM inventory_audits WHERE id = %s",
                    (audit_id,),
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()

    # ------------------------------------------------------------------
    # Report queries
    # ------------------------------------------------------------------

    def get_report_metrics(self) -> Dict[str, Any]:
        """Get aggregate audit metrics for reports.

        Returns:
            Dictionary with audit counts and adjustment totals.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT "
                    "COUNT(*) AS total_audits, "
                    "COALESCE(SUM(status = 'open'), 0) AS open_audits, "
                    "COALESCE(SUM(status = 'completed'), 0) AS completed_audits, "
                    "COALESCE(SUM(status = 'cancelled'), 0) AS cancelled_audits "
                    "FROM inventory_audits"
                )
                counts = cursor.fetchone()

                cursor.execute(
                    "SELECT "
                    "COALESCE(SUM(ai.difference > 0), 0) AS adjusted_items, "
                    "COALESCE(SUM(ai.difference > 0), 0) AS added_items, "
                    "COALESCE(SUM(ai.difference < 0), 0) AS removed_items, "
                    "COALESCE(SUM(ai.difference), 0) AS net_difference, "
                    "COALESCE(SUM(IF(ai.difference > 0, ai.difference, 0)), 0) "
                    "AS units_added, "
                    "COALESCE(SUM(IF(ai.difference < 0, -ai.difference, 0)), 0) "
                    "AS units_removed "
                    "FROM inventory_audit_items ai "
                    "JOIN inventory_audits a ON a.id = ai.audit_id "
                    "WHERE a.status = 'completed' "
                    "AND ai.counted_quantity IS NOT NULL"
                )
                adjustments = cursor.fetchone()

                return {
                    "total_audits": int(counts["total_audits"]),
                    "open_audits": int(counts["open_audits"]),
                    "completed_audits": int(counts["completed_audits"]),
                    "cancelled_audits": int(counts["cancelled_audits"]),
                    "adjusted_items": int(adjustments["adjusted_items"]),
                    "added_items": int(adjustments["added_items"]),
                    "removed_items": int(adjustments["removed_items"]),
                    "net_difference": int(adjustments["net_difference"]),
                    "units_added": int(adjustments["units_added"]),
                    "units_removed": int(adjustments["units_removed"]),
                }
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_monthly_summary(self, year: int) -> List[Dict[str, Any]]:
        """Get completed audit counts per month for a year.

        Args:
            year: Year to summarize.

        Returns:
            List of month dicts with month, month_name, and audits.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT MONTH(completed_at) AS month, "
                    "COUNT(*) AS audits "
                    "FROM inventory_audits "
                    "WHERE status = 'completed' "
                    "AND YEAR(completed_at) = %s "
                    "GROUP BY MONTH(completed_at) "
                    "ORDER BY month",
                    (year,),
                )
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    month = int(row["month"])
                    result.append({
                        "month": month,
                        "month_name": f"{month:02d}",
                        "audits": int(row["audits"]),
                    })
                return result
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_yearly_summary(self, from_year: int, to_year: int) -> List[Dict[str, Any]]:
        """Get completed audit counts per year across a range.

        Args:
            from_year: First year of the range.
            to_year: Last year of the range.

        Returns:
            List of year dicts with year and audits.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT YEAR(completed_at) AS year, COUNT(*) AS audits "
                    "FROM inventory_audits "
                    "WHERE status = 'completed' "
                    "AND YEAR(completed_at) BETWEEN %s AND %s "
                    "GROUP BY YEAR(completed_at) "
                    "ORDER BY year",
                    (from_year, to_year),
                )
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    result.append({
                        "year": int(row["year"]),
                        "audits": int(row["audits"]),
                    })
                return result
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_largest_shortages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get products with the largest negative differences.

        Args:
            limit: Maximum number of rows to return.

        Returns:
            List of dicts with product, audit name, and difference.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT ai.difference, ai.system_quantity, "
                    "ai.counted_quantity, p.name AS product_name, "
                    "a.name AS audit_name "
                    "FROM inventory_audit_items ai "
                    "JOIN inventory_audits a ON a.id = ai.audit_id "
                    "JOIN products p ON p.id = ai.product_id "
                    "WHERE a.status = 'completed' "
                    "AND ai.counted_quantity IS NOT NULL "
                    "AND ai.difference < 0 "
                    "ORDER BY ai.difference ASC "
                    "LIMIT %s",
                    (limit,),
                )
                rows = cursor.fetchall()
                for row in rows:
                    row["difference"] = int(row["difference"])
                    row["system_quantity"] = int(row["system_quantity"])
                    row["counted_quantity"] = int(row["counted_quantity"])
                return rows
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_largest_overages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get products with the largest positive differences.

        Args:
            limit: Maximum number of rows to return.

        Returns:
            List of dicts with product, audit name, and difference.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT ai.difference, ai.system_quantity, "
                    "ai.counted_quantity, p.name AS product_name, "
                    "a.name AS audit_name "
                    "FROM inventory_audit_items ai "
                    "JOIN inventory_audits a ON a.id = ai.audit_id "
                    "JOIN products p ON p.id = ai.product_id "
                    "WHERE a.status = 'completed' "
                    "AND ai.counted_quantity IS NOT NULL "
                    "AND ai.difference > 0 "
                    "ORDER BY ai.difference DESC "
                    "LIMIT %s",
                    (limit,),
                )
                rows = cursor.fetchall()
                for row in rows:
                    row["difference"] = int(row["difference"])
                    row["system_quantity"] = int(row["system_quantity"])
                    row["counted_quantity"] = int(row["counted_quantity"])
                return rows
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()
