"""Customer validator for customer input validation."""

import re
from typing import Dict, Any, Optional


class CustomerValidator:
    """Validator for customer input data.

    Handles all validation logic for customer-related operations.
    Does not access the database or execute business logic.
    """

    MAX_NAME_LENGTH = 100
    MAX_PHONE_LENGTH = 20
    MAX_EMAIL_LENGTH = 150
    MAX_ADDRESS_LENGTH = 1000

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    @staticmethod
    def validate_name(name: Any) -> str:
        """Validate customer name format and length.

        Args:
            name: Customer name to validate.

        Returns:
            Stripped and validated name.

        Raises:
            ValueError: If name is invalid.
        """
        if not name:
            raise ValueError("Customer name is required")

        name = str(name).strip()

        if len(name) == 0:
            raise ValueError("Customer name cannot be empty")

        if len(name) > CustomerValidator.MAX_NAME_LENGTH:
            raise ValueError(
                f"Customer name must not exceed {CustomerValidator.MAX_NAME_LENGTH} characters"
            )

        return name

    @staticmethod
    def validate_phone(phone: Any) -> str:
        """Validate customer phone number.

        Args:
            phone: Phone number to validate.

        Returns:
            Stripped and validated phone number.

        Raises:
            ValueError: If phone is invalid.
        """
        if not phone:
            raise ValueError("Phone number is required")

        phone = str(phone).strip()

        if len(phone) == 0:
            raise ValueError("Phone number cannot be empty")

        if len(phone) > CustomerValidator.MAX_PHONE_LENGTH:
            raise ValueError(
                f"Phone number must not exceed {CustomerValidator.MAX_PHONE_LENGTH} characters"
            )

        return phone

    @staticmethod
    def validate_email(email: Any) -> Optional[str]:
        """Validate customer email address.

        Args:
            email: Email address to validate.

        Returns:
            Stripped and validated email, or None if empty.

        Raises:
            ValueError: If email format is invalid.
        """
        if not email:
            return None

        email = str(email).strip()

        if len(email) == 0:
            return None

        if len(email) > CustomerValidator.MAX_EMAIL_LENGTH:
            raise ValueError(
                f"Email must not exceed {CustomerValidator.MAX_EMAIL_LENGTH} characters"
            )

        if not CustomerValidator.EMAIL_REGEX.match(email):
            raise ValueError("Invalid email format")

        return email

    @staticmethod
    def validate_address(address: Any) -> Optional[str]:
        """Validate customer address.

        Args:
            address: Address to validate.

        Returns:
            Stripped and validated address, or None if empty.

        Raises:
            ValueError: If address is too long.
        """
        if not address:
            return None

        address = str(address).strip()

        if len(address) == 0:
            return None

        if len(address) > CustomerValidator.MAX_ADDRESS_LENGTH:
            raise ValueError(
                f"Address must not exceed {CustomerValidator.MAX_ADDRESS_LENGTH} characters"
            )

        return address

    @staticmethod
    def validate_create_customer(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate create customer data.

        Args:
            data: Dictionary containing customer information.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Customer data is required")

        validated = {
            "name": CustomerValidator.validate_name(data.get("name")),
            "phone": CustomerValidator.validate_phone(data.get("phone")),
            "email": CustomerValidator.validate_email(data.get("email")),
            "address": CustomerValidator.validate_address(data.get("address")),
        }

        return validated

    @staticmethod
    def validate_update_customer(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update customer data.

        Args:
            data: Dictionary containing customer fields to update.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Update data is required")

        validated = {}

        if "name" in data:
            validated["name"] = CustomerValidator.validate_name(data["name"])

        if "phone" in data:
            validated["phone"] = CustomerValidator.validate_phone(data["phone"])

        if "email" in data:
            validated["email"] = CustomerValidator.validate_email(data["email"])

        if "address" in data:
            validated["address"] = CustomerValidator.validate_address(data["address"])

        if not validated:
            raise ValueError("No valid fields to update")

        return validated
