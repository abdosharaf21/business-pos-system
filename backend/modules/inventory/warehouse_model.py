"""Warehouse model representing the warehouses database table."""

from datetime import datetime
from typing import Optional


class Warehouse:
    """Represents a warehouse (storage location) in the system.

    The two built-in warehouses are ``WH-MAIN`` (warehouse location stock)
    and ``STORE`` (store location stock sold by the POS). Custom warehouses
    the user creates also use the ``warehouse`` location with their own
    ``warehouse_id``.

    Attributes:
        id: Unique identifier of the warehouse.
        name: Human-readable warehouse name.
        code: Unique short code used by the system (e.g. WH-MAIN).
        address: Optional physical address.
        manager_name: Optional name of the warehouse manager.
        phone: Optional contact phone.
        status: active or inactive.
        created_at: Timestamp when the record was created.
        updated_at: Timestamp when the record was last updated.
        stock_total: Total units of stock held in the warehouse.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        code: Optional[str] = None,
        address: Optional[str] = None,
        manager_name: Optional[str] = None,
        phone: Optional[str] = None,
        status: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        stock_total: int = 0,
    ) -> None:
        """Initialize a Warehouse instance.

        Args:
            id: Unique identifier of the warehouse.
            name: Human-readable warehouse name.
            code: Unique short code.
            address: Optional physical address.
            manager_name: Optional manager name.
            phone: Optional contact phone.
            status: active or inactive.
            created_at: Creation timestamp.
            updated_at: Last update timestamp.
            stock_total: Total units of stock in the warehouse.
        """
        self.id = id
        self.name = name
        self.code = code
        self.address = address
        self.manager_name = manager_name
        self.phone = phone
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.stock_total = int(stock_total or 0)

    def to_dict(self) -> dict:
        """Convert the Warehouse instance to a dictionary.

        Returns:
            Dictionary representation of the warehouse.
        """
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "address": self.address,
            "manager_name": self.manager_name,
            "phone": self.phone,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "stock_total": self.stock_total,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Warehouse":
        """Create a Warehouse instance from a dictionary.

        Args:
            data: Dictionary containing warehouse data.

        Returns:
            Warehouse instance created from the dictionary.
        """
        def _parse(value):
            if value and isinstance(value, str):
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            return value

        return cls(
            id=data.get("id"),
            name=data.get("name"),
            code=data.get("code"),
            address=data.get("address"),
            manager_name=data.get("manager_name"),
            phone=data.get("phone"),
            status=data.get("status"),
            created_at=_parse(data.get("created_at")),
            updated_at=_parse(data.get("updated_at")),
            stock_total=data.get("stock_total", 0),
        )

    def __str__(self) -> str:
        """Return a short string representation.

        Returns:
            String with id, name and code.
        """
        return f"Warehouse(id={self.id}, name={self.name}, code={self.code})"

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()
