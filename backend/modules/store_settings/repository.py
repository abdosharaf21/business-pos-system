"""Store settings repository for database operations."""

from datetime import datetime
from typing import Any, Dict, Optional

import mysql.connector

from backend.database import Database


class StoreSettingsRepository:
    """Repository for the single-row store settings table.

    Reads and updates the business configuration row. Always operates
    on the single record (id = 1) so only one row can ever exist.
    """

    def __init__(self, database: Database) -> None:
        """Initialize StoreSettingsRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def get_settings(self) -> Optional[Dict[str, Any]]:
        """Retrieve the single store settings row.

        Returns:
            Dictionary with all settings fields, or None when no row
            exists yet.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT id, store_name, owner_name, phone, email, address, "
                    "website, tax_number, currency, receipt_footer, logo_path, "
                    "login_background_path, login_logo_path, login_title, "
                    "login_subtitle, created_at, updated_at "
                    "FROM store_settings "
                    "ORDER BY id ASC LIMIT 1"
                )
                row = cursor.fetchone()
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

        if row is None:
            return None

        row["created_at"] = self._to_iso(row["created_at"])
        row["updated_at"] = self._to_iso(row["updated_at"])
        return row

    def upsert_settings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update the single store settings row.

        The first write creates the row (id 1); subsequent writes update
        it in place, so only one record can ever exist.

        Args:
            data: Dictionary with validated settings fields.

        Returns:
            Dictionary with the persisted settings fields.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO store_settings "
                    "(id, store_name, owner_name, phone, email, address, "
                    "website, tax_number, currency, receipt_footer, logo_path, "
                    "login_background_path, login_logo_path, login_title, "
                    "login_subtitle) "
                    "VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE "
                    "store_name = VALUES(store_name), "
                    "owner_name = VALUES(owner_name), "
                    "phone = VALUES(phone), "
                    "email = VALUES(email), "
                    "address = VALUES(address), "
                    "website = VALUES(website), "
                    "tax_number = VALUES(tax_number), "
                    "currency = VALUES(currency), "
                    "receipt_footer = VALUES(receipt_footer), "
                    "logo_path = VALUES(logo_path), "
                    "login_background_path = VALUES(login_background_path), "
                    "login_logo_path = VALUES(login_logo_path), "
                    "login_title = VALUES(login_title), "
                    "login_subtitle = VALUES(login_subtitle)",
                    (
                        data["store_name"],
                        data["owner_name"],
                        data["phone"],
                        data["email"],
                        data["address"],
                        data["website"],
                        data["tax_number"],
                        data["currency"],
                        data["receipt_footer"],
                        data.get("logo_path", ""),
                        data.get("login_background_path", ""),
                        data.get("login_logo_path", ""),
                        data.get("login_title", ""),
                        data.get("login_subtitle", ""),
                    ),
                )
                conn.commit()
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

        return self.get_settings()

    @staticmethod
    def _to_iso(value: Any) -> str:
        """Convert a DB timestamp to an ISO string.

        Args:
            value: A datetime object or string.

        Returns:
            ISO formatted string.
        """
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)
