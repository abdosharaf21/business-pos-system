"""Purchase repository for database operations on purchases, purchase_items,
inventory_transactions, and suppliers tables."""

from datetime import datetime
from typing import Optional, List, Dict, Any

import mysql.connector

from backend.database import Database
from backend.modules.purchases.model import Purchase, PurchaseItem


class PurchaseRepository:
    """Repository for purchase database operations.

    Handles all CRUD operations across purchases, purchase_items,
    inventory_transactions, and suppliers tables using a shared
    connection pool.
    """

    def __init__(self, database: Database) -> None:
        """Initialize PurchaseRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    # --- Supplier helpers ---

    def create_supplier(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new supplier.

        Args:
            data: Dictionary with name, phone, email, address.

        Returns:
            Dictionary of the created supplier with its id.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "INSERT INTO suppliers (name, phone, email, address) "
                    "VALUES (%s, %s, %s, %s)",
                    (data["name"], data.get("phone"), data.get("email"), data.get("address")),
                )
                conn.commit()
                supplier_id = cursor.lastrowid
                cursor.execute(
                    "SELECT id, name, phone, email, address "
                    "FROM suppliers WHERE id = %s",
                    (supplier_id,),
                )
                return cursor.fetchone()
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def exists_by_supplier_name(self, name: str) -> bool:
        """Check if a supplier exists with the given name.

        Args:
            name: The supplier name to check.

        Returns:
            True if a supplier with this name exists, False otherwise.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM suppliers WHERE name = %s",
                    (name,),
                )
                result = cursor.fetchone()
                return result[0] > 0
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def exists_by_supplier_email(self, email: str) -> bool:
        """Check if a supplier exists with the given email.

        Args:
            email: The supplier email to check.

        Returns:
            True if a supplier with this email exists, False otherwise.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM suppliers WHERE email = %s",
                    (email,),
                )
                result = cursor.fetchone()
                return result[0] > 0
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_all_suppliers(self) -> List[Dict[str, Any]]:
        """Retrieve all suppliers for dropdown selection.

        Returns:
            List of supplier dictionaries.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT id, name, phone, email FROM suppliers ORDER BY name ASC"
                )
                return cursor.fetchall()
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_supplier_by_id(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a supplier by its unique identifier.

        Args:
            supplier_id: The unique identifier of the supplier.

        Returns:
            Supplier dictionary if found, None otherwise.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT id, name, phone, email, address FROM suppliers WHERE id = %s",
                    (supplier_id,),
                )
                return cursor.fetchone()
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    # --- Product helpers ---

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a product by its unique identifier.

        Args:
            product_id: The unique identifier of the product.

        Returns:
            Product dictionary if found, None otherwise.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT id, name, quantity FROM products WHERE id = %s",
                    (product_id,),
                )
                return cursor.fetchone()
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def search_products(self, search: str) -> List[Dict[str, Any]]:
        """Search products by name, barcode, or SKU.

        Args:
            search: Search term.

        Returns:
            List of product dictionaries.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT id, name, sku, barcode, purchase_price, quantity "
                    "FROM products WHERE (name LIKE %s OR barcode LIKE %s OR sku LIKE %s) "
                    "AND status = 'active' ORDER BY "
                    "CASE WHEN barcode = %s THEN 0 "
                    "WHEN sku = %s THEN 1 "
                    "WHEN name LIKE %s THEN 2 "
                    "ELSE 3 END, "
                    "name ASC LIMIT 20",
                    (f"%{search}%", f"%{search}%", f"%{search}%",
                     search, search, f"{search}%"),
                )
                return cursor.fetchall()
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    # --- Purchase CRUD ---

    def _row_to_purchase(self, row: tuple) -> Purchase:
        """Convert a database row tuple to a Purchase instance.

        Args:
            row: Database row as a tuple.

        Returns:
            Purchase instance.
        """
        return Purchase(
            id=row[0],
            supplier_id=row[1],
            user_id=row[2],
            invoice_number=row[3],
            total_amount=row[4],
            status=row[5],
            created_at=row[6],
        )

    def _row_to_purchase_with_joins(self, row: tuple) -> Purchase:
        """Convert a joined database row to a Purchase instance.

        Args:
            row: Database row as a tuple with extra fields.

        Returns:
            Purchase instance with supplier_name and user_name.
        """
        purchase = self._row_to_purchase(row[:7])
        purchase.supplier_name = row[7] if len(row) > 7 else None
        purchase.user_name = row[8] if len(row) > 8 else None
        return purchase

    def _get_next_invoice_number(self, cursor) -> str:
        """Generate the next sequential invoice number.

        Args:
            cursor: Active database cursor.

        Returns:
            Invoice number string (e.g. PO-20260729-00001).
        """
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM purchases")
        row = cursor.fetchone()
        next_id = row["next_id"] if isinstance(row, dict) else row[0]
        date_part = datetime.now().strftime("%Y%m%d")
        return f"PO-{date_part}-{next_id:05d}"

    def create_purchase(
        self,
        supplier_id: Optional[int],
        user_id: int,
        items_data: List[Dict[str, Any]],
    ) -> Purchase:
        """Create a complete purchase with all related records in one transaction.

        Inserts the purchase header, line items, updates product stock,
        and creates inventory transactions atomically.

        Args:
            supplier_id: ID of the supplier (can be None).
            user_id: ID of the creating user.
            items_data: List of item dicts with product_id, quantity, cost_price.

        Returns:
            Created Purchase instance with items populated.

        Raises:
            mysql.connector.Error: If any database operation fails.
            ValueError: If a product is not found.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                invoice_number = self._get_next_invoice_number(cursor)

                cursor.execute(
                    "INSERT INTO purchases "
                    "(supplier_id, user_id, invoice_number, total_amount, status) "
                    "VALUES (%s, %s, %s, %s, 'completed')",
                    (supplier_id, user_id, invoice_number, 0),
                )
                purchase_id = cursor.lastrowid

                total_amount = 0.0
                created_items = []

                for item in items_data:
                    product_id = item["product_id"]
                    quantity = item["quantity"]
                    cost_price = item["cost_price"]
                    subtotal = quantity * cost_price

                    cursor.execute(
                        "SELECT id, name, quantity FROM products WHERE id = %s",
                        (product_id,),
                    )
                    product = cursor.fetchone()
                    if not product:
                        raise ValueError(f"Product with id {product_id} not found")

                    cursor.execute(
                        "INSERT INTO purchase_items "
                        "(purchase_id, product_id, quantity, cost_price, subtotal) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (purchase_id, product_id, quantity, cost_price, subtotal),
                    )
                    item_id = cursor.lastrowid

                    cursor.execute(
                        "UPDATE products SET quantity = quantity + %s WHERE id = %s",
                        (quantity, product_id),
                    )

                    cursor.execute(
                        "INSERT INTO inventory_transactions "
                        "(product_id, transaction_type, quantity, reference_id) "
                        "VALUES (%s, 'purchase', %s, %s)",
                        (product_id, quantity, purchase_id),
                    )

                    created_items.append(PurchaseItem(
                        id=item_id,
                        purchase_id=purchase_id,
                        product_id=product_id,
                        product_name=product["name"],
                        quantity=quantity,
                        cost_price=cost_price,
                        subtotal=subtotal,
                    ))
                    total_amount += subtotal

                cursor.execute(
                    "UPDATE purchases SET total_amount = %s WHERE id = %s",
                    (total_amount, purchase_id),
                )

                conn.commit()

                return Purchase(
                    id=purchase_id,
                    supplier_id=supplier_id,
                    user_id=user_id,
                    invoice_number=invoice_number,
                    total_amount=total_amount,
                    status="completed",
                    items=created_items,
                    created_at=datetime.now(),
                )

            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def get_by_id(self, purchase_id: int) -> Optional[Purchase]:
        """Retrieve a purchase by its unique identifier.

        Args:
            purchase_id: The unique identifier of the purchase.

        Returns:
            Purchase instance with items if found, None otherwise.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT p.*, s.name AS supplier_name, u.full_name AS user_name "
                    "FROM purchases p "
                    "LEFT JOIN suppliers s ON s.id = p.supplier_id "
                    "LEFT JOIN users u ON u.id = p.user_id "
                    "WHERE p.id = %s",
                    (purchase_id,),
                )
                row = cursor.fetchone()
                if not row:
                    return None

                purchase = Purchase(
                    id=row[0],
                    supplier_id=row[1],
                    user_id=row[2],
                    invoice_number=row[3],
                    total_amount=row[4],
                    status=row[5],
                    created_at=row[6],
                )
                purchase.supplier_name = row[7]
                purchase.user_name = row[8]

                cursor.execute(
                    "SELECT pi.*, pr.name AS product_name, pr.sku AS product_sku "
                    "FROM purchase_items pi "
                    "JOIN products pr ON pr.id = pi.product_id "
                    "WHERE pi.purchase_id = %s",
                    (purchase_id,),
                )
                for item_row in cursor.fetchall():
                    purchase.items.append(PurchaseItem(
                        id=item_row[0],
                        purchase_id=item_row[1],
                        product_id=item_row[2],
                        quantity=item_row[3],
                        cost_price=item_row[4],
                        subtotal=item_row[5],
                        product_name=item_row[6],
                        product_sku=item_row[7],
                    ))

                return purchase

            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_all(
        self,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Purchase]:
        """Retrieve purchase records with optional search.

        Args:
            search: Optional search term for invoice number or supplier name.
            limit: Maximum number of records.
            offset: Pagination offset.

        Returns:
            List of Purchase instances.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = (
                    "SELECT p.*, s.name AS supplier_name, u.full_name AS user_name "
                    "FROM purchases p "
                    "LEFT JOIN suppliers s ON s.id = p.supplier_id "
                    "LEFT JOIN users u ON u.id = p.user_id "
                )
                params = []

                if search:
                    query += "WHERE p.invoice_number LIKE %s OR s.name LIKE %s "
                    params.extend([f"%{search}%", f"%{search}%"])

                query += "ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()

                purchases = []
                for row in rows:
                    purchase = self._row_to_purchase_with_joins(row)
                    purchases.append(purchase)

                return purchases

            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_invoice_data(self, purchase_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve formatted invoice data for a purchase.

        Args:
            purchase_id: The unique identifier of the purchase.

        Returns:
            Dictionary with invoice details if found, None otherwise.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT p.id, p.invoice_number, p.total_amount, "
                    "p.status, p.created_at, "
                    "s.name AS supplier_name, s.phone AS supplier_phone, "
                    "s.email AS supplier_email, s.address AS supplier_address, "
                    "u.full_name AS user_name "
                    "FROM purchases p "
                    "LEFT JOIN suppliers s ON s.id = p.supplier_id "
                    "LEFT JOIN users u ON u.id = p.user_id "
                    "WHERE p.id = %s",
                    (purchase_id,),
                )
                invoice = cursor.fetchone()
                if not invoice:
                    return None

                cursor.execute(
                    "SELECT pi.quantity, pi.cost_price, pi.subtotal, "
                    "pr.name AS product_name, pr.barcode, pr.sku AS product_sku "
                    "FROM purchase_items pi "
                    "JOIN products pr ON pr.id = pi.product_id "
                    "WHERE pi.purchase_id = %s",
                    (purchase_id,),
                )
                invoice["items"] = cursor.fetchall()

                return invoice

            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_total_count(self, search: Optional[str] = None) -> int:
        """Get total count of purchases for pagination.

        Args:
            search: Optional search term.

        Returns:
            Total count.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = (
                    "SELECT COUNT(*) FROM purchases p "
                    "LEFT JOIN suppliers s ON s.id = p.supplier_id "
                )
                params = []

                if search:
                    query += "WHERE p.invoice_number LIKE %s OR s.name LIKE %s "
                    params.extend([f"%{search}%", f"%{search}%"])

                cursor.execute(query, tuple(params))
                return cursor.fetchone()[0]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()
