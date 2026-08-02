"""Category service for category-related business logic."""

from typing import Optional, List

import mysql.connector

from backend.modules.categories.model import Category
from backend.modules.categories.repository import CategoryRepository
from backend.modules.categories.validator import CategoryValidator


class CategoryService:
    """Service for category business operations.

    Handles all category-related business logic including creation,
    updates, deletion, and hierarchy management. Communicates only
    with CategoryRepository for data access.
    """

    def __init__(self, category_repository: CategoryRepository) -> None:
        """Initialize CategoryService with a CategoryRepository.

        Args:
            category_repository: Repository for category database operations.
        """
        self._category_repository = category_repository

    def _ensure_parent_exists(self, parent_id: Optional[int]) -> Optional[Category]:
        """Verify that a parent category exists.

        Args:
            parent_id: The parent category identifier, or None for a root.

        Returns:
            The parent Category instance or None for a root category.

        Raises:
            ValueError: If the parent category does not exist.
        """
        if parent_id is None:
            return None
        parent = self._category_repository.get_by_id(parent_id)
        if parent is None:
            raise ValueError("Parent category not found")
        return parent

    def _is_descendant(self, category_id: int, ancestor_id: int) -> bool:
        """Check whether a category is a descendant of another category.

        Args:
            category_id: The identifier of the category to check.
            ancestor_id: The identifier of the candidate ancestor.

        Returns:
            True if category_id is a descendant of ancestor_id.
        """
        current = self._category_repository.get_by_id(category_id)
        visited = set()
        while current is not None and current.parent_id is not None:
            if current.parent_id in visited:
                return True
            visited.add(current.parent_id)
            if current.parent_id == ancestor_id:
                return True
            parent = self._category_repository.get_by_id(current.parent_id)
            if parent is None:
                return False
            current = parent
        return False

    def create_category(self, data: dict) -> Category:
        """Create a new category.

        Args:
            data: Dictionary containing category information.

        Returns:
            Created Category instance.

        Raises:
            ValueError: If required fields are missing.
            ValueError: If name already exists.
            ValueError: If parent category is invalid.
            ValueError: If validation fails.
        """
        validated = CategoryValidator.validate_create_category(data)

        if self._category_repository.exists_by_name(validated["name"]):
            raise ValueError("A category with this name already exists")

        self._ensure_parent_exists(validated["parent_id"])

        category = Category(
            parent_id=validated["parent_id"],
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

    def get_category_tree(self) -> List[dict]:
        """Retrieve all categories organized as a nested tree.

        Root categories are returned first, each with its children
        nested recursively under the ``children`` key. Children are
        ordered alphabetically by name.

        Returns:
            List of nested category dictionaries.
        """
        categories = self._category_repository.get_all()
        nodes = {category.id: self._category_dict(category) for category in categories}

        for category in categories:
            node = nodes[category.id]
            parent_id = category.parent_id
            if parent_id is not None and parent_id in nodes:
                nodes[parent_id]["children"].append(node)

        for node in nodes.values():
            node["children"].sort(key=lambda child: (child["name"] or "").lower())

        roots = [nodes[category.id] for category in categories if category.parent_id is None]
        roots.sort(key=lambda root: (root["name"] or "").lower())
        return roots

    @staticmethod
    def _category_dict(category: Category) -> dict:
        """Build a nested tree dictionary for a category.

        Args:
            category: The Category instance.

        Returns:
            Dictionary with children placeholder.
        """
        data = category.to_dict()
        data["children"] = []
        return data

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
            ValueError: If parent would create a cycle.
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

        if "parent_id" in validated:
            new_parent_id = validated["parent_id"]
            if new_parent_id == category_id:
                raise ValueError("A category cannot be its own parent")
            self._ensure_parent_exists(new_parent_id)
            if new_parent_id is not None and self._is_descendant(new_parent_id, category_id):
                raise ValueError("A category cannot be moved under one of its own subcategories")
            category.parent_id = new_parent_id

        updated = self._category_repository.update(category)
        if updated is None:
            raise ValueError("Failed to update category")
        return updated

    def delete_category(self, category_id: int) -> bool:
        """Delete a category.

        A category that still contains subcategories cannot be deleted.
        A category that is referenced by products cannot be deleted.

        Args:
            category_id: The unique identifier of the category.

        Returns:
            True if category was deleted successfully.

        Raises:
            ValueError: If category not found.
            ValueError: If the category has subcategories or products.
        """
        category = self._category_repository.get_by_id(category_id)
        if category is None:
            raise ValueError("Category not found")

        if self._category_repository.count_children(category_id) > 0:
            raise ValueError("Cannot delete a category that has subcategories")

        try:
            deleted = self._category_repository.delete(category_id)
        except mysql.connector.IntegrityError as e:
            if e.errno == 1451:
                raise ValueError("Cannot delete a category that is assigned to products")
            raise

        if not deleted:
            raise ValueError("Category not found")
        return True
