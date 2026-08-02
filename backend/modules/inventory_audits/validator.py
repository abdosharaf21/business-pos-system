"""Inventory audit validator for audit input validation."""

from typing import Any, Dict, Optional


class InventoryAuditValidator:
    """Validator for inventory audit input data.

    Handles all validation logic for audit-related operations.
    Does not access the database or execute business logic.
    """

    MAX_NAME_LENGTH = 150
    MAX_NOTES_LENGTH = 255

    VALID_LOCATIONS = ("warehouse", "store")

    VALID_STATUSES = ("open", "completed", "cancelled")

    @staticmethod
    def validate_name(name: str) -> str:
        """Validate audit name format and length.

        Args:
            name: Audit name to validate.

        Returns:
            Stripped and validated name.

        Raises:
            ValueError: If name is missing or too long.
        """
        if not name:
            raise ValueError("Audit name is required")

        name = name.strip()

        if len(name) == 0:
            raise ValueError("Audit name cannot be empty")

        if len(name) > InventoryAuditValidator.MAX_NAME_LENGTH:
            raise ValueError(
                f"Audit name must not exceed "
                f"{InventoryAuditValidator.MAX_NAME_LENGTH} characters"
            )

        return name

    @staticmethod
    def validate_location(location: str) -> str:
        """Validate audit location is one of the supported locations.

        Args:
            location: Location to validate (warehouse or store).

        Returns:
            Validated location string.

        Raises:
            ValueError: If location is invalid.
        """
        if not location:
            raise ValueError("Audit location is required")

        location = location.strip().lower()

        if location not in InventoryAuditValidator.VALID_LOCATIONS:
            raise ValueError(
                f"Invalid audit location. Must be one of: "
                f"{', '.join(InventoryAuditValidator.VALID_LOCATIONS)}"
            )

        return location

    @staticmethod
    def validate_status(status: str) -> str:
        """Validate audit status is one of the supported statuses.

        Args:
            status: Status to validate.

        Returns:
            Validated status string.

        Raises:
            ValueError: If status is invalid.
        """
        if not status:
            raise ValueError("Audit status is required")

        status = status.strip().lower()

        if status not in InventoryAuditValidator.VALID_STATUSES:
            raise ValueError(
                f"Invalid audit status. Must be one of: "
                f"{', '.join(InventoryAuditValidator.VALID_STATUSES)}"
            )

        return status

    @staticmethod
    def validate_counted_quantity(value: Any) -> int:
        """Validate a counted quantity is a non-negative integer.

        Args:
            value: Counted quantity to validate.

        Returns:
            Validated non-negative integer quantity.

        Raises:
            ValueError: If quantity is missing or not a non-negative integer.
        """
        if value is None or value == "":
            raise ValueError("Counted quantity is required")

        try:
            quantity = int(value)
        except (TypeError, ValueError):
            raise ValueError("Counted quantity must be a valid number")

        if quantity < 0:
            raise ValueError("Counted quantity cannot be negative")

        return quantity

    @staticmethod
    def validate_notes(notes: str) -> Optional[str]:
        """Validate audit item notes format and length.

        Args:
            notes: Notes to validate.

        Returns:
            Stripped notes string or None if empty.

        Raises:
            ValueError: If notes exceed the maximum length.
        """
        if not notes:
            return None

        notes = notes.strip()

        if len(notes) == 0:
            return None

        if len(notes) > InventoryAuditValidator.MAX_NOTES_LENGTH:
            raise ValueError(
                f"Notes must not exceed "
                f"{InventoryAuditValidator.MAX_NOTES_LENGTH} characters"
            )

        return notes

    @staticmethod
    def validate_items(items: Any) -> Dict[int, Dict[str, Any]]:
        """Validate audit item count updates.

        Args:
            items: List of item dictionaries with product_id and counted_quantity.

        Returns:
            Dictionary mapping product_id to validated counted_quantity and notes.

        Raises:
            ValueError: If items is missing or contains invalid entries.
        """
        if not items:
            raise ValueError("Audit items are required")

        if not isinstance(items, list):
            raise ValueError("Audit items must be a list")

        validated: Dict[int, Dict[str, Any]] = {}

        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Each audit item must be an object")

            product_id = item.get("product_id")
            try:
                product_id = int(product_id)
            except (TypeError, ValueError):
                raise ValueError("Each audit item must have a valid product_id")

            if product_id <= 0:
                raise ValueError("Each audit item must have a valid product_id")

            validated[product_id] = {
                "product_id": product_id,
                "counted_quantity": InventoryAuditValidator.validate_counted_quantity(
                    item.get("counted_quantity")
                ),
                "notes": InventoryAuditValidator.validate_notes(item.get("notes")),
            }

        return validated

    @staticmethod
    def validate_create_audit(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate create audit data.

        Args:
            data: Dictionary containing audit information.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Audit data is required")

        return {
            "name": InventoryAuditValidator.validate_name(data.get("name")),
            "location": InventoryAuditValidator.validate_location(data.get("location")),
        }

    @staticmethod
    def validate_update_audit(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update audit data.

        Args:
            data: Dictionary containing audit fields to update.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Update data is required")

        validated = {}

        if "name" in data:
            validated["name"] = InventoryAuditValidator.validate_name(data["name"])

        if "status" in data:
            validated["status"] = InventoryAuditValidator.validate_status(data["status"])

        if "items" in data:
            validated["items"] = InventoryAuditValidator.validate_items(data["items"])

        if not validated:
            raise ValueError("No valid fields to update")

        return validated
