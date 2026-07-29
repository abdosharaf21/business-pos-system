"""Customer repository for database operations on the customers table."""

from typing import Optional, List

import mysql.connector

from backend.database import Database
from backend.modules.customers.model import Customer


class CustomerRepository:
    """Repository for customer database operations.

    Handles all CRUD operations for the customers table using
    parameterized queries and a shared connection pool.
    """

    def __init__(self, database: Database) -> None:
        """Initialize CustomerRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def _row_to_customer(self, row: tuple) -> Customer:
        """Convert a database row tuple to a Customer instance.

        Args:
            row: Database row as a tuple.

        Returns:
            Customer instance populated from the row data.
        """
        return Customer(
            id=row[0],
            name=row[1],
            phone=row[2],
            email=row[3],
            address=row[4],
            created_at=row[5],
            updated_at=row[6],
        )

    def create(self, customer: Customer) -> Customer:
        """Insert a new customer record into the database.

        Args:
            customer: Customer instance to insert.

        Returns:
            Customer instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    INSERT INTO customers (name, phone, email, address)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (
                    customer.name,
                    customer.phone,
                    customer.email,
                    customer.address,
                ))
                conn.commit()
                customer.id = cursor.lastrowid
                return customer
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Retrieve a customer by its unique identifier.

        Args:
            customer_id: The unique identifier of the customer.

        Returns:
            Customer instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT * FROM customers WHERE id = %s"
                cursor.execute(query, (customer_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_customer(row)
                return None
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_all(self, search: Optional[str] = None) -> List[Customer]:
        """Retrieve all customer records with optional search.

        Args:
            search: Optional search term for name or phone.

        Returns:
            List of Customer instances.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT * FROM customers"
                params = []

                if search:
                    query += " WHERE name LIKE %s OR phone LIKE %s"
                    params.extend([f"%{search}%", f"%{search}%"])

                query += " ORDER BY created_at DESC"

                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                return [self._row_to_customer(row) for row in rows]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def update(self, customer: Customer) -> Optional[Customer]:
        """Update an existing customer record in the database.

        Args:
            customer: Customer instance with updated fields.

        Returns:
            Updated Customer instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    UPDATE customers
                    SET name = %s, phone = %s, email = %s, address = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    customer.name,
                    customer.phone,
                    customer.email,
                    customer.address,
                    customer.id,
                ))
                conn.commit()
                if cursor.rowcount > 0:
                    cursor.execute("SELECT * FROM customers WHERE id = %s", (customer.id,))
                    row = cursor.fetchone()
                    if row:
                        return self._row_to_customer(row)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def delete(self, customer_id: int) -> bool:
        """Delete a customer record from the database.

        Args:
            customer_id: The unique identifier of the customer to delete.

        Returns:
            True if the customer was deleted, False if not found.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "DELETE FROM customers WHERE id = %s"
                cursor.execute(query, (customer_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def exists_by_phone(self, phone: str) -> bool:
        """Check if a customer exists with the given phone number.

        Args:
            phone: The phone number to check.

        Returns:
            True if a customer with this phone exists, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT COUNT(*) FROM customers WHERE phone = %s"
                cursor.execute(query, (phone,))
                result = cursor.fetchone()
                return result[0] > 0
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def exists_by_email(self, email: str) -> bool:
        """Check if a customer exists with the given email.

        Args:
            email: The email to check.

        Returns:
            True if a customer with this email exists, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT COUNT(*) FROM customers WHERE email = %s"
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                return result[0] > 0
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()
