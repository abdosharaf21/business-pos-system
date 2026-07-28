"""ClientService repository for database operations on the client_services table."""

from datetime import datetime
from typing import Optional, List

import mysql.connector

from backend.database import Database
from backend.modules.client_services.model import ClientService


class ClientServiceRepository:
    """Repository for client service database operations.

    Handles all CRUD operations for the client_services table using
    parameterized queries and a shared connection pool.
    """

    _SELECT_COLUMNS = "id, client_id, service_id, start_date, end_date, status, created_at"

    def __init__(self, database: Database) -> None:
        """Initialize ClientServiceRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def _row_to_client_service(self, row: tuple) -> ClientService:
        """Convert a database row tuple to a ClientService instance.

        Args:
            row: Database row as a tuple matching _SELECT_COLUMNS order.

        Returns:
            ClientService instance populated from the row data.
        """
        return ClientService(
            id=row[0],
            client_id=row[1],
            service_id=row[2],
            start_date=row[3],
            end_date=row[4],
            status=row[5],
            created_at=row[6]
        )

    def create(self, client_service: ClientService) -> ClientService:
        """Insert a new client service record into the database.

        Args:
            client_service: ClientService instance to insert.

        Returns:
            ClientService instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    INSERT INTO client_services (client_id, service_id, start_date, end_date, status)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    client_service.client_id,
                    client_service.service_id,
                    client_service.start_date,
                    client_service.end_date,
                    client_service.status
                ))
                conn.commit()
                client_service.id = cursor.lastrowid
                client_service.created_at = datetime.now()
                return client_service
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def get_by_id(self, client_service_id: int) -> Optional[ClientService]:
        """Retrieve a client service record by its unique identifier.

        Args:
            client_service_id: The unique identifier of the client service.

        Returns:
            ClientService instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = f"SELECT {self._SELECT_COLUMNS} FROM client_services WHERE id = %s"
                cursor.execute(query, (client_service_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_client_service(row)
                return None
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_by_client(self, client_id: int) -> List[ClientService]:
        """Retrieve all client service records for a specific client.

        Args:
            client_id: The unique identifier of the client.

        Returns:
            List of ClientService instances for the given client.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = f"SELECT {self._SELECT_COLUMNS} FROM client_services WHERE client_id = %s ORDER BY created_at DESC"
                cursor.execute(query, (client_id,))
                rows = cursor.fetchall()
                return [self._row_to_client_service(row) for row in rows]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_by_service(self, service_id: int) -> List[ClientService]:
        """Retrieve all client service records for a specific service.

        Args:
            service_id: The unique identifier of the service.

        Returns:
            List of ClientService instances for the given service.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = f"SELECT {self._SELECT_COLUMNS} FROM client_services WHERE service_id = %s ORDER BY created_at DESC"
                cursor.execute(query, (service_id,))
                rows = cursor.fetchall()
                return [self._row_to_client_service(row) for row in rows]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_all(self) -> List[ClientService]:
        """Retrieve all client service records from the database.

        Returns:
            List of ClientService instances.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = f"SELECT {self._SELECT_COLUMNS} FROM client_services ORDER BY created_at DESC"
                cursor.execute(query)
                rows = cursor.fetchall()
                return [self._row_to_client_service(row) for row in rows]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def update(self, client_service: ClientService) -> Optional[ClientService]:
        """Update an existing client service record in the database.

        Args:
            client_service: ClientService instance with updated fields.

        Returns:
            Updated ClientService instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    UPDATE client_services
                    SET client_id = %s, service_id = %s, start_date = %s,
                        end_date = %s, status = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    client_service.client_id,
                    client_service.service_id,
                    client_service.start_date,
                    client_service.end_date,
                    client_service.status,
                    client_service.id
                ))
                conn.commit()
                if cursor.rowcount > 0:
                    cursor.execute(f"SELECT {self._SELECT_COLUMNS} FROM client_services WHERE id = %s", (client_service.id,))
                    row = cursor.fetchone()
                    if row:
                        return self._row_to_client_service(row)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def delete(self, client_service_id: int) -> bool:
        """Delete a client service record from the database.

        Args:
            client_service_id: The unique identifier of the record to delete.

        Returns:
            True if the record was deleted, False if not found.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "DELETE FROM client_services WHERE id = %s"
                cursor.execute(query, (client_service_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()
