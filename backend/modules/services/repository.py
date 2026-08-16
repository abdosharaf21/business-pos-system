"""Service repository for database operations on the services table."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

import mysql.connector

from backend.database import Database
from backend.modules.services.model import Service
from backend.shared.database import db_cursor


class ServiceRepository:
    """Repository for service database operations.

    Handles all CRUD operations for the services table using
    parameterized queries and a shared connection pool.
    """

    def __init__(self, database: Database) -> None:
        """Initialize ServiceRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def _row_to_service(self, row: tuple) -> Service:
        """Convert a database row tuple to a Service instance.

        Args:
            row: Database row as a tuple.

        Returns:
            Service instance populated from the row data.
        """
        return Service(
            id=row[0],
            category_id=row[1],
            name=row[2],
            description=row[3],
            price=Decimal(str(row[4])) if row[4] is not None else None,
            duration_days=row[5],
            status=row[6],
            created_at=row[7]
        )

    def create(self, service: Service) -> Service:
        """Insert a new service record into the database.

        Args:
            service: Service instance to insert.

        Returns:
            Service instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = """
                    INSERT INTO services (category_id, name, description, price, duration_days, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    service.category_id,
                    service.name,
                    service.description,
                    service.price,
                    service.duration_days,
                    service.status
                ))
                conn.commit()
                service.id = cursor.lastrowid
                service.created_at = datetime.now()
                return service
            except mysql.connector.Error:
                conn.rollback()
                raise

    def get_by_id(self, service_id: int) -> Optional[Service]:
        """Retrieve a service by its unique identifier.

        Args:
            service_id: The unique identifier of the service.

        Returns:
            Service instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "SELECT * FROM services WHERE id = %s"
                cursor.execute(query, (service_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_service(row)
                return None
            except mysql.connector.Error:
                raise

    def get_by_category(self, category_id: int) -> List[Service]:
        """Retrieve all services belonging to a specific category.

        Args:
            category_id: The unique identifier of the category.

        Returns:
            List of Service instances for the given category.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "SELECT * FROM services WHERE category_id = %s ORDER BY created_at DESC"
                cursor.execute(query, (category_id,))
                rows = cursor.fetchall()
                return [self._row_to_service(row) for row in rows]
            except mysql.connector.Error:
                raise

    def get_all(self) -> List[Service]:
        """Retrieve all service records from the database.

        Returns:
            List of Service instances.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "SELECT * FROM services ORDER BY created_at DESC"
                cursor.execute(query)
                rows = cursor.fetchall()
                return [self._row_to_service(row) for row in rows]
            except mysql.connector.Error:
                raise

    def update(self, service: Service) -> Optional[Service]:
        """Update an existing service record in the database.

        Args:
            service: Service instance with updated fields.

        Returns:
            Updated Service instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = """
                    UPDATE services
                    SET category_id = %s, name = %s, description = %s,
                        price = %s, duration_days = %s, status = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    service.category_id,
                    service.name,
                    service.description,
                    service.price,
                    service.duration_days,
                    service.status,
                    service.id
                ))
                conn.commit()
                if cursor.rowcount > 0:
                    cursor.execute("SELECT * FROM services WHERE id = %s", (service.id,))
                    row = cursor.fetchone()
                    if row:
                        return self._row_to_service(row)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise

    def delete(self, service_id: int) -> bool:
        """Delete a service record from the database.

        Args:
            service_id: The unique identifier of the service to delete.

        Returns:
            True if the service was deleted, False if not found.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "DELETE FROM services WHERE id = %s"
                cursor.execute(query, (service_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise
