"""Customer model representing the customers table."""

from datetime import datetime
from typing import Optional


class Customer:
    """Represents a customer record in the customers table.

    Attributes:
        id: Unique identifier for the customer.
        name: Full name of the customer.
        phone: Phone number of the customer.
        email: Email address of the customer.
        address: Physical address of the customer.
        created_at: Timestamp when the customer was created.
        updated_at: Timestamp when the customer was last updated.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        """Initialize a Customer instance.

        Args:
            id: Unique identifier for the customer.
            name: Full name of the customer.
            phone: Phone number of the customer.
            email: Email address of the customer.
            address: Physical address of the customer.
            created_at: Timestamp when the customer was created.
            updated_at: Timestamp when the customer was last updated.
        """
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert Customer instance to dictionary.

        Returns:
            Dictionary representation of the customer.
        """
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Customer":
        """Create a Customer instance from a dictionary.

        Args:
            data: Dictionary containing customer data.

        Returns:
            Customer instance created from the dictionary.
        """
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return cls(
            id=data.get("id"),
            name=data.get("name"),
            phone=data.get("phone"),
            email=data.get("email"),
            address=data.get("address"),
            created_at=created_at,
            updated_at=updated_at,
        )

    def __str__(self) -> str:
        """Return string representation of the Customer.

        Returns:
            String with customer id and name.
        """
        return f"Customer(id={self.id}, name={self.name})"

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()
