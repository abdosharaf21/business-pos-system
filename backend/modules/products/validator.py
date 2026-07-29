"""Product validator for product input validation."""

from typing import Dict, Any, Optional


class ProductValidator:
    """Validator for product input data.

    Handles all validation logic for product-related operations.
    Does not access the database or execute business logic.
    """

    MAX_NAME_LENGTH = 150
    MAX_SKU_LENGTH = 50
    MAX_BARCODE_LENGTH = 50
    MAX_DESCRIPTION_LENGTH = 1000

    VALID_STATUSES = {"active", "inactive"}

    @staticmethod
    def validate_name(name: Any) -> str:
        """Validate product name format and length.

        Args:
            name: Product name to validate.

        Returns:
            Stripped and validated name.

        Raises:
            ValueError: If name is invalid.
        """
        if not name:
            raise ValueError("Product name is required")

        name = str(name).strip()

        if len(name) == 0:
            raise ValueError("Product name cannot be empty")

        if len(name) > ProductValidator.MAX_NAME_LENGTH:
            raise ValueError(
                f"Product name must not exceed {ProductValidator.MAX_NAME_LENGTH} characters"
            )

        return name

    @staticmethod
    def validate_sku(sku: Any) -> Optional[str]:
        """Validate product SKU format and length.

        Args:
            sku: SKU to validate.

        Returns:
            Stripped and validated SKU, or None.

        Raises:
            ValueError: If SKU is invalid.
        """
        if not sku:
            return None

        sku = str(sku).strip()

        if len(sku) == 0:
            return None

        if len(sku) > ProductValidator.MAX_SKU_LENGTH:
            raise ValueError(
                f"SKU must not exceed {ProductValidator.MAX_SKU_LENGTH} characters"
            )

        return sku

    @staticmethod
    def validate_barcode(barcode: Any) -> str:
        """Validate product barcode format and length.

        Args:
            barcode: Barcode to validate.

        Returns:
            Stripped and validated barcode.

        Raises:
            ValueError: If barcode is invalid.
        """
        if not barcode:
            raise ValueError("Barcode is required")

        barcode = str(barcode).strip()

        if len(barcode) == 0:
            raise ValueError("Barcode cannot be empty")

        if len(barcode) > ProductValidator.MAX_BARCODE_LENGTH:
            raise ValueError(
                f"Barcode must not exceed {ProductValidator.MAX_BARCODE_LENGTH} characters"
            )

        return barcode

    @staticmethod
    def validate_description(description: Any) -> Optional[str]:
        """Validate product description format and length.

        Args:
            description: Description to validate.

        Returns:
            Stripped and validated description, or None.

        Raises:
            ValueError: If description is invalid.
        """
        if not description:
            return None

        description = str(description).strip()

        if len(description) > ProductValidator.MAX_DESCRIPTION_LENGTH:
            raise ValueError(
                f"Description must not exceed {ProductValidator.MAX_DESCRIPTION_LENGTH} characters"
            )

        return description if description else None

    @staticmethod
    def validate_positive_decimal(value: Any, field_name: str) -> float:
        """Validate a decimal value is non-negative.

        Args:
            value: Value to validate.
            field_name: Name of the field for error messages.

        Returns:
            Validated float value.

        Raises:
            ValueError: If value is negative or not a valid number.
        """
        try:
            val = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field_name} must be a valid number")

        if val < 0:
            raise ValueError(f"{field_name} must be greater than or equal to 0")

        return val

    @staticmethod
    def validate_positive_int(value: Any, field_name: str) -> int:
        """Validate an integer value is non-negative.

        Args:
            value: Value to validate.
            field_name: Name of the field for error messages.

        Returns:
            Validated integer value.

        Raises:
            ValueError: If value is negative or not a valid integer.
        """
        try:
            val = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field_name} must be a valid integer")

        if val < 0:
            raise ValueError(f"{field_name} must be greater than or equal to 0")

        return val

    @staticmethod
    def validate_category_id(value: Any) -> int:
        """Validate category ID is a positive integer.

        Args:
            value: Category ID to validate.

        Returns:
            Validated category ID.

        Raises:
            ValueError: If category ID is invalid.
        """
        try:
            val = int(value)
        except (TypeError, ValueError):
            raise ValueError("Category ID must be a valid integer")

        if val <= 0:
            raise ValueError("Category ID must be a positive integer")

        return val

    @staticmethod
    def validate_status(value: Any) -> str:
        """Validate product status.

        Args:
            value: Status to validate.

        Returns:
            Validated status string.

        Raises:
            ValueError: If status is invalid.
        """
        if not value:
            return "active"

        status = str(value).strip().lower()

        if status not in ProductValidator.VALID_STATUSES:
            raise ValueError(
                f"Status must be one of: {', '.join(sorted(ProductValidator.VALID_STATUSES))}"
            )

        return status

    @staticmethod
    def validate_create_product(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate create product data.

        Args:
            data: Dictionary containing product information.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Product data is required")

        validated = {
            "name": ProductValidator.validate_name(data.get("name")),
            "sku": ProductValidator.validate_sku(data.get("sku")),
            "barcode": ProductValidator.validate_barcode(data.get("barcode")),
            "category_id": ProductValidator.validate_category_id(data.get("category_id")),
            "description": ProductValidator.validate_description(data.get("description")),
            "purchase_price": ProductValidator.validate_positive_decimal(
                data.get("purchase_price", 0), "Purchase price"
            ),
            "selling_price": ProductValidator.validate_positive_decimal(
                data.get("selling_price", 0), "Selling price"
            ),
            "quantity": ProductValidator.validate_positive_int(
                data.get("quantity", 0), "Quantity"
            ),
            "minimum_stock": ProductValidator.validate_positive_int(
                data.get("minimum_stock", 0), "Minimum stock"
            ),
            "status": ProductValidator.validate_status(data.get("status")),
        }

        if validated["selling_price"] < validated["purchase_price"]:
            raise ValueError(
                "Selling price should not be lower than purchase price"
            )

        return validated

    @staticmethod
    def validate_update_product(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update product data.

        Args:
            data: Dictionary containing product fields to update.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Update data is required")

        validated = {}

        if "name" in data:
            validated["name"] = ProductValidator.validate_name(data["name"])

        if "sku" in data:
            validated["sku"] = ProductValidator.validate_sku(data["sku"])

        if "barcode" in data:
            validated["barcode"] = ProductValidator.validate_barcode(data["barcode"])

        if "category_id" in data:
            validated["category_id"] = ProductValidator.validate_category_id(data["category_id"])

        if "description" in data:
            validated["description"] = ProductValidator.validate_description(data["description"])

        if "purchase_price" in data:
            validated["purchase_price"] = ProductValidator.validate_positive_decimal(
                data["purchase_price"], "Purchase price"
            )

        if "selling_price" in data:
            validated["selling_price"] = ProductValidator.validate_positive_decimal(
                data["selling_price"], "Selling price"
            )

        if "quantity" in data:
            validated["quantity"] = ProductValidator.validate_positive_int(
                data["quantity"], "Quantity"
            )

        if "minimum_stock" in data:
            validated["minimum_stock"] = ProductValidator.validate_positive_int(
                data["minimum_stock"], "Minimum stock"
            )

        if "status" in data:
            validated["status"] = ProductValidator.validate_status(data["status"])

        if not validated:
            raise ValueError("No valid fields to update")

        if ("selling_price" in validated and "purchase_price" in validated
                and validated["selling_price"] < validated["purchase_price"]):
            raise ValueError(
                "Selling price should not be lower than purchase price"
            )

        return validated
