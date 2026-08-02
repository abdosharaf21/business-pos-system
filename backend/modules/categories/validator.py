"""Category validator for category input validation."""

from typing import Dict, Any, Optional


class CategoryValidator:
    """Validator for category input data.

    Handles all validation logic for category-related operations.
    Does not access the database or execute business logic.
    """

    MAX_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 1000

    @staticmethod
    def validate_name(name: str) -> str:
        """Validate category name format and length.

        Args:
            name: Category name to validate.

        Returns:
            Stripped and validated name.

        Raises:
            ValueError: If name is invalid.
        """
        if not name:
            raise ValueError("Category name is required")

        name = name.strip()

        if len(name) == 0:
            raise ValueError("Category name cannot be empty")

        if len(name) > CategoryValidator.MAX_NAME_LENGTH:
            raise ValueError(
                f"Category name must not exceed {CategoryValidator.MAX_NAME_LENGTH} characters"
            )

        return name

    @staticmethod
    def validate_description(description: str) -> str:
        """Validate category description format and length.

        Args:
            description: Description to validate.

        Returns:
            Stripped and validated description.

        Raises:
            ValueError: If description is invalid.
        """
        if not description:
            return None

        description = description.strip()

        if len(description) > CategoryValidator.MAX_DESCRIPTION_LENGTH:
            raise ValueError(
                f"Description must not exceed {CategoryValidator.MAX_DESCRIPTION_LENGTH} characters"
            )

        return description

    @staticmethod
    def validate_parent_id(parent_id) -> Optional[int]:
        """Validate a category parent identifier.

        Args:
            parent_id: The parent category identifier, may be None for a root.

        Returns:
            The validated parent identifier or None for a root category.

        Raises:
            ValueError: If parent identifier is invalid.
        """
        if parent_id is None or parent_id == "":
            return None

        try:
            parent_id = int(parent_id)
        except (TypeError, ValueError):
            raise ValueError("Parent category is invalid")

        if parent_id < 1:
            raise ValueError("Parent category is invalid")

        return parent_id

    @staticmethod
    def validate_create_category(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate create category data.

        Args:
            data: Dictionary containing category information.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Category data is required")

        validated = {
            "name": CategoryValidator.validate_name(data.get("name")),
            "description": CategoryValidator.validate_description(data.get("description")),
            "parent_id": CategoryValidator.validate_parent_id(data.get("parent_id")),
        }

        return validated

    @staticmethod
    def validate_update_category(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update category data.

        Args:
            data: Dictionary containing category fields to update.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Update data is required")

        validated = {}

        if "name" in data:
            validated["name"] = CategoryValidator.validate_name(data["name"])

        if "description" in data:
            validated["description"] = CategoryValidator.validate_description(data["description"])

        if "parent_id" in data:
            validated["parent_id"] = CategoryValidator.validate_parent_id(data["parent_id"])

        if not validated:
            raise ValueError("No valid fields to update")

        return validated
