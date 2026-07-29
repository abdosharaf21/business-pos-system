"""Category service for category-related business logic."""

from typing import Optional, List

from backend.modules.categories.model import Category
from backend.modules.categories.repository import CategoryRepository
from backend.modules.categories.validator import CategoryValidator


class CategoryService:
    """Service for category business operations.

    Handles all category-related business logic including creation,
    updates, and deletion. Communicates only with CategoryRepository
    for data access.
    """

    def __init__(self, category_repository: CategoryRepository) -> None:
        """Initialize CategoryService with a CategoryRepository.

        Args:
            category_repository: Repository for category database operations.
        """
        self._category_repository = category_repository

    def create_category(self, data: dict) -> Category:
        """Create a new category.

        Args:
            data: Dictionary containing category information.

        Returns:
            Created Category instance.

        Raises:
            ValueError: If required fields are missing.
            ValueError: If name already exists.
            ValueError: If validation fails.
        """
        validated = CategoryValidator.validate_create_category(data)

        if self._category_repository.exists_by_name(validated["name"]):
            raise ValueError("A category with this name already exists")

        category = Category(
            name=validated["name"],
            description=validated["description"],
        )

        return self._category_repository.create(category)

    def get_category(self, category_id: int) -> Category:
        """Retrieve a category by its unique identifier.

        Args:
            category_id: The unique identifier of the category.

        Returns:
            Category instance if found.

        Raises:
            ValueError: If category not found.
        """
        category = self._category_repository.get_by_id(category_id)
        if category is None:
            raise ValueError("Category not found")
        return category

    def get_all_categories(self) -> List[Category]:
        """Retrieve all categories.

        Returns:
            List of Category instances.
        """
        return self._category_repository.get_all()

    def update_category(self, category_id: int, data: dict) -> Category:
        """Update an existing category.

        Args:
            category_id: The unique identifier of the category.
            data: Dictionary containing fields to update.

        Returns:
            Updated Category instance.

        Raises:
            ValueError: If category not found.
            ValueError: If name already exists.
            ValueError: If validation fails.
        """
        validated = CategoryValidator.validate_update_category(data)

        category = self._category_repository.get_by_id(category_id)
        if category is None:
            raise ValueError("Category not found")

        if "name" in validated:
            existing = self._category_repository.exists_by_name(validated["name"])
            if existing and validated["name"] != category.name:
                raise ValueError("A category with this name already exists")
            category.name = validated["name"]

        if "description" in validated:
            category.description = validated["description"]

        updated = self._category_repository.update(category)
        if updated is None:
            raise ValueError("Failed to update category")
        return updated

    def delete_category(self, category_id: int) -> bool:
        """Delete a category.

        Args:
            category_id: The unique identifier of the category.

        Returns:
            True if category was deleted successfully.

        Raises:
            ValueError: If category not found.
        """
        deleted = self._category_repository.delete(category_id)
        if not deleted:
            raise ValueError("Category not found")
        return True
