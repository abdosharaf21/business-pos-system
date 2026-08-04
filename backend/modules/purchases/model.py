"""Purchase and PurchaseItem models representing the purchases and purchase_items tables."""

from datetime import datetime
from typing import Optional, List


class PurchaseItem:
    """Represents a line item in a purchase order.

    Attributes:
        id: Unique identifier for the purchase item.
        purchase_id: Foreign key to purchases table.
        product_id: Foreign key to products table.
        product_name: Optional product name from join.
        product_sku: Optional product SKU from join.
        quantity: Quantity purchased.
        cost_price: Cost price per unit.
        subtotal: Line total (quantity * cost_price).
        expiration_date: Optional expiration date of the batch (YYYY-MM-DD).
    """

    def __init__(
        self,
        id: Optional[int] = None,
        purchase_id: Optional[int] = None,
        product_id: Optional[int] = None,
        product_name: Optional[str] = None,
        product_sku: Optional[str] = None,
        quantity: int = 1,
        cost_price: float = 0.0,
        subtotal: float = 0.0,
        expiration_date: Optional[str] = None,
    ) -> None:
        """Initialize a PurchaseItem instance.

        Args:
            id: Unique identifier for the purchase item.
            purchase_id: Foreign key to purchases table.
            product_id: Foreign key to products table.
            product_name: Optional product name from join.
            product_sku: Optional product SKU from join.
            quantity: Quantity purchased.
            cost_price: Cost price per unit.
            subtotal: Line total.
            expiration_date: Optional expiration date of the batch (YYYY-MM-DD).
        """
        self.id = id
        self.purchase_id = purchase_id
        self.product_id = product_id
        self.product_name = product_name
        self.product_sku = product_sku
        self.quantity = quantity
        self.cost_price = cost_price
        self.subtotal = subtotal
        self.expiration_date = expiration_date

    def to_dict(self) -> dict:
        """Convert PurchaseItem instance to dictionary.

        Returns:
            Dictionary representation of the purchase item.
        """
        result = {
            "id": self.id,
            "purchase_id": self.purchase_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "cost_price": float(self.cost_price),
            "subtotal": float(self.subtotal),
            "expiration_date": self.expiration_date,
        }
        if self.product_name is not None:
            result["product_name"] = self.product_name
        if self.product_sku is not None:
            result["product_sku"] = self.product_sku
        return result

    def __str__(self) -> str:
        """Return string representation of the PurchaseItem.

        Returns:
            String with product id and quantity.
        """
        return f"PurchaseItem(product_id={self.product_id}, qty={self.quantity})"

    def __repr__(self) -> str:
        return self.__str__()


class Purchase:
    """Represents a purchase order record.

    Attributes:
        id: Unique identifier for the purchase.
        supplier_id: Foreign key to suppliers table.
        supplier_name: Optional supplier name from join.
        user_id: Foreign key to users table.
        user_name: Optional user name from join.
        invoice_number: Auto-generated unique invoice number.
        total_amount: Total amount of the purchase.
        status: Purchase status (pending/completed/cancelled).
        payment_method: Payment method used for the purchase.
        notes: Optional notes attached to the purchase.
        items: List of PurchaseItem instances.
        created_at: Timestamp when the purchase was created.
    """

    VALID_STATUSES = {"pending", "completed", "cancelled"}
    VALID_PAYMENT_METHODS = {"cash", "card", "transfer", "mixed", "vodafone_cash"}

    def __init__(
        self,
        id: Optional[int] = None,
        supplier_id: Optional[int] = None,
        supplier_name: Optional[str] = None,
        user_id: Optional[int] = None,
        user_name: Optional[str] = None,
        invoice_number: Optional[str] = None,
        total_amount: float = 0.0,
        status: str = "completed",
        payment_method: str = "cash",
        notes: Optional[str] = None,
        items: Optional[List[PurchaseItem]] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        """Initialize a Purchase instance.

        Args:
            id: Unique identifier for the purchase.
            supplier_id: Foreign key to suppliers table.
            supplier_name: Optional supplier name from join.
            user_id: Foreign key to users table.
            user_name: Optional user name from join.
            invoice_number: Auto-generated unique invoice number.
            total_amount: Total amount of the purchase.
            status: Purchase status.
            payment_method: Payment method used for the purchase.
            notes: Optional notes attached to the purchase.
            items: List of PurchaseItem instances.
            created_at: Timestamp when the purchase was created.
        """
        self.id = id
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.user_id = user_id
        self.user_name = user_name
        self.invoice_number = invoice_number
        self.total_amount = total_amount
        self.status = status
        self.payment_method = payment_method
        self.notes = notes
        self.items = items or []
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert Purchase instance to dictionary.

        Returns:
            Dictionary representation of the purchase.
        """
        result = {
            "id": self.id,
            "supplier_id": self.supplier_id,
            "user_id": self.user_id,
            "invoice_number": self.invoice_number,
            "total_amount": float(self.total_amount),
            "status": self.status,
            "payment_method": self.payment_method,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if self.supplier_name is not None:
            result["supplier_name"] = self.supplier_name
        if self.user_name is not None:
            result["user_name"] = self.user_name
        if self.items:
            result["items"] = [item.to_dict() for item in self.items]
        return result

    def __str__(self) -> str:
        """Return string representation of the Purchase.

        Returns:
            String with invoice number.
        """
        return f"Purchase(invoice={self.invoice_number}, total={self.total_amount})"

    def __repr__(self) -> str:
        return self.__str__()
