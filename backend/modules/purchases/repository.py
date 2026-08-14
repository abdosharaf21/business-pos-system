"""Purchase repository for database operations on purchases, purchase_items,
inventory_transactions, and suppliers tables."""

from datetime import datetime
from typing import Optional, List, Dict, Any

import mysql.connector

from backend.database import Database
from backend.modules.purchases.model import Purchase, PurchaseItem
from backend.shared.expiration import normalize_expiration_date
from backend.shared.database import db_cursor


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
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
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

    def exists_by_supplier_name(self, name: str) -> bool:
        """Check if a supplier exists with the given name.

        Args:
            name: The supplier name to check.

        Returns:
            True if a supplier with this name exists, False otherwise.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM suppliers WHERE name = %s",
                    (name,),
                )
                result = cursor.fetchone()
                return result[0] > 0
            except mysql.connector.Error:
                raise

    def exists_by_supplier_email(self, email: str) -> bool:
        """Check if a supplier exists with the given email.

        Args:
            email: The supplier email to check.

        Returns:
            True if a supplier with this email exists, False otherwise.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM suppliers WHERE email = %s",
                    (email,),
                )
                result = cursor.fetchone()
                return result[0] > 0
            except mysql.connector.Error:
                raise

    def get_all_suppliers(self) -> List[Dict[str, Any]]:
        """Retrieve all suppliers for dropdown selection.

        Returns:
            List of supplier dictionaries.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT id, name, phone, email FROM suppliers ORDER BY name ASC"
                )
                return cursor.fetchall()
            except mysql.connector.Error:
                raise

    def get_supplier_by_id(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a supplier by its unique identifier.

        Args:
            supplier_id: The unique identifier of the supplier.

        Returns:
            Supplier dictionary if found, None otherwise.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT id, name, phone, email, address FROM suppliers WHERE id = %s",
                    (supplier_id,),
                )
                return cursor.fetchone()
            except mysql.connector.Error:
                raise

    def update_supplier(self, supplier_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing supplier.

        Args:
            supplier_id: The unique identifier of the supplier.
            data: Dictionary with name, phone, email, address.

        Returns:
            Dictionary of the updated supplier.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "UPDATE suppliers SET name = %s, phone = %s, email = %s, "
                    "address = %s WHERE id = %s",
                    (
                        data["name"],
                        data.get("phone"),
                        data.get("email"),
                        data.get("address"),
                        supplier_id,
                    ),
                )
                conn.commit()
                cursor.execute(
                    "SELECT id, name, phone, email, address "
                    "FROM suppliers WHERE id = %s",
                    (supplier_id,),
                )
                return cursor.fetchone()
            except mysql.connector.Error:
                conn.rollback()
                raise

    def delete_supplier(self, supplier_id: int) -> None:
        """Delete a supplier by its unique identifier.

        Args:
            supplier_id: The unique identifier of the supplier.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    "DELETE FROM suppliers WHERE id = %s",
                    (supplier_id,),
                )
                conn.commit()
            except mysql.connector.Error:
                conn.rollback()
                raise

    # --- Product helpers ---

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a product by its unique identifier.

        Args:
            product_id: The unique identifier of the product.

        Returns:
            Product dictionary if found, None otherwise.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT id, name, quantity FROM products WHERE id = %s",
                    (product_id,),
                )
                return cursor.fetchone()
            except mysql.connector.Error:
                raise

    def search_products(self, search: str) -> List[Dict[str, Any]]:
        """Search products by name, barcode, or SKU.

        Args:
            search: Search term.

        Returns:
            List of product dictionaries.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
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

    # --- Purchase CRUD ---

    _PURCHASE_COLUMNS = (
        "p.id, p.supplier_id, p.user_id, p.invoice_number, p.total_amount, "
        "p.status, p.payment_method, p.notes, p.created_at"
    )

    def _row_to_purchase(self, row: tuple) -> Purchase:
        """Convert a database row tuple to a Purchase instance.

        Args:
            row: Database row as a tuple matching _PURCHASE_COLUMNS order.

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
            payment_method=row[6],
            notes=row[7],
            created_at=row[8],
        )

    def _row_to_purchase_with_joins(self, row: tuple) -> Purchase:
        """Convert a joined database row to a Purchase instance.

        Args:
            row: Database row as a tuple with supplier_name and user_name.

        Returns:
            Purchase instance with supplier_name and user_name.
        """
        purchase = self._row_to_purchase(row[:9])
        purchase.supplier_name = row[9] if len(row) > 9 else None
        purchase.user_name = row[10] if len(row) > 10 else None
        return purchase

    def _build_filter_where(
        self,
        search: Optional[str],
        date: Optional[str],
        date_from: Optional[str],
        date_to: Optional[str],
    ) -> tuple:
        """Build a WHERE clause and parameters for purchase list filters.

        Args:
            search: Search term for invoice number or supplier name.
            date: Exact date filter (YYYY-MM-DD).
            date_from: Start of date range (YYYY-MM-DD).
            date_to: End of date range (YYYY-MM-DD).

        Returns:
            Tuple of (where_clause, params list).
        """
        clauses = []
        params: list = []

        if search:
            clauses.append("(p.invoice_number LIKE %s OR s.name LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])

        if date:
            clauses.append("DATE(p.created_at) = %s")
            params.append(date)

        if date_from:
            clauses.append("DATE(p.created_at) >= %s")
            params.append(date_from)

        if date_to:
            clauses.append("DATE(p.created_at) <= %s")
            params.append(date_to)

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        return where, params

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
        payment_method: str = "cash",
        notes: Optional[str] = None,
    ) -> Purchase:
        """Create a complete purchase with all related records in one transaction.

        Inserts the purchase header, line items, updates product stock,
        and creates inventory transactions atomically.

        Args:
            supplier_id: ID of the supplier (can be None).
            user_id: ID of the creating user.
            items_data: List of item dicts with product_id, quantity, cost_price.
            payment_method: Payment method used for the purchase.
            notes: Optional notes attached to the purchase.

        Returns:
            Created Purchase instance with items populated.

        Raises:
            mysql.connector.Error: If any database operation fails.
            ValueError: If a product is not found.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                invoice_number = self._get_next_invoice_number(cursor)

                cursor.execute(
                    "INSERT INTO purchases "
                    "(supplier_id, user_id, invoice_number, total_amount, status, "
                    "payment_method, notes) "
                    "VALUES (%s, %s, %s, %s, 'completed', %s, %s)",
                    (supplier_id, user_id, invoice_number, 0, payment_method, notes),
                )
                purchase_id = cursor.lastrowid

                total_amount = 0.0
                created_items = []

                for item in items_data:
                    product_id = item["product_id"]
                    quantity = item["quantity"]
                    cost_price = item["cost_price"]
                    expiration_date = item.get("expiration_date")
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
                        "(purchase_id, product_id, quantity, cost_price, subtotal, "
                        "expiration_date) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (purchase_id, product_id, quantity, cost_price, subtotal,
                         expiration_date),
                    )
                    item_id = cursor.lastrowid

                    cursor.execute(
                        "UPDATE products SET quantity = quantity + %s WHERE id = %s",
                        (quantity, product_id),
                    )

                    cursor.execute(
                        "INSERT INTO inventory (product_id, location, quantity) "
                        "VALUES (%s, 'warehouse', %s) "
                        "ON DUPLICATE KEY UPDATE quantity = quantity + %s",
                        (product_id, quantity, quantity),
                    )

                    cursor.execute(
                        "INSERT INTO stock_movements "
                        "(product_id, from_location, to_location, quantity, "
                        "movement_type, reference, notes, user_id) "
                        "VALUES (%s, NULL, 'warehouse', %s, 'purchase', %s, %s, %s)",
                        (product_id, quantity, invoice_number, "Purchase", user_id),
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
                        expiration_date=expiration_date,
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
                    payment_method=payment_method,
                    notes=notes,
                    items=created_items,
                    created_at=datetime.now(),
                )

            except mysql.connector.Error:
                conn.rollback()
                raise

    def get_by_id(self, purchase_id: int) -> Optional[Purchase]:
        """Retrieve a purchase by its unique identifier.

        Args:
            purchase_id: The unique identifier of the purchase.

        Returns:
            Purchase instance with items if found, None otherwise.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    "SELECT " + self._PURCHASE_COLUMNS +
                    ", s.name AS supplier_name, u.full_name AS user_name "
                    "FROM purchases p "
                    "LEFT JOIN suppliers s ON s.id = p.supplier_id "
                    "LEFT JOIN users u ON u.id = p.user_id "
                    "WHERE p.id = %s",
                    (purchase_id,),
                )
                row = cursor.fetchone()
                if not row:
                    return None

                purchase = self._row_to_purchase_with_joins(row)

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
                        expiration_date=normalize_expiration_date(item_row[6]),
                        product_name=item_row[7],
                        product_sku=item_row[8],
                    ))

                return purchase

            except mysql.connector.Error:
                raise

    def get_all(
        self,
        search: Optional[str] = None,
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Purchase]:
        """Retrieve purchase records with optional filters.

        Args:
            search: Optional search term for invoice number or supplier name.
            date: Optional exact purchase date (YYYY-MM-DD).
            date_from: Optional start of date range (YYYY-MM-DD).
            date_to: Optional end of date range (YYYY-MM-DD).
            limit: Maximum number of records.
            offset: Pagination offset.

        Returns:
            List of Purchase instances.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                where, params = self._build_filter_where(
                    search, date, date_from, date_to
                )

                query = (
                    "SELECT " + self._PURCHASE_COLUMNS +
                    ", s.name AS supplier_name, u.full_name AS user_name "
                    "FROM purchases p "
                    "LEFT JOIN suppliers s ON s.id = p.supplier_id "
                    "LEFT JOIN users u ON u.id = p.user_id "
                    + where + " "
                    "ORDER BY p.created_at DESC, p.id DESC LIMIT %s OFFSET %s"
                )
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

    def get_invoice_data(self, purchase_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve formatted invoice data for a purchase.

        Args:
            purchase_id: The unique identifier of the purchase.

        Returns:
            Dictionary with invoice details if found, None otherwise.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT p.id, p.invoice_number, p.total_amount, "
                    "p.status, p.payment_method, p.notes, p.created_at, "
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
                    "pi.expiration_date, "
                    "pr.name AS product_name, pr.barcode, pr.sku AS product_sku "
                    "FROM purchase_items pi "
                    "JOIN products pr ON pr.id = pi.product_id "
                    "WHERE pi.purchase_id = %s",
                    (purchase_id,),
                )
                invoice["items"] = cursor.fetchall()
                for invoice_item in invoice["items"]:
                    invoice_item["expiration_date"] = normalize_expiration_date(
                        invoice_item["expiration_date"]
                    )

                return invoice

            except mysql.connector.Error:
                raise

    def get_total_count(
        self,
        search: Optional[str] = None,
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> int:
        """Get total count of purchases for pagination.

        Args:
            search: Optional search term.
            date: Optional exact purchase date (YYYY-MM-DD).
            date_from: Optional start of date range (YYYY-MM-DD).
            date_to: Optional end of date range (YYYY-MM-DD).

        Returns:
            Total count.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                where, params = self._build_filter_where(
                    search, date, date_from, date_to
                )

                query = (
                    "SELECT COUNT(*) FROM purchases p "
                    "LEFT JOIN suppliers s ON s.id = p.supplier_id "
                    + where
                )

                cursor.execute(query, tuple(params))
                return cursor.fetchone()[0]
            except mysql.connector.Error:
                raise
