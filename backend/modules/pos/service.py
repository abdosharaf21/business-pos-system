"""Service layer for POS operations."""
from typing import Any, Dict, List, Optional

from backend.modules.pos.model import PosProduct
from backend.modules.pos.repository import PosRepository


class PosService:
    """Contains business logic for the POS interface."""

    VALID_PAYMENT_METHODS = {"cash", "card", "transfer", "mixed"}

    def __init__(self, pos_repository: PosRepository) -> None:
        self._pos_repository = pos_repository

    def get_active_products(
        self,
        search: Optional[str] = None,
        barcode: Optional[str] = None,
        category_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch and format active products.

        Args:
            search: Search term for name or barcode.
            barcode: Exact barcode match.
            category_id: Filter by category ID.

        Returns:
            List of product dicts.
        """
        products = self._pos_repository.get_active_products(
            search=search, barcode=barcode, category_id=category_id
        )
        return [p.to_dict() for p in products]

    def get_categories(self) -> List[Dict[str, Any]]:
        """Fetch categories for the filter dropdown.

        Returns:
            List of category dicts.
        """
        return self._pos_repository.get_categories()

    def checkout(self, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Process a POS checkout.

        Validates cart, stock, customer, payment method, then
        creates sale with items, decreases stock, and records
        inventory transactions in a single database transaction.

        Args:
            data: Checkout data with items, customer_id, payment_method.
            user_id: ID of the cashier.

        Returns:
            Completed sale dict with invoice number and items.

        Raises:
            ValueError: If validation fails or business rules are violated.
        """
        items = data.get("items", [])
        if not items:
            raise ValueError("Cart is empty")

        for item in items:
            if not item.get("product_id"):
                raise ValueError("Invalid product in cart")
            quantity = item.get("quantity")
            if not isinstance(quantity, int) or quantity < 1:
                raise ValueError(
                    f"Invalid quantity for product {item.get('product_id')}"
                )
            unit_price = item.get("unit_price")
            if not isinstance(unit_price, (int, float)) or unit_price < 0:
                raise ValueError(
                    f"Invalid price for product {item.get('product_id')}"
                )

        payment_method = data.get("payment_method", "cash")
        if payment_method not in self.VALID_PAYMENT_METHODS:
            raise ValueError(f"Invalid payment method: {payment_method}")

        customer_id = data.get("customer_id")
        if customer_id is not None:
            customer = self._pos_repository.get_customer_by_id(customer_id)
            if customer is None:
                raise ValueError("Customer not found")

        discount = float(data.get("discount", 0))
        if discount < 0:
            raise ValueError("Discount cannot be negative")

        items_data = [
            {
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "unit_price": float(item["unit_price"]),
            }
            for item in items
        ]

        return self._pos_repository.create_checkout(
            user_id=user_id,
            items_data=items_data,
            customer_id=customer_id,
            payment_method=payment_method,
            discount=discount,
        )

    def get_invoice(self, sale_id: int) -> Dict[str, Any]:
        """Retrieve formatted invoice data.

        Args:
            sale_id: ID of the sale.

        Returns:
            Invoice dict with header, items, and totals.

        Raises:
            ValueError: If sale not found.
        """
        invoice = self._pos_repository.get_invoice(sale_id)
        if invoice is None:
            raise ValueError("Sale not found")
        return invoice

    def search_customers(self, search: str) -> List[Dict[str, Any]]:
        """Search customers by name or phone.

        Args:
            search: Search term.

        Returns:
            List of matching customer dicts.
        """
        return self._pos_repository.search_customers(search)
