"""Transfer repository for database operations on transfers and transfer_items."""

from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

import mysql.connector

from backend.database import Database
from backend.modules.inventory.transfer_model import Transfer, TransferItem
from backend.shared.database import db_cursor


class TransferRepository:
    """Repository for stock transfer database operations.

    Creating a transfer records intent only. Completing a transfer runs in
    a single transaction that validates source stock, decrements the source
    warehouse row, increments the destination warehouse row, and logs stock
    movements for both sides so every change is traceable.
    """

    SORTABLE_COLUMNS = {
        "transfer_number": "t.transfer_number",
        "status": "t.status",
        "created_at": "t.created_at",
        "completed_at": "t.completed_at",
    }

    def __init__(self, database: Database) -> None:
        """Initialize TransferRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def _get_next_transfer_number(self, cursor) -> str:
        """Generate the next sequential transfer number.

        Args:
            cursor: Active database cursor.

        Returns:
            Transfer number string (e.g. TRF-20260815-00001).
        """
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM transfers")
        row = cursor.fetchone()
        next_id = row["next_id"] if isinstance(row, dict) else row[0]
        date_part = datetime.now().strftime("%Y%m%d")
        return f"TRF-{date_part}-{next_id:05d}"

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

    def missing_product_ids(self, product_ids: List[int]) -> List[int]:
        """Return the product ids that do not exist in the products table.

        Args:
            product_ids: Product ids to check.

        Returns:
            List of product ids that have no matching product row.
        """
        if not product_ids:
            return []
        unique_ids = list(dict.fromkeys(product_ids))
        placeholders = ",".join(["%s"] * len(unique_ids))
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    f"SELECT id FROM products WHERE id IN ({placeholders})",
                    tuple(unique_ids),
                )
                existing = {row[0] for row in cursor.fetchall()}
            except mysql.connector.Error:
                raise
        return [pid for pid in unique_ids if pid not in existing]

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def list_transfers(
        self, filters: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List transfers with filters and pagination.

        Args:
            filters: Dictionary with search, status, sort, order, page,
                per_page keys.

        Returns:
            Tuple of (items list, total count).
        """
        search = filters.get("search")
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
            conditions.append("t.transfer_number LIKE %s")
            params.append(f"%{search}%")

        if status:
            conditions.append("t.status = %s")
            params.append(status)

        where_sql = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    f"SELECT COUNT(*) AS total FROM transfers t {where_sql}",
                    tuple(params),
                )
                total = int(cursor.fetchone()["total"])

                query = (
                    "SELECT t.id, t.transfer_number, t.status, t.notes, "
                    "t.created_by, u.full_name AS created_by_name, "
                    "t.completed_by, t.completed_at, t.created_at, "
                    "w_s.name AS source_name, w_d.name AS destination_name, "
                    "COUNT(ti.id) AS item_count, "
                    "COALESCE(SUM(ti.quantity), 0) AS total_quantity "
                    "FROM transfers t "
                    "JOIN users u ON u.id = t.created_by "
                    "JOIN warehouses w_s ON w_s.id = t.source_warehouse_id "
                    "JOIN warehouses w_d ON w_d.id = t.destination_warehouse_id "
                    "LEFT JOIN transfer_items ti ON ti.transfer_id = t.id "
                    f"{where_sql} "
                    "GROUP BY t.id, t.transfer_number, t.status, t.notes, "
                    "t.created_by, u.full_name, t.completed_by, t.completed_at, "
                    "t.created_at, w_s.name, w_d.name "
                    f"ORDER BY {sort_column} {order_sql} "
                    "LIMIT %s OFFSET %s"
                )
                params.extend([per_page, offset])
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                for row in rows:
                    row["item_count"] = int(row["item_count"])
                    row["total_quantity"] = int(row["total_quantity"])
                return rows, total
            except mysql.connector.Error:
                raise

    def get_with_items(self, transfer_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a transfer with its items joined with product names.

        Args:
            transfer_id: The unique identifier of the transfer.

        Returns:
            Dictionary with transfer header and items, or None.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT t.id, t.transfer_number, t.source_warehouse_id, "
                    "t.destination_warehouse_id, t.status, t.created_by, "
                    "u.full_name AS created_by_name, t.completed_by, "
                    "t.completed_at, t.notes, t.created_at, "
                    "w_s.name AS source_name, w_d.name AS destination_name "
                    "FROM transfers t "
                    "JOIN users u ON u.id = t.created_by "
                    "JOIN warehouses w_s ON w_s.id = t.source_warehouse_id "
                    "JOIN warehouses w_d ON w_d.id = t.destination_warehouse_id "
                    "WHERE t.id = %s",
                    (transfer_id,),
                )
                row = cursor.fetchone()
                if not row:
                    return None

                cursor.execute(
                    "SELECT ti.id, ti.transfer_id, ti.product_id, ti.quantity, "
                    "ti.cost_price, p.name AS product_name, p.barcode AS product_barcode "
                    "FROM transfer_items ti "
                    "JOIN products p ON p.id = ti.product_id "
                    "WHERE ti.transfer_id = %s "
                    "ORDER BY p.name ASC",
                    (transfer_id,),
                )
                items = cursor.fetchall()
                for item in items:
                    item["quantity"] = int(item["quantity"])
                    item["cost_price"] = float(item["cost_price"])

                row["items"] = items
                return row
            except mysql.connector.Error:
                raise

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create(self, transfer: Transfer) -> Transfer:
        """Create a pending transfer and its items in one transaction.

        Args:
            transfer: Transfer instance without an id yet.

        Returns:
            The created Transfer instance with its id and number.

        Raises:
            mysql.connector.Error: If the database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                transfer_number = self._get_next_transfer_number(cursor)
                cursor.execute(
                    "INSERT INTO transfers "
                    "(transfer_number, source_warehouse_id, destination_warehouse_id, "
                    "status, created_by, notes) "
                    "VALUES (%s, %s, %s, 'pending', %s, %s)",
                    (
                        transfer_number,
                        transfer.source_warehouse_id,
                        transfer.destination_warehouse_id,
                        transfer.created_by,
                        transfer.notes,
                    ),
                )
                transfer.id = cursor.lastrowid
                transfer.transfer_number = transfer_number
                transfer.status = "pending"

                if transfer.items:
                    cursor.executemany(
                        "INSERT INTO transfer_items "
                        "(transfer_id, product_id, quantity, cost_price) "
                        "VALUES (%s, %s, %s, %s)",
                        [
                            (
                                transfer.id,
                                item.product_id,
                                item.quantity,
                                item.cost_price,
                            )
                            for item in transfer.items
                        ],
                    )

                conn.commit()
                return transfer
            except Exception:
                conn.rollback()
                raise

    def complete(self, transfer_id: int, user_id: Optional[int]) -> Transfer:
        """Complete a pending transfer applying the stock movement.

        Validates and locks source stock for every item, decrements the
        source warehouse row, increments the destination warehouse row,
        and logs 'transfer' stock movements for both sides. Runs in a
        single transaction with commit on success and rollback on error.

        Args:
            transfer_id: The unique identifier of the transfer.
            user_id: ID of the user completing the transfer.

        Returns:
            The completed Transfer instance.

        Raises:
            ValueError: If the transfer is not pending or source stock is
                insufficient.
            mysql.connector.Error: If the database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT t.id, t.transfer_number, t.source_warehouse_id, "
                    "t.destination_warehouse_id, t.status, "
                    "w_s.code AS source_code, w_d.code AS destination_code "
                    "FROM transfers t "
                    "JOIN warehouses w_s ON w_s.id = t.source_warehouse_id "
                    "JOIN warehouses w_d ON w_d.id = t.destination_warehouse_id "
                    "WHERE t.id = %s FOR UPDATE",
                    (transfer_id,),
                )
                transfer = cursor.fetchone()
                if transfer is None:
                    raise ValueError("Transfer not found")
                if transfer["status"] != "pending":
                    raise ValueError("Only pending transfers can be completed")

                source_warehouse_id = int(transfer["source_warehouse_id"])
                destination_warehouse_id = int(transfer["destination_warehouse_id"])
                source_code = transfer["source_code"]
                destination_code = transfer["destination_code"]
                from_location = "store" if source_code == "STORE" else "warehouse"
                to_location = "store" if destination_code == "STORE" else "warehouse"

                cursor.execute(
                    "SELECT id, product_id, quantity, cost_price "
                    "FROM transfer_items WHERE transfer_id = %s FOR UPDATE",
                    (transfer_id,),
                )
                items = cursor.fetchall()
                if not items:
                    raise ValueError("Transfer has no items to complete")

                for item in items:
                    product_id = int(item["product_id"])
                    quantity = int(item["quantity"])

                    cursor.execute(
                        "SELECT id, quantity FROM inventory "
                        "WHERE product_id = %s AND warehouse_id = %s FOR UPDATE",
                        (product_id, source_warehouse_id),
                    )
                    source_row = cursor.fetchone()
                    if source_row is None:
                        raise ValueError(
                            f"No source stock record for product {product_id}"
                        )
                    available = int(source_row["quantity"])
                    if available < quantity:
                        raise ValueError(
                            f"Insufficient stock to complete transfer: "
                            f"available {available}, requested {quantity} for product {product_id}"
                        )

                    cursor.execute(
                        "UPDATE inventory SET quantity = quantity - %s "
                        "WHERE id = %s",
                        (quantity, source_row["id"]),
                    )

                    cursor.execute(
                        "INSERT INTO inventory "
                        "(product_id, location, warehouse_id, quantity) "
                        "VALUES (%s, %s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE quantity = quantity + %s",
                        (
                            product_id,
                            to_location,
                            destination_warehouse_id,
                            quantity,
                            quantity,
                        ),
                    )

                    cursor.execute(
                        "INSERT INTO stock_movements "
                        "(product_id, from_location, to_location, warehouse_id, "
                        "quantity, movement_type, reference, notes, user_id) "
                        "VALUES (%s, %s, %s, %s, %s, 'transfer', %s, 'Transfer out', %s)",
                        (
                            product_id,
                            from_location,
                            None,
                            source_warehouse_id,
                            quantity,
                            transfer["transfer_number"],
                            user_id,
                        ),
                    )
                    cursor.execute(
                        "INSERT INTO stock_movements "
                        "(product_id, from_location, to_location, warehouse_id, "
                        "quantity, movement_type, reference, notes, user_id) "
                        "VALUES (%s, %s, %s, %s, %s, 'transfer', %s, 'Transfer in', %s)",
                        (
                            product_id,
                            None,
                            to_location,
                            destination_warehouse_id,
                            quantity,
                            transfer["transfer_number"],
                            user_id,
                        ),
                    )

                    self._sync_product_total(cursor, product_id)

                cursor.execute(
                    "UPDATE transfers SET status = 'completed', "
                    "completed_by = %s, completed_at = CURRENT_TIMESTAMP "
                    "WHERE id = %s",
                    (user_id, transfer_id),
                )

                conn.commit()
                return self.get_transfer_by_id(transfer_id)
            except Exception:
                conn.rollback()
                raise

    def cancel(self, transfer_id: int) -> Optional[Transfer]:
        """Cancel a pending transfer.

        Args:
            transfer_id: The unique identifier of the transfer.

        Returns:
            The cancelled Transfer instance.

        Raises:
            ValueError: If the transfer is not pending.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    "SELECT id, status FROM transfers WHERE id = %s FOR UPDATE",
                    (transfer_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    return None
                if row[1] != "pending":
                    raise ValueError("Only pending transfers can be cancelled")
                cursor.execute(
                    "UPDATE transfers SET status = 'cancelled' WHERE id = %s",
                    (transfer_id,),
                )
                conn.commit()
                return self.get_transfer_by_id(transfer_id)
            except Exception:
                conn.rollback()
                raise

    def get_transfer_by_id(self, transfer_id: int) -> Optional[Transfer]:
        """Retrieve a transfer as a Transfer model instance.

        Args:
            transfer_id: The unique identifier of the transfer.

        Returns:
            Transfer instance if found, None otherwise.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT t.id, t.transfer_number, t.source_warehouse_id, "
                    "t.destination_warehouse_id, t.status, t.created_by, "
                    "u.full_name AS created_by_name, t.completed_by, "
                    "t.completed_at, t.notes, t.created_at, "
                    "w_s.name AS source_name, w_d.name AS destination_name "
                    "FROM transfers t "
                    "JOIN users u ON u.id = t.created_by "
                    "JOIN warehouses w_s ON w_s.id = t.source_warehouse_id "
                    "JOIN warehouses w_d ON w_d.id = t.destination_warehouse_id "
                    "WHERE t.id = %s",
                    (transfer_id,),
                )
                row = cursor.fetchone()
                if not row:
                    return None

                cursor.execute(
                    "SELECT id, transfer_id, product_id, quantity, cost_price "
                    "FROM transfer_items WHERE transfer_id = %s",
                    (transfer_id,),
                )
                items = [
                    TransferItem(
                        id=item["id"],
                        transfer_id=item["transfer_id"],
                        product_id=item["product_id"],
                        quantity=item["quantity"],
                        cost_price=item["cost_price"],
                    )
                    for item in cursor.fetchall()
                ]

                return Transfer.from_dict({
                    **row,
                    "items": [item.to_dict() for item in items],
                })
            except mysql.connector.Error:
                raise
