"""ServiceCategory model representing the service_categories table."""

from datetime import datetime
from typing import Optional


class ServiceCategory:
    """Represents a service category record in the service_categories table.

    Attributes:
        id: Unique identifier for the category.
        name: Name of the service category.
        description: Description of the service category.
        created_at: Timestamp when the category was created.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None
    ) -> None:
        """Initialize a ServiceCategory instance.

        Args:
            id: Unique identifier for the category.
            name: Name of the service category.
            description: Description of the service category.
            created_at: Timestamp when the category was created.
        """
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert ServiceCategory instance to dictionary.

        Returns:
            Dictionary representation of the service category.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ServiceCategory":
        """Create a ServiceCategory instance from a dictionary.

        Args:
            data: Dictionary containing service category data.

        Returns:
            ServiceCategory instance created from the dictionary.
        """
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            created_at=created_at
        )

    def __str__(self) -> str:
        """Return string representation of the ServiceCategory.

        Returns:
            String with category id and name.
        """
        return f"ServiceCategory(id={self.id}, name={self.name})"

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()
