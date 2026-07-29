"""Inventory models representing inventory transactions and stock views."""

from datetime import datetime
from typing import Optional


class InventoryTransaction:
    """Represents an inventory transaction record.

    Attributes:
        id: Unique identifier for the transaction.
        product_id: ID of the product involved.
        transaction_type: Type of transaction (purchase, sale, adjustment, return).
        quantity: Quantity changed (positive = in, negative = out).
        reference_id: Optional reference to related sale/purchase.
        created_at: Timestamp when the transaction occurred.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        product_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        quantity: int = 0,
        reference_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.product_id = product_id
        self.transaction_type = transaction_type
        self.quantity = quantity
        self.reference_id = reference_id
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "transaction_type": self.transaction_type,
            "quantity": self.quantity,
            "reference_id": self.reference_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InventoryTransaction":
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        return cls(
            id=data.get("id"),
            product_id=data.get("product_id"),
            transaction_type=data.get("transaction_type"),
            quantity=data.get("quantity", 0),
            reference_id=data.get("reference_id"),
            created_at=created_at,
        )

    def __str__(self) -> str:
        return f"InventoryTransaction(id={self.id}, product_id={self.product_id}, type={self.transaction_type})"

    def __repr__(self) -> str:
        return self.__str__()
