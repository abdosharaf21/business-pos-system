"""Notification repository for database operations on notifications."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import mysql.connector

from backend.database import Database
from backend.modules.notifications.model import Notification
from backend.shared.expiration import normalize_expiration_date
from backend.shared.database import db_cursor


class NotificationRepository:
    """Repository for notification database operations.

    Generates notifications from live inventory and expiration data,
    persists them without duplicates, tracks read state, and reads
    the list joined with current product context. Uses parameterized
    queries and a shared connection pool.
    """

    def __init__(self, database: Database) -> None:
        """Initialize NotificationRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    # ------------------------------------------------------------------
    # Alert source data (used by the service to generate notifications)
    # ------------------------------------------------------------------

    def get_products_with_stock(
        self,
    ) -> List[Dict[str, Any]]:
        """Retrieve active products with current stock and minimum level.

        Returns:
            List of dicts with id, name, barcode, sku, total quantity,
            and minimum_stock for every active product.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT p.id, p.name, p.barcode, p.sku, p.minimum_stock, "
                    "COALESCE(wh.quantity, 0) + COALESCE(st.quantity, 0) "
                    "AS total_quantity "
                    "FROM products p "
                    "LEFT JOIN inventory wh ON wh.product_id = p.id "
                    "AND wh.location = 'warehouse' "
                    "LEFT JOIN inventory st ON st.product_id = p.id "
                    "AND st.location = 'store' "
                    "WHERE p.status = 'active' "
                    "ORDER BY p.name ASC"
                )
                return cursor.fetchall()
            except mysql.connector.Error:
                raise

    def get_products_with_expiration(
        self,
    ) -> List[Dict[str, Any]]:
        """Retrieve active products with their oldest batch expiration.

        Returns:
            List of dicts with id, name, barcode, sku, total quantity,
            and the oldest expiration_date per product.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT p.id, p.name, p.barcode, p.sku, "
                    "COALESCE(wh.quantity, 0) + COALESCE(st.quantity, 0) "
                    "AS total_quantity, e.expiration_date "
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
                    "WHERE p.status = 'active' AND e.expiration_date IS NOT NULL "
                    "ORDER BY p.name ASC"
                )
                return cursor.fetchall()
            except mysql.connector.Error:
                raise

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def upsert_notification(
        self, product_id: int, notification_type: str, priority: str
    ) -> None:
        """Insert a notification or refresh an existing one in place.

        Uses the unique (product_id, notification_type) key so each
        product/type combination produces exactly one notification.
        Existing rows keep their id, read state, and original created_at.

        Args:
            product_id: ID of the related product.
            notification_type: One of the Notification.TYPE_* constants.
            priority: One of the Notification.PRIORITY_* constants.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    "INSERT INTO notifications "
                    "(product_id, notification_type, priority) "
                    "VALUES (%s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE priority = VALUES(priority)",
                    (product_id, notification_type, priority),
                )
                conn.commit()
            except mysql.connector.Error:
                conn.rollback()
                raise

    def get_existing_keys(self) -> List[Tuple[int, str]]:
        """Return all (product_id, notification_type) pairs currently stored.

        Returns:
            List of tuples for existing notifications.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    "SELECT product_id, notification_type FROM notifications"
                )
                return [tuple(row) for row in cursor.fetchall()]
            except mysql.connector.Error:
                raise

    def delete_stale_notifications(self, keys: List[Tuple[int, str]]) -> None:
        """Delete notifications whose alert no longer applies.

        Args:
            keys: List of (product_id, notification_type) pairs to remove.
        """
        if not keys:
            return
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.executemany(
                    "DELETE FROM notifications "
                    "WHERE product_id = %s AND notification_type = %s",
                    keys,
                )
                conn.commit()
            except mysql.connector.Error:
                conn.rollback()
                raise

    # ------------------------------------------------------------------
    # Read / read-state operations
    # ------------------------------------------------------------------

    def get_all_notifications(
        self, limit: Optional[int] = None
    ) -> List[Notification]:
        """Retrieve notifications joined with current product context.

        Newest notifications first.

        Args:
            limit: Optional maximum number of notifications to return.

        Returns:
            List of Notification instances.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                query = (
                    "SELECT n.id, n.product_id, n.notification_type, "
                    "n.priority, n.is_read, n.created_at, "
                    "p.name AS product_name, p.barcode, p.sku, "
                    "COALESCE(wh.quantity, 0) + COALESCE(st.quantity, 0) "
                    "AS total_quantity, e.expiration_date "
                    "FROM notifications n "
                    "JOIN products p ON p.id = n.product_id "
                    "LEFT JOIN inventory wh ON wh.product_id = n.product_id "
                    "AND wh.location = 'warehouse' "
                    "LEFT JOIN inventory st ON st.product_id = n.product_id "
                    "AND st.location = 'store' "
                    "LEFT JOIN ("
                    "SELECT product_id, MIN(expiration_date) AS expiration_date "
                    "FROM purchase_items WHERE expiration_date IS NOT NULL "
                    "GROUP BY product_id"
                    ") e ON e.product_id = n.product_id "
                    "ORDER BY n.created_at DESC, n.id DESC"
                )
                if limit is not None:
                    query += " LIMIT %s"
                    cursor.execute(query, (int(limit),))
                else:
                    cursor.execute(query)
                rows = cursor.fetchall()
            except mysql.connector.Error:
                raise

        return [self._row_to_notification(row) for row in rows]

    @staticmethod
    def _row_to_notification(row: Dict[str, Any]) -> Notification:
        """Convert a joined database row to a Notification instance.

        Args:
            row: Database row as a dictionary.

        Returns:
            Notification instance populated from the row.
        """
        return Notification(
            id=row["id"],
            product_id=row["product_id"],
            notification_type=row["notification_type"],
            priority=row["priority"],
            is_read=bool(row["is_read"]),
            created_at=row["created_at"],
            product_name=row.get("product_name"),
            barcode=row.get("barcode"),
            sku=row.get("sku"),
            quantity=row.get("total_quantity"),
            expiration_date=normalize_expiration_date(row.get("expiration_date")),
        )

    def get_unread_count(self) -> int:
        """Count unread notifications.

        Returns:
            Number of notifications where is_read is false.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM notifications WHERE is_read = 0"
                )
                return int(cursor.fetchone()[0])
            except mysql.connector.Error:
                raise

    def mark_as_read(self, notification_id: int) -> bool:
        """Mark a single notification as read.

        Args:
            notification_id: ID of the notification to mark read.

        Returns:
            True if a notification was updated, False otherwise.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    "UPDATE notifications SET is_read = 1 WHERE id = %s",
                    (notification_id,),
                )
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise

    def mark_all_as_read(self) -> int:
        """Mark every notification as read.

        Returns:
            Number of notifications updated.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute("UPDATE notifications SET is_read = 1")
                conn.commit()
                return cursor.rowcount
            except mysql.connector.Error:
                conn.rollback()
                raise
