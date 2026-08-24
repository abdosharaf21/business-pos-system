"""Repository for POS product queries."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.database import Database
from backend.modules.pos.model import PosProduct


class PosRepository:
    """Handles database queries for the POS interface."""

    def __init__(self, database: Database) -> None:
        self._database = database

    def _row_to_pos_product(self, row: Dict[str, Any]) -> PosProduct:
        return PosProduct(
            id=row["id"],
            barcode=row.get("barcode"),
            name=row["name"],
            category=row.get("category_name", ""),
            selling_price=float(row["selling_price"]),
            quantity=int(row["quantity"]),
            minimum_stock=int(row.get("minimum_stock", 0)),
        )

    def _get_next_invoice_number(self, cursor) -> str:
        """Generate the next sequential invoice number for sales.

        Args:
            cursor: Active database cursor.

        Returns:
            Invoice number string (e.g. INV-20260729-00001).
        """
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM sales")
        row = cursor.fetchone()
        next_id = row["next_id"] if isinstance(row, dict) else row[0]
        date_part = datetime.now().strftime("%Y%m%d")
        return f"INV-{date_part}-{next_id:05d}"

    def get_active_products(
        self,
        search: Optional[str] = None,
        barcode: Optional[str] = None,
        category_id: Optional[int] = None,
    ) -> List[PosProduct]:
        """Fetch active products with optional filters.

        Args:
            search: Search term for name or barcode (partial match).
            barcode: Exact barcode match.
            category_id: Filter by category ID.

        Returns:
            List of PosProduct instances.
        """
        query = (
            "SELECT p.id, p.barcode, p.name, c.name AS category_name, "
            "p.selling_price, p.quantity, p.minimum_stock "
            "FROM products p "
            "LEFT JOIN categories c ON p.category_id = c.id "
            "WHERE p.status = 'active'"
        )
        params: list = []

        if barcode:
            query += " AND p.barcode = %s"
            params.append(barcode)

        if category_id is not None:
            query += " AND p.category_id = %s"
            params.append(category_id)

        if search:
            query += " AND (p.name LIKE %s OR p.barcode LIKE %s)"
            like_term = f"%{search}%"
            params.extend([like_term, like_term])

        query += " ORDER BY p.name ASC"

        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                return [self._row_to_pos_product(row) for row in rows]
            except Exception:
                raise
            finally:
                cursor.close()

    def get_categories(self) -> List[Dict[str, Any]]:
        """Fetch all categories for the filter dropdown.

        Returns:
            List of category dicts with id and name.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("SELECT id, name FROM categories ORDER BY name ASC")
                return cursor.fetchall()
            except Exception:
                raise
            finally:
                cursor.close()

    def get_customer_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a customer by ID for validation.

        Args:
            customer_id: Customer ID.

        Returns:
            Customer dict or None.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT id, name, phone FROM customers WHERE id = %s",
                    (customer_id,),
                )
                return cursor.fetchone()
            except Exception:
                raise
            finally:
                cursor.close()

    def search_customers(self, search: str) -> List[Dict[str, Any]]:
        """Search customers by name or phone.

        Args:
            search: Search term.

        Returns:
            List of matching customer dicts.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT id, name, phone FROM customers "
                    "WHERE name LIKE %s OR phone LIKE %s "
                    "ORDER BY name ASC LIMIT 20",
                    (f"%{search}%", f"%{search}%"),
                )
                return cursor.fetchall()
            except Exception:
                raise
            finally:
                cursor.close()

    def get_invoice(self, sale_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve formatted invoice data for a completed sale.

        Args:
            sale_id: ID of the sale.

        Returns:
            Dict with sale header, items, and totals, or None if not found.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT s.id, s.invoice_number, s.created_at, "
                    "s.total_amount, s.discount, s.paid_amount, "
                    "s.payment_method, s.status, "
                    "u.full_name AS cashier_name, "
                    "c.name AS customer_name, c.phone AS customer_phone "
                    "FROM sales s "
                    "JOIN users u ON s.user_id = u.id "
                    "LEFT JOIN customers c ON s.customer_id = c.id "
                    "WHERE s.id = %s",
                    (sale_id,),
                )
                sale = cursor.fetchone()
                if not sale:
                    return None

                cursor.execute(
                    "SELECT si.id, si.product_id, si.quantity, "
                    "si.unit_price, si.subtotal, "
                    "p.name AS product_name "
                    "FROM sale_items si "
                    "JOIN products p ON si.product_id = p.id "
                    "WHERE si.sale_id = %s "
                    "ORDER BY si.id ASC",
                    (sale_id,),
                )
                items = cursor.fetchall()

                return {
                    "id": sale["id"],
                    "invoice_number": sale["invoice_number"],
                    "created_at": sale["created_at"].isoformat() if sale["created_at"] else None,
                    "cashier_name": sale["cashier_name"],
                    "customer_name": sale.get("customer_name"),
                    "customer_phone": sale.get("customer_phone"),
                    "payment_method": sale["payment_method"],
                    "status": sale["status"],
                    "items": [
                        {
                            "id": item["id"],
                            "product_id": item["product_id"],
                            "product_name": item["product_name"],
                            "quantity": item["quantity"],
                            "unit_price": float(item["unit_price"]),
                            "subtotal": float(item["subtotal"]),
                        }
                        for item in items
                    ],
                    "subtotal": float(sale["total_amount"]),
                    "discount": float(sale["discount"]),
                    "grand_total": float(sale["total_amount"]) - float(sale["discount"]),
                    "paid_amount": float(sale["paid_amount"]),
                }

            except Exception:
                raise
            finally:
                cursor.close()

    def create_checkout(
        self,
        user_id: int,
        items_data: List[Dict[str, Any]],
        customer_id: Optional[int] = None,
        payment_method: str = "cash",
        discount: float = 0.0,
    ) -> Dict[str, Any]:
        """Create a completed sale in one transaction.

        Inserts sale header, sale items, decreases stock,
        and creates inventory transactions atomically.

        Args:
            user_id: ID of the cashier.
            items_data: List of item dicts with product_id, quantity, unit_price.
            customer_id: Optional customer ID.
            payment_method: Payment method enum.
            discount: Discount amount.

        Returns:
            Dict with sale details including invoice_number and items.

        Raises:
            ValueError: If a product is not found or stock is insufficient.
            mysql.connector.Error: If any database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                invoice_number = self._get_next_invoice_number(cursor)

                cursor.execute(
                    "INSERT INTO sales "
                    "(customer_id, user_id, invoice_number, total_amount, discount, "
                    "paid_amount, payment_method, status) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, 'completed')",
                    (customer_id, user_id, invoice_number, 0, discount, 0, payment_method),
                )
                sale_id = cursor.lastrowid

                total_amount = 0.0
                created_items = []

                for item in items_data:
                    product_id = item["product_id"]
                    quantity = item["quantity"]
                    unit_price = item["unit_price"]
                    subtotal = quantity * unit_price

                    cursor.execute(
                        "SELECT id, name, quantity FROM products WHERE id = %s FOR UPDATE",
                        (product_id,),
                    )
                    product = cursor.fetchone()
                    if not product:
                        raise ValueError(f"Product with id {product_id} not found")

                    cursor.execute(
                        "SELECT id, quantity FROM inventory "
                        "WHERE product_id = %s "
                        "AND (warehouse_id = "
                        "(SELECT id FROM warehouses WHERE code = 'STORE') "
                        "OR (warehouse_id IS NULL AND location = 'store')) "
                        "ORDER BY warehouse_id IS NULL ASC LIMIT 1 FOR UPDATE",
                        (product_id,),
                    )
                    store_stock = cursor.fetchone()
                    store_quantity = int(store_stock["quantity"]) if store_stock else 0

                    if store_quantity < quantity:
                        raise ValueError(
                            f"Insufficient store stock for '{product['name']}': "
                            f"available {store_quantity}, requested {quantity}"
                        )

                    cursor.execute(
                        "INSERT INTO sale_items "
                        "(sale_id, product_id, quantity, unit_price, subtotal) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (sale_id, product_id, quantity, unit_price, subtotal),
                    )
                    item_id = cursor.lastrowid

                    cursor.execute(
                        "UPDATE products SET quantity = quantity - %s WHERE id = %s",
                        (quantity, product_id),
                    )

                    if store_stock:
                        cursor.execute(
                            "UPDATE inventory SET quantity = quantity - %s WHERE id = %s",
                            (quantity, store_stock["id"]),
                        )

                    cursor.execute(
                        "INSERT INTO stock_movements "
                        "(product_id, from_location, to_location, quantity, "
                        "movement_type, reference, notes, user_id) "
                        "VALUES (%s, 'store', NULL, %s, 'sale', %s, %s, %s)",
                        (product_id, quantity, invoice_number, "POS sale", user_id),
                    )

                    cursor.execute(
                        "INSERT INTO inventory_transactions "
                        "(product_id, transaction_type, quantity, reference_id) "
                        "VALUES (%s, 'sale', %s, %s)",
                        (product_id, -quantity, sale_id),
                    )

                    created_items.append({
                        "id": item_id,
                        "sale_id": sale_id,
                        "product_id": product_id,
                        "product_name": product["name"],
                        "quantity": quantity,
                        "unit_price": float(unit_price),
                        "subtotal": float(subtotal),
                    })
                    total_amount += subtotal

                paid_amount = total_amount - discount
                cursor.execute(
                    "UPDATE sales SET total_amount = %s, paid_amount = %s WHERE id = %s",
                    (total_amount, paid_amount, sale_id),
                )

                conn.commit()

                return {
                    "id": sale_id,
                    "invoice_number": invoice_number,
                    "total_amount": float(total_amount),
                    "discount": float(discount),
                    "paid_amount": float(paid_amount),
                    "payment_method": payment_method,
                    "status": "completed",
                    "user_id": user_id,
                    "customer_id": customer_id,
                    "items": created_items,
                }

            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()
