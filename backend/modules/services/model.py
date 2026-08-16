"""Service model representing the services table."""

from datetime import datetime
from decimal import Decimal
from typing import Optional


class Service:
    """Represents a service record in the services table.

    Attributes:
        id: Unique identifier for the service.
        category_id: Foreign key to the service_categories table.
        name: Name of the service.
        description: Description of the service.
        price: Price of the service.
        duration_days: Duration of the service in days.
        status: Service status (active, inactive).
        created_at: Timestamp when the service was created.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        category_id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[Decimal] = None,
        duration_days: Optional[int] = None,
        status: str = "active",
        created_at: Optional[datetime] = None
    ) -> None:
        """Initialize a Service instance.

        Args:
            id: Unique identifier for the service.
            category_id: Foreign key to the service_categories table.
            name: Name of the service.
            description: Description of the service.
            price: Price of the service.
            duration_days: Duration of the service in days.
            status: Service status (active, inactive).
            created_at: Timestamp when the service was created.
        """
        self.id = id
        self.category_id = category_id
        self.name = name
        self.description = description
        self.price = price
        self.duration_days = duration_days
        self.status = status
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert Service instance to dictionary.

        Returns:
            Dictionary representation of the service.
        """
        return {
            "id": self.id,
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price) if self.price else None,
            "duration_days": self.duration_days,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Service":
        """Create a Service instance from a dictionary.

        Args:
            data: Dictionary containing service data.

        Returns:
            Service instance created from the dictionary.
        """
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        price = data.get("price")
        if price is not None and not isinstance(price, Decimal):
            price = Decimal(str(price))

        return cls(
            id=data.get("id"),
            category_id=data.get("category_id"),
            name=data.get("name"),
            description=data.get("description"),
            price=price,
            duration_days=data.get("duration_days"),
            status=data.get("status", "active"),
            created_at=created_at
        )

    def __str__(self) -> str:
        """Return string representation of the Service.

        Returns:
            String with service id, name, and price.
        """
        return f"Service(id={self.id}, name={self.name}, price={self.price})"

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()
