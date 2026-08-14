"""User repository for database operations on the users table."""

from datetime import datetime
from typing import Optional, List

import mysql.connector

from backend.database import Database
from backend.modules.users.model import User
from backend.shared.database import db_cursor


class UserRepository:
    """Repository for user database operations.

    Handles all CRUD operations for the users table using
    parameterized queries and a shared connection pool.
    """

    def __init__(self, database: Database) -> None:
        """Initialize UserRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def _row_to_user(self, row: tuple) -> User:
        """Convert a database row tuple to a User instance.

        Args:
            row: Database row as a tuple.

        Returns:
            User instance populated from the row data.
        """
        return User(
            id=row[0],
            full_name=row[1],
            email=row[2],
            password_hash=row[3],
            phone=row[4],
            role=row[5],
            status=row[6],
            created_at=row[7],
            updated_at=row[8]
        )

    def create(self, user: User) -> User:
        """Insert a new user record into the database.

        Args:
            user: User instance to insert.

        Returns:
            User instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = """
                    INSERT INTO users (full_name, email, password_hash, phone, role, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    user.full_name,
                    user.email,
                    user.password_hash,
                    user.phone,
                    user.role,
                    user.status
                ))
                conn.commit()
                user.id = cursor.lastrowid
                user.created_at = datetime.now()
                user.updated_at = datetime.now()
                return user
            except mysql.connector.Error:
                conn.rollback()
                raise

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their unique identifier.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            User instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "SELECT * FROM users WHERE id = %s"
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_user(row)
                return None
            except mysql.connector.Error:
                raise

    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address.

        Args:
            email: The email address to search for.

        Returns:
            User instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "SELECT * FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_user(row)
                return None
            except mysql.connector.Error:
                raise

    def exists_by_email(self, email: str) -> bool:
        """Check if a user exists with the given email address.

        Args:
            email: The email address to check.

        Returns:
            True if a user with this email exists, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "SELECT COUNT(*) FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                return result[0] > 0
            except mysql.connector.Error:
                raise

    def get_all(self) -> List[User]:
        """Retrieve all user records from the database.

        Returns:
            List of User instances.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "SELECT * FROM users ORDER BY created_at DESC"
                cursor.execute(query)
                rows = cursor.fetchall()
                return [self._row_to_user(row) for row in rows]
            except mysql.connector.Error:
                raise

    def update(self, user: User) -> Optional[User]:
        """Update an existing user record in the database.

        Args:
            user: User instance with updated fields.

        Returns:
            Updated User instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = """
                    UPDATE users
                    SET full_name = %s, email = %s, password_hash = %s,
                        phone = %s, role = %s, status = %s, updated_at = NOW()
                    WHERE id = %s
                """
                cursor.execute(query, (
                    user.full_name,
                    user.email,
                    user.password_hash,
                    user.phone,
                    user.role,
                    user.status,
                    user.id
                ))
                conn.commit()
                if cursor.rowcount > 0:
                    cursor.execute("SELECT * FROM users WHERE id = %s", (user.id,))
                    row = cursor.fetchone()
                    if row:
                        return self._row_to_user(row)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise

    def update_password(self, user_id: int, new_hash: str) -> bool:
        """Update a user's password hash.

        Args:
            user_id: The unique identifier of the user.
            new_hash: The new bcrypt password hash.

        Returns:
            True if updated, False if user not found.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = """
                    UPDATE users
                    SET password_hash = %s, updated_at = NOW()
                    WHERE id = %s
                """
                cursor.execute(query, (new_hash, user_id))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise

    def delete(self, user_id: int) -> bool:
        """Delete a user record from the database.

        Args:
            user_id: The unique identifier of the user to delete.

        Returns:
            True if the user was deleted, False if not found.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                query = "DELETE FROM users WHERE id = %s"
                cursor.execute(query, (user_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise
