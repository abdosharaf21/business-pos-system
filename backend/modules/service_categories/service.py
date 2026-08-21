"""ServiceCategory service for category-related business logic."""

from typing import Optional, List

from backend.modules.service_categories.model import ServiceCategory
from backend.modules.service_categories.repository import ServiceCategoryRepository
from backend.modules.service_categories.validator import ServiceCategoryValidator


class ServiceCategoryService:
    """Service for service category business operations.

    Handles all category-related business logic including creation,
    updates, and deletion. Communicates only with ServiceCategoryRepository
    for data access.
    """

    def __init__(self, category_repository: ServiceCategoryRepository) -> None:
        """Initialize ServiceCategoryService with a ServiceCategoryRepository.

        Args:
            category_repository: Repository for service category database operations.
        """
        self._category_repository = category_repository

    def create_category(self, data: dict) -> ServiceCategory:
        """Create a new service category.

        Args:
            data: Dictionary containing category information.

        Returns:
            Created ServiceCategory instance.

        Raises:
            ValueError: If required fields are missing.
            ValueError: If validation fails.
        """
        validated = ServiceCategoryValidator.validate_create_category(data)

        category = ServiceCategory(
            name=validated["name"],
            description=validated["description"]
        )

        return self._category_repository.create(category)

    def get_category(self, category_id: int) -> ServiceCategory:
        """Retrieve a category by its unique identifier.

        Args:
            category_id: The unique identifier of the category.

        Returns:
            ServiceCategory instance if found.

        Raises:
            ValueError: If category not found.
        """
        category = self._category_repository.get_by_id(category_id)
        if category is None:
            raise ValueError("Category not found")
        return category

    def get_all_categories(self) -> List[ServiceCategory]:
        """Retrieve all service categories.

        Returns:
            List of ServiceCategory instances.
        """
        return self._category_repository.get_all()

    def update_category(self, category_id: int, data: dict) -> ServiceCategory:
        """Update an existing service category.

        Args:
            category_id: The unique identifier of the category.
            data: Dictionary containing fields to update.

        Returns:
            Updated ServiceCategory instance.

        Raises:
            ValueError: If category not found.
            ValueError: If validation fails.
        """
        validated = ServiceCategoryValidator.validate_update_category(data)

        category = self._category_repository.get_by_id(category_id)
        if category is None:
            raise ValueError("Category not found")

        if "name" in validated:
            category.name = validated["name"]
        if "description" in validated:
            category.description = validated["description"]

        updated = self._category_repository.update(category)
        if updated is None:
            raise ValueError("Failed to update category")
        return updated

    def delete_category(self, category_id: int) -> bool:
        """Delete a service category.

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
