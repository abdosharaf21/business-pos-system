"""Transfer and transfer item models representing the transfers tables."""

from datetime import datetime
from typing import List, Optional


class TransferItem:
    """Represents a product line within a stock transfer.

    Attributes:
        id: Unique identifier of the transfer item.
        transfer_id: Foreign key referencing transfers.id.
        product_id: Foreign key referencing products.id.
        product_name: Product name (from a join).
        product_barcode: Product barcode (from a join).
        quantity: Units to transfer.
        cost_price: Unit cost price recorded for valuation.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        transfer_id: Optional[int] = None,
        product_id: Optional[int] = None,
        product_name: Optional[str] = None,
        product_barcode: Optional[str] = None,
        quantity: int = 0,
        cost_price: float = 0.0,
    ) -> None:
        """Initialize a TransferItem instance.

        Args:
            id: Unique identifier of the transfer item.
            transfer_id: Foreign key referencing transfers.id.
            product_id: Foreign key referencing products.id.
            product_name: Product name.
            product_barcode: Product barcode.
            quantity: Units to transfer.
            cost_price: Unit cost price.
        """
        self.id = id
        self.transfer_id = transfer_id
        self.product_id = product_id
        self.product_name = product_name
        self.product_barcode = product_barcode
        self.quantity = quantity
        self.cost_price = cost_price

    def to_dict(self) -> dict:
        """Convert the TransferItem instance to a dictionary.

        Returns:
            Dictionary representation of the transfer item.
        """
        result = {
            "id": self.id,
            "transfer_id": self.transfer_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "cost_price": self.cost_price,
        }
        if self.product_name is not None:
            result["product_name"] = self.product_name
        if self.product_barcode is not None:
            result["product_barcode"] = self.product_barcode
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "TransferItem":
        """Create a TransferItem instance from a dictionary.

        Args:
            data: Dictionary containing transfer item data.

        Returns:
            TransferItem instance created from the dictionary.
        """
        return cls(
            id=data.get("id"),
            transfer_id=data.get("transfer_id"),
            product_id=data.get("product_id"),
            product_name=data.get("product_name"),
            product_barcode=data.get("product_barcode"),
            quantity=data.get("quantity", 0) or 0,
            cost_price=data.get("cost_price", 0) or 0,
        )

    def __str__(self) -> str:
        """Return a short string representation.

        Returns:
            String with id, product id and quantity.
        """
        return f"TransferItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})"

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()


class Transfer:
    """Represents a stock transfer between two warehouses.

    Creating a transfer only records intent; stock is moved when the
    transfer is completed.

    Attributes:
        id: Unique identifier of the transfer.
        transfer_number: Human-readable unique number (e.g. TRF-20260815-00001).
        source_warehouse_id: Warehouse the stock is transferred from.
        destination_warehouse_id: Warehouse the stock is transferred to.
        status: pending, completed, or cancelled.
        created_by: ID of the user who created the transfer.
        created_by_name: Full name of the creating user (from a join).
        completed_by: ID of the user who completed the transfer.
        completed_at: Timestamp when the transfer was completed.
        notes: Optional notes attached to the transfer.
        created_at: Timestamp when the transfer was created.
        source_name: Source warehouse name (from a join).
        destination_name: Destination warehouse name (from a join).
        items: List of TransferItem instances.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        transfer_number: Optional[str] = None,
        source_warehouse_id: Optional[int] = None,
        destination_warehouse_id: Optional[int] = None,
        status: Optional[str] = None,
        created_by: Optional[int] = None,
        created_by_name: Optional[str] = None,
        completed_by: Optional[int] = None,
        completed_at: Optional[datetime] = None,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        source_name: Optional[str] = None,
        destination_name: Optional[str] = None,
        items: Optional[List[TransferItem]] = None,
    ) -> None:
        """Initialize a Transfer instance.

        Args:
            id: Unique identifier of the transfer.
            transfer_number: Unique human-readable number.
            source_warehouse_id: Source warehouse id.
            destination_warehouse_id: Destination warehouse id.
            status: Transfer status.
            created_by: ID of the creating user.
            created_by_name: Full name of the creating user.
            completed_by: ID of the completing user.
            completed_at: Completion timestamp.
            notes: Optional notes.
            created_at: Creation timestamp.
            source_name: Source warehouse name.
            destination_name: Destination warehouse name.
            items: Transfer items.
        """
        self.id = id
        self.transfer_number = transfer_number
        self.source_warehouse_id = source_warehouse_id
        self.destination_warehouse_id = destination_warehouse_id
        self.status = status
        self.created_by = created_by
        self.created_by_name = created_by_name
        self.completed_by = completed_by
        self.completed_at = completed_at
        self.notes = notes
        self.created_at = created_at or datetime.now()
        self.source_name = source_name
        self.destination_name = destination_name
        self.items = items or []

    def to_dict(self) -> dict:
        """Convert the Transfer instance to a dictionary.

        Returns:
            Dictionary representation of the transfer.
        """
        result = {
            "id": self.id,
            "transfer_number": self.transfer_number,
            "source_warehouse_id": self.source_warehouse_id,
            "destination_warehouse_id": self.destination_warehouse_id,
            "status": self.status,
            "created_by": self.created_by,
            "completed_by": self.completed_by,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "items": [item.to_dict() for item in self.items],
        }
        if self.created_by_name is not None:
            result["created_by_name"] = self.created_by_name
        if self.source_name is not None:
            result["source_name"] = self.source_name
        if self.destination_name is not None:
            result["destination_name"] = self.destination_name
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Transfer":
        """Create a Transfer instance from a dictionary.

        Args:
            data: Dictionary containing transfer data.

        Returns:
            Transfer instance created from the dictionary.
        """
        def _parse(value):
            if value and isinstance(value, str):
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            return value

        items = data.get("items") or []
        return cls(
            id=data.get("id"),
            transfer_number=data.get("transfer_number"),
            source_warehouse_id=data.get("source_warehouse_id"),
            destination_warehouse_id=data.get("destination_warehouse_id"),
            status=data.get("status"),
            created_by=data.get("created_by"),
            created_by_name=data.get("created_by_name"),
            completed_by=data.get("completed_by"),
            completed_at=_parse(data.get("completed_at")),
            notes=data.get("notes"),
            created_at=_parse(data.get("created_at")),
            source_name=data.get("source_name"),
            destination_name=data.get("destination_name"),
            items=[TransferItem.from_dict(item) for item in items],
        )

    def __str__(self) -> str:
        """Return a short string representation.

        Returns:
            String with id, number and status.
        """
        return f"Transfer(id={self.id}, number={self.transfer_number}, status={self.status})"

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()
