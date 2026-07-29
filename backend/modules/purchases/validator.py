"""Purchase validator for purchase input validation."""

from typing import Dict, Any, List


class PurchaseValidator:
    """Validator for purchase input data.

    Handles all validation logic for purchase-related operations.
    Does not access the database or execute business logic.
    """

    @staticmethod
    def validate_quantity(value: Any) -> int:
        """Validate item quantity.

        Args:
            value: Quantity to validate.

        Returns:
            Validated integer quantity.

        Raises:
            ValueError: If quantity is invalid.
        """
        try:
            qty = int(value)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be a valid integer")

        if qty <= 0:
            raise ValueError("Quantity must be greater than zero")

        return qty

    @staticmethod
    def validate_cost_price(value: Any) -> float:
        """Validate item cost price.

        Args:
            value: Cost price to validate.

        Returns:
            Validated float cost price.

        Raises:
            ValueError: If cost price is invalid.
        """
        try:
            price = float(value)
        except (TypeError, ValueError):
            raise ValueError("Cost price must be a valid number")

        if price < 0:
            raise ValueError("Cost price must be greater than or equal to 0")

        return price

    @staticmethod
    def validate_product_id(value: Any) -> int:
        """Validate product ID.

        Args:
            value: Product ID to validate.

        Returns:
            Validated integer product ID.

        Raises:
            ValueError: If product ID is invalid.
        """
        try:
            pid = int(value)
        except (TypeError, ValueError):
            raise ValueError("Product ID must be a valid integer")

        if pid <= 0:
            raise ValueError("Invalid product ID")

        return pid

    @staticmethod
    def validate_supplier_id(value: Any) -> int:
        """Validate supplier ID.

        Args:
            value: Supplier ID to validate.

        Returns:
            Validated integer supplier ID.

        Raises:
            ValueError: If supplier ID is invalid.
        """
        if value is None:
            raise ValueError("Supplier is required")

        try:
            sid = int(value)
        except (TypeError, ValueError):
            raise ValueError("Supplier ID must be a valid integer")

        if sid <= 0:
            raise ValueError("Invalid supplier ID")

        return sid

    @staticmethod
    def validate_item(item: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate a single purchase item.

        Args:
            item: Item dictionary with product_id, quantity, cost_price.
            index: Zero-based index of the item for error messages.

        Returns:
            Validated item dictionary.

        Raises:
            ValueError: If item validation fails.
        """
        if not item or not isinstance(item, dict):
            raise ValueError(f"Item at index {index} is invalid")

        validated = {
            "product_id": PurchaseValidator.validate_product_id(item.get("product_id")),
            "quantity": PurchaseValidator.validate_quantity(item.get("quantity")),
            "cost_price": PurchaseValidator.validate_cost_price(item.get("cost_price")),
        }

        return validated

    @staticmethod
    def validate_supplier_name(value: Any) -> str:
        """Validate supplier name.

        Args:
            value: Supplier name to validate.

        Returns:
            Stripped validated name.

        Raises:
            ValueError: If name is invalid.
        """
        if not value:
            raise ValueError("Supplier name is required")

        name = str(value).strip()

        if not name:
            raise ValueError("Supplier name cannot be empty")

        if len(name) > 150:
            raise ValueError("Supplier name must not exceed 150 characters")

        return name

    @staticmethod
    def validate_supplier_phone(value: Any) -> str:
        """Validate supplier phone.

        Args:
            value: Supplier phone to validate.

        Returns:
            Stripped validated phone.

        Raises:
            ValueError: If phone is invalid.
        """
        if not value:
            raise ValueError("Phone number is required")

        phone = str(value).strip()

        if not phone:
            raise ValueError("Phone number cannot be empty")

        if len(phone) > 20:
            raise ValueError("Phone number must not exceed 20 characters")

        return phone

    @staticmethod
    def validate_supplier_email(value: Any) -> str:
        """Validate supplier email.

        Args:
            value: Supplier email to validate.

        Returns:
            Stripped validated email, or None.

        Raises:
            ValueError: If email format is invalid.
        """
        if not value:
            return None

        email = str(value).strip()

        if not email:
            return None

        if len(email) > 150:
            raise ValueError("Email must not exceed 150 characters")

        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Invalid email format")

        return email

    @staticmethod
    def validate_supplier_address(value: Any) -> str:
        """Validate supplier address.

        Args:
            value: Supplier address to validate.

        Returns:
            Stripped validated address, or None.
        """
        if not value:
            return None

        address = str(value).strip()
        return address if address else None

    @staticmethod
    def validate_create_supplier(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate create supplier data.

        Args:
            data: Dictionary with name, phone, email, address.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Supplier data is required")

        return {
            "name": PurchaseValidator.validate_supplier_name(data.get("name")),
            "phone": PurchaseValidator.validate_supplier_phone(data.get("phone")),
            "email": PurchaseValidator.validate_supplier_email(data.get("email")),
            "address": PurchaseValidator.validate_supplier_address(data.get("address")),
        }

    @staticmethod
    def validate_create_purchase(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate create purchase data.

        Args:
            data: Dictionary with supplier_id and items array.

        Returns:
            Validated data dictionary with validated items.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Purchase data is required")

        items_data = data.get("items", [])

        if not items_data or not isinstance(items_data, list):
            raise ValueError("At least one item is required")

        validated = {
            "supplier_id": PurchaseValidator.validate_supplier_id(data.get("supplier_id")),
            "items": [],
        }

        for i, item in enumerate(items_data):
            validated["items"].append(PurchaseValidator.validate_item(item, i))

        return validated
