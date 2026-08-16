"""Client repository for database operations on the clients table."""

from datetime import datetime
from typing import Optional, List

import mysql.connector

from backend.database import Database
from backend.modules.clients.model import Client
from backend.shared.database import db_cursor


class ClientRepository:
    """Repository for client database operations.

    Handles all CRUD operations for the clients table using
    parameterized queries and a shared connection pool.
    """

    def __init__(self, database: Database) -> None:
        """Initialize ClientRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def _row_to_client(self, row: tuple) -> Client:
        """Convert a database row tuple to a Client instance.

        Args:
            row: Database row as a tuple.

        Returns:
            Client instance populated from the row data.
        """
        return Client(
            id=row[0],
            company_name=row[1],
            contact_person=row[2],
            email=row[3],
            phone=row[4],
            address=row[5],
            status=row[6],
            created_at=row[7]
        )

    def create(self, client: Client) -> Client:
        """Insert a new client record into the database.

        Args:
            client: Client instance to insert.

        Returns:
            Client instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = """
                    INSERT INTO clients (company_name, contact_person, email, phone, address, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    client.company_name,
                    client.contact_person,
                    client.email,
                    client.phone,
                    client.address,
                    client.status
                ))
                conn.commit()
                client.id = cursor.lastrowid
                client.created_at = datetime.now()
                return client
            except mysql.connector.Error:
                conn.rollback()
                raise

    def get_by_id(self, client_id: int) -> Optional[Client]:
        """Retrieve a client by their unique identifier.

        Args:
            client_id: The unique identifier of the client.

        Returns:
            Client instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "SELECT * FROM clients WHERE id = %s"
                cursor.execute(query, (client_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_client(row)
                return None
            except mysql.connector.Error:
                raise

    def get_all(self) -> List[Client]:
        """Retrieve all client records from the database.

        Returns:
            List of Client instances.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "SELECT * FROM clients ORDER BY created_at DESC"
                cursor.execute(query)
                rows = cursor.fetchall()
                return [self._row_to_client(row) for row in rows]
            except mysql.connector.Error:
                raise

    def update(self, client: Client) -> Optional[Client]:
        """Update an existing client record in the database.

        Args:
            client: Client instance with updated fields.

        Returns:
            Updated Client instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = """
                    UPDATE clients
                    SET company_name = %s, contact_person = %s, email = %s,
                        phone = %s, address = %s, status = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    client.company_name,
                    client.contact_person,
                    client.email,
                    client.phone,
                    client.address,
                    client.status,
                    client.id
                ))
                conn.commit()
                if cursor.rowcount > 0:
                    cursor.execute("SELECT * FROM clients WHERE id = %s", (client.id,))
                    row = cursor.fetchone()
                    if row:
                        return self._row_to_client(row)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise

    def delete(self, client_id: int) -> bool:
        """Delete a client record from the database.

        Args:
            client_id: The unique identifier of the client to delete.

        Returns:
            True if the client was deleted, False if not found.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "DELETE FROM clients WHERE id = %s"
                cursor.execute(query, (client_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise
