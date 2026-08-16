"""Inventory audit and audit item models representing database tables."""

from datetime import datetime
from typing import Optional


class InventoryAuditItem:
    """Represents a product row within an inventory audit.

    Attributes:
        id: Unique identifier for the audit item.
        audit_id: Foreign key referencing inventory_audits.id.
        product_id: Foreign key referencing products.id.
        product_name: Product name (from a join).
        system_quantity: Stock quantity recorded in the system at audit time.
        counted_quantity: Physically counted quantity entered by the user.
        difference: counted_quantity - system_quantity.
        notes: Optional free-text notes about the item.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        audit_id: Optional[int] = None,
        product_id: Optional[int] = None,
        product_name: Optional[str] = None,
        system_quantity: int = 0,
        counted_quantity: int = 0,
        difference: int = 0,
        notes: Optional[str] = None,
    ) -> None:
        """Initialize an InventoryAuditItem instance.

        Args:
            id: Unique identifier for the audit item.
            audit_id: Foreign key referencing inventory_audits.id.
            product_id: Foreign key referencing products.id.
            product_name: Product name.
            system_quantity: Stock quantity in the system at audit time.
            counted_quantity: Physically counted quantity.
            difference: counted_quantity - system_quantity.
            notes: Optional free-text notes.
        """
        self.id = id
        self.audit_id = audit_id
        self.product_id = product_id
        self.product_name = product_name
        self.system_quantity = system_quantity
        self.counted_quantity = counted_quantity
        self.difference = difference
        self.notes = notes

    def to_dict(self) -> dict:
        """Convert InventoryAuditItem instance to dictionary.

        Returns:
            Dictionary representation of the audit item.
        """
        result = {
            "id": self.id,
            "audit_id": self.audit_id,
            "product_id": self.product_id,
            "system_quantity": self.system_quantity,
            "counted_quantity": self.counted_quantity,
            "difference": self.difference,
            "notes": self.notes,
        }
        if self.product_name is not None:
            result["product_name"] = self.product_name
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "InventoryAuditItem":
        """Create an InventoryAuditItem instance from a dictionary.

        Args:
            data: Dictionary containing audit item data.

        Returns:
            InventoryAuditItem instance created from the dictionary.
        """
        return cls(
            id=data.get("id"),
            audit_id=data.get("audit_id"),
            product_id=data.get("product_id"),
            product_name=data.get("product_name"),
            system_quantity=data.get("system_quantity", 0) or 0,
            counted_quantity=data.get("counted_quantity", 0) or 0,
            difference=data.get("difference", 0) or 0,
            notes=data.get("notes"),
        )

    def __str__(self) -> str:
        """Return string representation of the audit item.

        Returns:
            String with item id and product id.
        """
        return f"InventoryAuditItem(id={self.id}, product_id={self.product_id})"

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()


class InventoryAudit:
    """Represents an inventory audit (physical stock count) header.

    Attributes:
        id: Unique identifier for the audit.
        name: Human-readable audit name.
        location: Location being audited (warehouse or store).
        warehouse_id: Warehouse the audit applies to. Built-in audits
            default to WH-MAIN for warehouse and STORE for store.
        status: Audit status (open, completed, cancelled).
        created_by: ID of the user who created the audit.
        created_by_name: Full name of the creating user (from a join).
        total_items: Number of products in the audit (from a join).
        counted_items: Number of items with a counted quantity entered.
        adjusted_items: Number of items whose difference is non-zero.
        total_difference: Sum of all item differences.
        started_at: Timestamp when the audit was created.
        completed_at: Timestamp when the audit was completed.
        created_at: Timestamp when the record was created.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        location: Optional[str] = None,
        warehouse_id: Optional[int] = None,
        status: Optional[str] = None,
        created_by: Optional[int] = None,
        created_by_name: Optional[str] = None,
        total_items: int = 0,
        counted_items: int = 0,
        adjusted_items: int = 0,
        total_difference: int = 0,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        """Initialize an InventoryAudit instance.

        Args:
            id: Unique identifier for the audit.
            name: Human-readable audit name.
            location: Location being audited.
            warehouse_id: Warehouse the audit applies to.
            status: Audit status.
            created_by: ID of the creating user.
            created_by_name: Full name of the creating user.
            total_items: Number of products in the audit.
            counted_items: Number of items with counted quantity entered.
            adjusted_items: Number of items with non-zero difference.
            total_difference: Sum of all item differences.
            started_at: Timestamp when the audit was created.
            completed_at: Timestamp when the audit was completed.
            created_at: Timestamp when the record was created.
        """
        self.id = id
        self.name = name
        self.location = location
        self.warehouse_id = warehouse_id
        self.status = status
        self.created_by = created_by
        self.created_by_name = created_by_name
        self.total_items = total_items
        self.counted_items = counted_items
        self.adjusted_items = adjusted_items
        self.total_difference = total_difference
        self.started_at = started_at or datetime.now()
        self.completed_at = completed_at
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert InventoryAudit instance to dictionary.

        Returns:
            Dictionary representation of the audit.
        """
        result = {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "warehouse_id": self.warehouse_id,
            "status": self.status,
            "created_by": self.created_by,
            "total_items": self.total_items,
            "counted_items": self.counted_items,
            "adjusted_items": self.adjusted_items,
            "total_difference": self.total_difference,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if self.created_by_name is not None:
            result["created_by_name"] = self.created_by_name
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "InventoryAudit":
        """Create an InventoryAudit instance from a dictionary.

        Args:
            data: Dictionary containing audit data.

        Returns:
            InventoryAudit instance created from the dictionary.
        """
        def _parse(value):
            if value and isinstance(value, str):
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            return value

        return cls(
            id=data.get("id"),
            name=data.get("name"),
            location=data.get("location"),
            warehouse_id=data.get("warehouse_id"),
            status=data.get("status"),
            created_by=data.get("created_by"),
            created_by_name=data.get("created_by_name"),
            total_items=data.get("total_items", 0) or 0,
            counted_items=data.get("counted_items", 0) or 0,
            adjusted_items=data.get("adjusted_items", 0) or 0,
            total_difference=data.get("total_difference", 0) or 0,
            started_at=_parse(data.get("started_at")),
            completed_at=_parse(data.get("completed_at")),
            created_at=_parse(data.get("created_at")),
        )

    def __str__(self) -> str:
        """Return string representation of the audit.

        Returns:
            String with audit id, name and status.
        """
        return f"InventoryAudit(id={self.id}, name={self.name}, status={self.status})"

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()
