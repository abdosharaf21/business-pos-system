"""Product repository for database operations on the products table."""

from datetime import datetime
from typing import Optional, List

import mysql.connector

from backend.database import Database
from backend.modules.products.model import Product


class ProductRepository:
    """Repository for product database operations.

    Handles all CRUD operations for the products table using
    parameterized queries and a shared connection pool.
    """

    def __init__(self, database: Database) -> None:
        """Initialize ProductRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def _row_to_product(self, row: tuple) -> Product:
        """Convert a database row tuple to a Product instance.

        Args:
            row: Database row as a tuple.

        Returns:
            Product instance populated from the row data.
        """
        return Product(
            id=row[0],
            category_id=row[1],
            name=row[2],
            sku=row[3],
            barcode=row[4],
            description=row[5],
            purchase_price=row[6],
            selling_price=row[7],
            quantity=row[8],
            minimum_stock=row[9],
            status=row[10],
            created_at=row[11],
            updated_at=row[12],
        )

    def _row_to_product_with_category(self, row: tuple) -> Product:
        """Convert a database row tuple (with category join) to a Product instance.

        Args:
            row: Database row as a tuple including category_name.

        Returns:
            Product instance with category_name populated.
        """
        product = self._row_to_product(row[:13])
        product.category_name = row[13] if len(row) > 13 else None
        return product

    def create(self, product: Product) -> Product:
        """Insert a new product record into the database.

        Args:
            product: Product instance to insert.

        Returns:
            Product instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    INSERT INTO products (category_id, name, sku, barcode, description,
                        purchase_price, selling_price, quantity, minimum_stock, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    product.category_id,
                    product.name,
                    product.sku,
                    product.barcode,
                    product.description,
                    product.purchase_price,
                    product.selling_price,
                    product.quantity,
                    product.minimum_stock,
                    product.status,
                ))
                conn.commit()
                product.id = cursor.lastrowid

                cursor.execute(
                    "INSERT IGNORE INTO inventory (product_id, location, quantity) "
                    "VALUES (%s, 'warehouse', 0), (%s, 'store', 0)",
                    (product.id, product.id),
                )
                conn.commit()
                return product
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Retrieve a product by its unique identifier.

        Args:
            product_id: The unique identifier of the product.

        Returns:
            Product instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    SELECT p.*, c.name AS category_name
                    FROM products p
                    LEFT JOIN categories c ON c.id = p.category_id
                    WHERE p.id = %s
                """
                cursor.execute(query, (product_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_product_with_category(row)
                return None
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_all(self, search: Optional[str] = None,
                category_id: Optional[int] = None,
                status: Optional[str] = None) -> List[Product]:
        """Retrieve product records with optional filtering.

        Args:
            search: Optional search term for name or barcode.
            category_id: Optional category filter.
            status: Optional status filter.

        Returns:
            List of Product instances.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    SELECT p.*, c.name AS category_name
                    FROM products p
                    LEFT JOIN categories c ON c.id = p.category_id
                """
                conditions = []
                params = []

                if search:
                    conditions.append("(p.name LIKE %s OR p.barcode LIKE %s OR p.sku LIKE %s)")
                    params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

                if category_id is not None:
                    conditions.append("p.category_id = %s")
                    params.append(category_id)

                if status:
                    conditions.append("p.status = %s")
                    params.append(status)

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                query += " ORDER BY p.created_at DESC"

                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                return [self._row_to_product_with_category(row) for row in rows]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def update(self, product: Product) -> Optional[Product]:
        """Update an existing product record in the database.

        Args:
            product: Product instance with updated fields.

        Returns:
            Updated Product instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    UPDATE products
                    SET category_id = %s, name = %s, sku = %s, barcode = %s,
                        description = %s, purchase_price = %s, selling_price = %s,
                        quantity = %s, minimum_stock = %s, status = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    product.category_id,
                    product.name,
                    product.sku,
                    product.barcode,
                    product.description,
                    product.purchase_price,
                    product.selling_price,
                    product.quantity,
                    product.minimum_stock,
                    product.status,
                    product.id,
                ))
                conn.commit()
                if cursor.rowcount > 0:
                    return self.get_by_id(product.id)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def delete(self, product_id: int) -> bool:
        """Delete a product record from the database.

        Args:
            product_id: The unique identifier of the product to delete.

        Returns:
            True if the product was deleted, False if not found.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "DELETE FROM products WHERE id = %s"
                cursor.execute(query, (product_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def exists_by_name(self, name: str) -> bool:
        """Check if a product exists with the given name.

        Args:
            name: The product name to check.

        Returns:
            True if a product with this name exists, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT COUNT(*) FROM products WHERE name = %s"
                cursor.execute(query, (name,))
                result = cursor.fetchone()
                return result[0] > 0
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def exists_by_barcode(self, barcode: str) -> bool:
        """Check if a product exists with the given barcode.

        Args:
            barcode: The barcode to check.

        Returns:
            True if a product with this barcode exists, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT COUNT(*) FROM products WHERE barcode = %s"
                cursor.execute(query, (barcode,))
                result = cursor.fetchone()
                return result[0] > 0
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def exists_by_sku(self, sku: str) -> bool:
        """Check if a product exists with the given SKU.

        Args:
            sku: The SKU to check.

        Returns:
            True if a product with this SKU exists, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT COUNT(*) FROM products WHERE sku = %s"
                cursor.execute(query, (sku,))
                result = cursor.fetchone()
                return result[0] > 0
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()
