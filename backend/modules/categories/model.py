"""Category model representing the categories table."""

from datetime import datetime
from typing import Optional


class Category:
    """Represents a category record in the categories table.

    Attributes:
        id: Unique identifier for the category.
        parent_id: Identifier of the parent category, None for root categories.
        name: Name of the category.
        description: Description of the category.
        created_at: Timestamp when the category was created.
        updated_at: Timestamp when the category was last updated.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        parent_id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        """Initialize a Category instance.

        Args:
            id: Unique identifier for the category.
            parent_id: Identifier of the parent category, None for root categories.
            name: Name of the category.
            description: Description of the category.
            created_at: Timestamp when the category was created.
            updated_at: Timestamp when the category was last updated.
        """
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert Category instance to dictionary.

        Returns:
            Dictionary representation of the category.
        """
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        """Create a Category instance from a dictionary.

        Args:
            data: Dictionary containing category data.

        Returns:
            Category instance created from the dictionary.
        """
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return cls(
            id=data.get("id"),
            parent_id=data.get("parent_id"),
            name=data.get("name"),
            description=data.get("description"),
            created_at=created_at,
            updated_at=updated_at,
        )

    def __str__(self) -> str:
        """Return string representation of the Category.

        Returns:
            String with category id and name.
        """
        return f"Category(id={self.id}, name={self.name})"

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()
