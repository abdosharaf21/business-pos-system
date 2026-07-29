"""Category repository for database operations on the categories table."""

from datetime import datetime
from typing import Optional, List

import mysql.connector

from backend.database import Database
from backend.modules.categories.model import Category


class CategoryRepository:
    """Repository for category database operations.

    Handles all CRUD operations for the categories table using
    parameterized queries and a shared connection pool.
    """

    def __init__(self, database: Database) -> None:
        """Initialize CategoryRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def _row_to_category(self, row: tuple) -> Category:
        """Convert a database row tuple to a Category instance.

        Args:
            row: Database row as a tuple.

        Returns:
            Category instance populated from the row data.
        """
        return Category(
            id=row[0],
            name=row[1],
            description=row[2],
            created_at=row[3],
            updated_at=row[4],
        )

    def create(self, category: Category) -> Category:
        """Insert a new category record into the database.

        Args:
            category: Category instance to insert.

        Returns:
            Category instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    INSERT INTO categories (name, description)
                    VALUES (%s, %s)
                """
                cursor.execute(query, (category.name, category.description))
                conn.commit()
                category.id = cursor.lastrowid
                category.created_at = datetime.now()
                category.updated_at = datetime.now()
                return category
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Retrieve a category by its unique identifier.

        Args:
            category_id: The unique identifier of the category.

        Returns:
            Category instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT * FROM categories WHERE id = %s"
                cursor.execute(query, (category_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_category(row)
                return None
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_all(self) -> List[Category]:
        """Retrieve all category records from the database.

        Returns:
            List of Category instances.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT * FROM categories ORDER BY created_at DESC"
                cursor.execute(query)
                rows = cursor.fetchall()
                return [self._row_to_category(row) for row in rows]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def update(self, category: Category) -> Optional[Category]:
        """Update an existing category record in the database.

        Args:
            category: Category instance with updated fields.

        Returns:
            Updated Category instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    UPDATE categories
                    SET name = %s, description = %s
                    WHERE id = %s
                """
                cursor.execute(query, (category.name, category.description, category.id))
                conn.commit()
                if cursor.rowcount > 0:
                    cursor.execute("SELECT * FROM categories WHERE id = %s", (category.id,))
                    row = cursor.fetchone()
                    if row:
                        return self._row_to_category(row)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def delete(self, category_id: int) -> bool:
        """Delete a category record from the database.

        Args:
            category_id: The unique identifier of the category to delete.

        Returns:
            True if the category was deleted, False if not found.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "DELETE FROM categories WHERE id = %s"
                cursor.execute(query, (category_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def exists_by_name(self, name: str) -> bool:
        """Check if a category exists with the given name.

        Args:
            name: The category name to check.

        Returns:
            True if a category with this name exists, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT COUNT(*) FROM categories WHERE name = %s"
                cursor.execute(query, (name,))
                result = cursor.fetchone()
                return result[0] > 0
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()
