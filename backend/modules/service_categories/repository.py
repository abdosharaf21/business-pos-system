"""ServiceCategory repository for database operations on the service_categories table."""

from datetime import datetime
from typing import Optional, List

import mysql.connector

from backend.database import Database
from backend.modules.service_categories.model import ServiceCategory
from backend.shared.database import db_cursor


class ServiceCategoryRepository:
    """Repository for service category database operations.

    Handles all CRUD operations for the service_categories table using
    parameterized queries and a shared connection pool.
    """

    def __init__(self, database: Database) -> None:
        """Initialize ServiceCategoryRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def _row_to_category(self, row: tuple) -> ServiceCategory:
        """Convert a database row tuple to a ServiceCategory instance.

        Args:
            row: Database row as a tuple.

        Returns:
            ServiceCategory instance populated from the row data.
        """
        return ServiceCategory(
            id=row[0],
            name=row[1],
            description=row[2],
            created_at=row[3]
        )

    def create(self, category: ServiceCategory) -> ServiceCategory:
        """Insert a new service category record into the database.

        Args:
            category: ServiceCategory instance to insert.

        Returns:
            ServiceCategory instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = """
                    INSERT INTO service_categories (name, description)
                    VALUES (%s, %s)
                """
                cursor.execute(query, (
                    category.name,
                    category.description
                ))
                conn.commit()
                category.id = cursor.lastrowid
                category.created_at = datetime.now()
                return category
            except mysql.connector.Error:
                conn.rollback()
                raise

    def get_by_id(self, category_id: int) -> Optional[ServiceCategory]:
        """Retrieve a service category by its unique identifier.

        Args:
            category_id: The unique identifier of the category.

        Returns:
            ServiceCategory instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "SELECT * FROM service_categories WHERE id = %s"
                cursor.execute(query, (category_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_category(row)
                return None
            except mysql.connector.Error:
                raise

    def get_all(self) -> List[ServiceCategory]:
        """Retrieve all service category records from the database.

        Returns:
            List of ServiceCategory instances.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "SELECT * FROM service_categories ORDER BY created_at DESC"
                cursor.execute(query)
                rows = cursor.fetchall()
                return [self._row_to_category(row) for row in rows]
            except mysql.connector.Error:
                raise

    def update(self, category: ServiceCategory) -> Optional[ServiceCategory]:
        """Update an existing service category record in the database.

        Args:
            category: ServiceCategory instance with updated fields.

        Returns:
            Updated ServiceCategory instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = """
                    UPDATE service_categories
                    SET name = %s, description = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    category.name,
                    category.description,
                    category.id
                ))
                conn.commit()
                if cursor.rowcount > 0:
                    cursor.execute("SELECT * FROM service_categories WHERE id = %s", (category.id,))
                    row = cursor.fetchone()
                    if row:
                        return self._row_to_category(row)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise

    def delete(self, category_id: int) -> bool:
        """Delete a service category record from the database.

        Args:
            category_id: The unique identifier of the category to delete.

        Returns:
            True if the category was deleted, False if not found.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "DELETE FROM service_categories WHERE id = %s"
                cursor.execute(query, (category_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise
