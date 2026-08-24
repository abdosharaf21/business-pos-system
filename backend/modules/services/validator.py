"""Service validator for service input validation."""

from decimal import Decimal, InvalidOperation
from typing import Dict, Any, Optional


class ServiceValidator:
    """Validator for service input data.

    Handles all validation logic for service-related operations.
    Does not access the database or execute business logic.
    """

    VALID_STATUSES = ["active", "inactive"]
    MAX_NAME_LENGTH = 150
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_PRICE = Decimal("99999999.99")
    MIN_PRICE = Decimal("0.00")
    MAX_DURATION_DAYS = 3650
    MIN_DURATION_DAYS = 1

    @staticmethod
    def validate_name(name: str) -> str:
        """Validate service name format and length.

        Args:
            name: Service name to validate.

        Returns:
            Stripped and validated name.

        Raises:
            ValueError: If name is invalid.
        """
        if not name:
            raise ValueError("Service name is required")

        name = name.strip()

        if len(name) == 0:
            raise ValueError("Service name cannot be empty")

        if len(name) > ServiceValidator.MAX_NAME_LENGTH:
            raise ValueError(f"Service name must not exceed {ServiceValidator.MAX_NAME_LENGTH} characters")

        return name

    @staticmethod
    def validate_description(description: str) -> str:
        """Validate service description format and length.

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

        if len(description) > ServiceValidator.MAX_DESCRIPTION_LENGTH:
            raise ValueError(f"Description must not exceed {ServiceValidator.MAX_DESCRIPTION_LENGTH} characters")

        return description

    @staticmethod
    def validate_price(price) -> Decimal:
        """Validate service price.

        Args:
            price: Price to validate.

        Returns:
            Validated Decimal price.

        Raises:
            ValueError: If price is invalid.
        """
        if price is None:
            return None

        try:
            price = Decimal(str(price))
        except (InvalidOperation, TypeError):
            raise ValueError("Invalid price format")

        if price < ServiceValidator.MIN_PRICE:
            raise ValueError("Price cannot be negative")

        if price > ServiceValidator.MAX_PRICE:
            raise ValueError(f"Price must not exceed {ServiceValidator.MAX_PRICE}")

        return price

    @staticmethod
    def validate_duration_days(duration_days) -> int:
        """Validate service duration in days.

        Args:
            duration_days: Duration to validate.

        Returns:
            Validated duration as integer.

        Raises:
            ValueError: If duration is invalid.
        """
        if duration_days is None:
            return None

        try:
            duration_days = int(duration_days)
        except (ValueError, TypeError):
            raise ValueError("Duration must be a valid integer")

        if duration_days < ServiceValidator.MIN_DURATION_DAYS:
            raise ValueError(f"Duration must be at least {ServiceValidator.MIN_DURATION_DAYS} day")

        if duration_days > ServiceValidator.MAX_DURATION_DAYS:
            raise ValueError(f"Duration must not exceed {ServiceValidator.MAX_DURATION_DAYS} days")

        return duration_days

    @staticmethod
    def validate_category_id(category_id) -> Optional[int]:
        """Validate service category ID.

        Args:
            category_id: Category ID to validate.

        Returns:
            Validated category ID as integer, or None if not provided.
        """
        if category_id is None:
            return None

        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            raise ValueError("Category ID must be a valid integer")

        if category_id <= 0:
            raise ValueError("Category ID must be a positive number")

        return category_id

    @staticmethod
    def validate_status(status: str) -> str:
        """Validate service status.

        Args:
            status: Status to validate.

        Returns:
            Validated status.

        Raises:
            ValueError: If status is invalid.
        """
        if not status:
            return "active"

        status = status.strip().lower()

        if status not in ServiceValidator.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(ServiceValidator.VALID_STATUSES)}")

        return status

    @staticmethod
    def validate_create_service(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate create service data.

        Args:
            data: Dictionary containing service information.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Service data is required")

        validated = {
            "category_id": ServiceValidator.validate_category_id(data.get("category_id")),
            "name": ServiceValidator.validate_name(data.get("name")),
            "description": ServiceValidator.validate_description(data.get("description")),
            "price": ServiceValidator.validate_price(data.get("price")),
            "duration_days": ServiceValidator.validate_duration_days(data.get("duration_days")),
            "status": ServiceValidator.validate_status(data.get("status"))
        }

        return validated

    @staticmethod
    def validate_update_service(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update service data.

        Args:
            data: Dictionary containing service fields to update.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Update data is required")

        validated = {}

        if "category_id" in data:
            validated["category_id"] = ServiceValidator.validate_category_id(data["category_id"])

        if "name" in data:
            validated["name"] = ServiceValidator.validate_name(data["name"])

        if "description" in data:
            validated["description"] = ServiceValidator.validate_description(data["description"])

        if "price" in data:
            validated["price"] = ServiceValidator.validate_price(data["price"])

        if "duration_days" in data:
            validated["duration_days"] = ServiceValidator.validate_duration_days(data["duration_days"])

        if "status" in data:
            validated["status"] = ServiceValidator.validate_status(data["status"])

        if not validated:
            raise ValueError("No valid fields to update")

        return validated
