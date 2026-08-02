"""Inventory models representing stock levels and stock movements."""

from datetime import datetime
from typing import Optional


class StockLevel:
    """Represents the stock quantity of a product at a single location.

    Attributes:
        id: Unique identifier of the stock record.
        product_id: ID of the product.
        location: Location name (warehouse or store).
        quantity: Units currently available at this location.
        updated_at: Timestamp of the last change.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        product_id: Optional[int] = None,
        location: Optional[str] = None,
        quantity: int = 0,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.product_id = product_id
        self.location = location
        self.quantity = quantity
        self.updated_at = updated_at or datetime.now()

    def to_dict(self) -> dict:
        """Serialize the stock level to a dictionary.

        Returns:
            Dictionary representation of the stock level.
        """
        return {
            "id": self.id,
            "product_id": self.product_id,
            "location": self.location,
            "quantity": self.quantity,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StockLevel":
        """Create a StockLevel instance from a dictionary.

        Args:
            data: Dictionary with stock level fields.

        Returns:
            Populated StockLevel instance.
        """
        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        return cls(
            id=data.get("id"),
            product_id=data.get("product_id"),
            location=data.get("location"),
            quantity=data.get("quantity", 0),
            updated_at=updated_at,
        )

    def __str__(self) -> str:
        return (
            f"StockLevel(id={self.id}, product_id={self.product_id}, "
            f"location={self.location}, quantity={self.quantity})"
        )

    def __repr__(self) -> str:
        return self.__str__()


class StockMovement:
    """Represents a stock movement record.

    Attributes:
        id: Unique identifier of the movement.
        product_id: ID of the product involved.
        from_location: Location the stock moved from (None for inbound).
        to_location: Location the stock moved to (None for outbound).
        quantity: Quantity moved (always positive in the record).
        movement_type: Type of movement (transfer, sale, purchase, ...).
        reference: Optional external reference (invoice number, etc.).
        notes: Optional human-readable note.
        user_id: ID of the user who performed the movement.
        created_at: Timestamp when the movement occurred.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        product_id: Optional[int] = None,
        from_location: Optional[str] = None,
        to_location: Optional[str] = None,
        quantity: int = 0,
        movement_type: Optional[str] = None,
        reference: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.product_id = product_id
        self.from_location = from_location
        self.to_location = to_location
        self.quantity = quantity
        self.movement_type = movement_type
        self.reference = reference
        self.notes = notes
        self.user_id = user_id
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """Serialize the movement to a dictionary.

        Returns:
            Dictionary representation of the movement.
        """
        return {
            "id": self.id,
            "product_id": self.product_id,
            "from_location": self.from_location,
            "to_location": self.to_location,
            "quantity": self.quantity,
            "movement_type": self.movement_type,
            "reference": self.reference,
            "notes": self.notes,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StockMovement":
        """Create a StockMovement instance from a dictionary.

        Args:
            data: Dictionary with movement fields.

        Returns:
            Populated StockMovement instance.
        """
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        return cls(
            id=data.get("id"),
            product_id=data.get("product_id"),
            from_location=data.get("from_location"),
            to_location=data.get("to_location"),
            quantity=data.get("quantity", 0),
            movement_type=data.get("movement_type"),
            reference=data.get("reference"),
            notes=data.get("notes"),
            user_id=data.get("user_id"),
            created_at=created_at,
        )

    def __str__(self) -> str:
        return (
            f"StockMovement(id={self.id}, product_id={self.product_id}, "
            f"type={self.movement_type}, qty={self.quantity})"
        )

    def __repr__(self) -> str:
        return self.__str__()
