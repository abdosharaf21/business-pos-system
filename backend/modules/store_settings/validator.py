"""Store settings validator for business information input validation."""

from typing import Any, Dict

from backend.modules.store_settings.model import StoreSettings


class StoreSettingsValidator:
    """Validator for store settings input data.

    Handles all validation logic for the store settings module. Does
    not access the database or execute business logic.
    """

    @staticmethod
    def validate_store_name(value: Any) -> str:
        """Validate the store name.

        Args:
            value: Store name to validate.

        Returns:
            Stripped validated store name.

        Raises:
            ValueError: If the store name is missing or too long.
        """
        if value is None:
            raise ValueError("Store name is required")

        name = str(value).strip()

        if not name:
            raise ValueError("Store name is required")

        if len(name) > 150:
            raise ValueError("Store name must not exceed 150 characters")

        return name

    @staticmethod
    def validate_owner_name(value: Any) -> str:
        """Validate the optional owner name.

        Args:
            value: Owner name to validate.

        Returns:
            Stripped validated owner name, or an empty string.

        Raises:
            ValueError: If the owner name exceeds the maximum length.
        """
        if value is None:
            return ""

        name = str(value).strip()

        if len(name) > 150:
            raise ValueError("Owner name must not exceed 150 characters")

        return name

    @staticmethod
    def validate_phone(value: Any) -> str:
        """Validate the business phone number.

        Accepts digits, spaces, dashes, parentheses and a leading plus.

        Args:
            value: Phone number to validate.

        Returns:
            Stripped validated phone number, or an empty string.

        Raises:
            ValueError: If the phone number is invalid.
        """
        if value is None:
            return ""

        phone = str(value).strip()

        if not phone:
            return ""

        allowed = set("0123456789 +-()")
        if not all(char in allowed for char in phone):
            raise ValueError("Phone number contains invalid characters")

        if len(phone) > 20:
            raise ValueError("Phone number must not exceed 20 characters")

        digits = "".join(char for char in phone if char.isdigit())
        if len(digits) < 7:
            raise ValueError("Phone number must contain at least 7 digits")

        return phone

    @staticmethod
    def validate_email(value: Any) -> str:
        """Validate the business contact email.

        Args:
            value: Email address to validate.

        Returns:
            Stripped validated email address, or an empty string.

        Raises:
            ValueError: If the email format is invalid.
        """
        if value is None:
            return ""

        email = str(value).strip()

        if not email:
            return ""

        if len(email) > 150:
            raise ValueError("Email must not exceed 150 characters")

        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Invalid email format")

        return email

    @staticmethod
    def validate_website(value: Any) -> str:
        """Validate the optional website URL.

        Args:
            value: Website URL to validate.

        Returns:
            Stripped validated website URL, or an empty string.

        Raises:
            ValueError: If the website URL is invalid.
        """
        if value is None:
            return ""

        website = str(value).strip()

        if not website:
            return ""

        if len(website) > 150:
            raise ValueError("Website must not exceed 150 characters")

        return website

    @staticmethod
    def validate_address(value: Any) -> str:
        """Validate the optional business address.

        Args:
            value: Address to validate.

        Returns:
            Stripped validated address, or an empty string.

        Raises:
            ValueError: If the address exceeds the maximum length.
        """
        if value is None:
            return ""

        address = str(value).strip()

        if len(address) > 255:
            raise ValueError("Address must not exceed 255 characters")

        return address

    @staticmethod
    def validate_tax_number(value: Any) -> str:
        """Validate the optional tax registration number.

        Args:
            value: Tax number to validate.

        Returns:
            Stripped validated tax number, or an empty string.

        Raises:
            ValueError: If the tax number exceeds the maximum length.
        """
        if value is None:
            return ""

        tax_number = str(value).strip()

        if len(tax_number) > 50:
            raise ValueError("Tax number must not exceed 50 characters")

        return tax_number

    @staticmethod
    def validate_currency(value: Any) -> str:
        """Validate the currency code.

        Args:
            value: Currency code to validate.

        Returns:
            Uppercased validated currency code.

        Raises:
            ValueError: If the currency is missing or too long.
        """
        if value is None or str(value).strip() == "":
            return StoreSettings.DEFAULT_CURRENCY

        currency = str(value).strip().upper()

        if len(currency) > 10:
            raise ValueError("Currency must not exceed 10 characters")

        return currency

    @staticmethod
    def validate_receipt_footer(value: Any) -> str:
        """Validate the optional receipt footer text.

        Args:
            value: Receipt footer text to validate.

        Returns:
            Stripped validated footer text, or an empty string.

        Raises:
            ValueError: If the footer exceeds the maximum length.
        """
        if value is None:
            return ""

        footer = str(value).strip()

        if len(footer) > 500:
            raise ValueError("Receipt footer must not exceed 500 characters")

        return footer

    @staticmethod
    def validate_login_title(value: Any) -> str:
        """Validate the optional login page welcome title.

        Args:
            value: Login welcome title to validate.

        Returns:
            Stripped validated title, or an empty string.

        Raises:
            ValueError: If the title exceeds the maximum length.
        """
        if value is None:
            return ""

        title = str(value).strip()

        if len(title) > 150:
            raise ValueError("Login title must not exceed 150 characters")

        return title

    @staticmethod
    def validate_login_subtitle(value: Any) -> str:
        """Validate the optional login page welcome subtitle.

        Args:
            value: Login welcome subtitle to validate.

        Returns:
            Stripped validated subtitle, or an empty string.

        Raises:
            ValueError: If the subtitle exceeds the maximum length.
        """
        if value is None:
            return ""

        subtitle = str(value).strip()

        if len(subtitle) > 255:
            raise ValueError("Login subtitle must not exceed 255 characters")

        return subtitle

    @staticmethod
    def validate_update(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate store settings update data.

        Args:
            data: Dictionary with optional store settings fields.

        Returns:
            Dictionary with validated fields, including defaults for
            any field that was not provided.

        Raises:
            ValueError: If validation fails.
        """
        if data is None:
            raise ValueError("Store settings data is required")

        return {
            "store_name": StoreSettingsValidator.validate_store_name(
                data.get("store_name")
            ),
            "owner_name": StoreSettingsValidator.validate_owner_name(
                data.get("owner_name")
            ),
            "phone": StoreSettingsValidator.validate_phone(data.get("phone")),
            "email": StoreSettingsValidator.validate_email(data.get("email")),
            "address": StoreSettingsValidator.validate_address(data.get("address")),
            "website": StoreSettingsValidator.validate_website(data.get("website")),
            "tax_number": StoreSettingsValidator.validate_tax_number(
                data.get("tax_number")
            ),
            "currency": StoreSettingsValidator.validate_currency(data.get("currency")),
            "receipt_footer": StoreSettingsValidator.validate_receipt_footer(
                data.get("receipt_footer")
            ),
            "login_title": StoreSettingsValidator.validate_login_title(
                data.get("login_title")
            ),
            "login_subtitle": StoreSettingsValidator.validate_login_subtitle(
                data.get("login_subtitle")
            ),
        }
