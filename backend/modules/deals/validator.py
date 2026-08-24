"""Deal validator for deal input validation."""

from datetime import date, datetime
from typing import Dict, Any


class DealValidator:
    """Validator for deal input data.

    Handles all validation logic for deal-related operations.
    Does not access the database or execute business logic.
    """

    VALID_PAYMENT_STATUSES = ["pending", "partial", "paid", "refunded"]
    VALID_DEAL_STATUSES = ["draft", "confirmed", "delivered", "cancelled"]
    MAX_PACKAGE_NAME_LENGTH = 200
    MAX_DEAL_NUMBER_LENGTH = 50
    MAX_NOTES_LENGTH = 5000

    @staticmethod
    def validate_client_id(client_id: Any) -> int:
        """Validate client_id.

        Args:
            client_id: Client ID to validate.

        Returns:
            Validated client ID as integer.

        Raises:
            ValueError: If client_id is invalid.
        """
        if client_id is None:
            raise ValueError("Client ID is required")

        try:
            client_id = int(client_id)
        except (TypeError, ValueError):
            raise ValueError("Client ID must be a valid integer")

        if client_id <= 0:
            raise ValueError("Client ID must be a positive integer")

        return client_id

    @staticmethod
    def validate_service_id(service_id: Any) -> int:
        """Validate service_id.

        Args:
            service_id: Service ID to validate.

        Returns:
            Validated service ID as integer.

        Raises:
            ValueError: If service_id is invalid.
        """
        if service_id is None:
            raise ValueError("Service ID is required")

        try:
            service_id = int(service_id)
        except (TypeError, ValueError):
            raise ValueError("Service ID must be a valid integer")

        if service_id <= 0:
            raise ValueError("Service ID must be a positive integer")

        return service_id

    @staticmethod
    def validate_package_name(package_name: str) -> str:
        """Validate package name format and length.

        Args:
            package_name: Package name to validate.

        Returns:
            Stripped and validated package name, or None if empty.

        Raises:
            ValueError: If package name is invalid.
        """
        if not package_name:
            return None

        package_name = package_name.strip()

        if len(package_name) > DealValidator.MAX_PACKAGE_NAME_LENGTH:
            raise ValueError(f"Package name must not exceed {DealValidator.MAX_PACKAGE_NAME_LENGTH} characters")

        return package_name or None

    @staticmethod
    def validate_sale_date(sale_date: Any) -> date:
        """Validate sale date.

        Args:
            sale_date: Sale date to validate.

        Returns:
            Validated date object.

        Raises:
            ValueError: If sale date is invalid.
        """
        if sale_date is None:
            return date.today()

        if isinstance(sale_date, date):
            return sale_date

        if isinstance(sale_date, str):
            try:
                return date.fromisoformat(sale_date)
            except ValueError:
                raise ValueError("Invalid sale date format. Use YYYY-MM-DD")

        raise ValueError("Sale date must be a date or date string")

    @staticmethod
    def validate_price(price: Any) -> float:
        """Validate price.

        Args:
            price: Price to validate.

        Returns:
            Validated price as float.

        Raises:
            ValueError: If price is invalid.
        """
        if price is None:
            raise ValueError("Price is required")

        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValueError("Price must be a valid number")

        if price < 0:
            raise ValueError("Price cannot be negative")

        return round(price, 2)

    @staticmethod
    def validate_discount(discount: Any) -> float:
        """Validate discount.

        Args:
            discount: Discount to validate.

        Returns:
            Validated discount as float.

        Raises:
            ValueError: If discount is invalid.
        """
        if discount is None:
            return 0.00

        try:
            discount = float(discount)
        except (TypeError, ValueError):
            raise ValueError("Discount must be a valid number")

        if discount < 0:
            raise ValueError("Discount cannot be negative")

        return round(discount, 2)

    @staticmethod
    def validate_tax(tax: Any) -> float:
        """Validate tax.

        Args:
            tax: Tax to validate.

        Returns:
            Validated tax as float.

        Raises:
            ValueError: If tax is invalid.
        """
        if tax is None:
            return 0.00

        try:
            tax = float(tax)
        except (TypeError, ValueError):
            raise ValueError("Tax must be a valid number")

        if tax < 0:
            raise ValueError("Tax cannot be negative")

        return round(tax, 2)

    @staticmethod
    def validate_payment_status(status: str) -> str:
        """Validate payment status.

        Args:
            status: Payment status to validate.

        Returns:
            Validated payment status.

        Raises:
            ValueError: If status is invalid.
        """
        if not status:
            return "pending"

        status = status.strip().lower()

        if status not in DealValidator.VALID_PAYMENT_STATUSES:
            raise ValueError(
                f"Invalid payment status. Must be one of: "
                f"{', '.join(DealValidator.VALID_PAYMENT_STATUSES)}"
            )

        return status

    @staticmethod
    def validate_deal_status(status: str) -> str:
        """Validate deal status.

        Args:
            status: Deal status to validate.

        Returns:
            Validated deal status.

        Raises:
            ValueError: If status is invalid.
        """
        if not status:
            return "draft"

        status = status.strip().lower()

        if status not in DealValidator.VALID_DEAL_STATUSES:
            raise ValueError(
                f"Invalid deal status. Must be one of: "
                f"{', '.join(DealValidator.VALID_DEAL_STATUSES)}"
            )

        return status

    @staticmethod
    def validate_notes(notes: str) -> str:
        """Validate notes.

        Args:
            notes: Notes to validate.

        Returns:
            Stripped and validated notes, or None if empty.

        Raises:
            ValueError: If notes are invalid.
        """
        if not notes:
            return None

        notes = notes.strip()

        if len(notes) > DealValidator.MAX_NOTES_LENGTH:
            raise ValueError(f"Notes must not exceed {DealValidator.MAX_NOTES_LENGTH} characters")

        return notes or None

    @staticmethod
    def validate_create_deal(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate create deal data.

        Args:
            data: Dictionary containing deal information.

        Returns:
            Validated data dictionary with computed final_amount.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Deal data is required")

        price = DealValidator.validate_price(data.get("price"))
        discount = DealValidator.validate_discount(data.get("discount"))
        tax = DealValidator.validate_tax(data.get("tax"))
        final_amount = round(price - discount + tax, 2)

        if final_amount < 0:
            raise ValueError("Final amount cannot be negative")

        validated = {
            "client_id": DealValidator.validate_client_id(data.get("client_id")),
            "service_id": DealValidator.validate_service_id(data.get("service_id")),
            "package_name": DealValidator.validate_package_name(data.get("package_name")),
            "sale_date": DealValidator.validate_sale_date(data.get("sale_date")),
            "price": price,
            "discount": discount,
            "tax": tax,
            "final_amount": final_amount,
            "payment_status": DealValidator.validate_payment_status(data.get("payment_status")),
            "deal_status": DealValidator.validate_deal_status(data.get("deal_status")),
            "notes": DealValidator.validate_notes(data.get("notes")),
        }

        return validated

    @staticmethod
    def validate_update_deal(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update deal data.

        Args:
            data: Dictionary containing deal fields to update.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Update data is required")

        validated = {}

        if "package_name" in data:
            validated["package_name"] = DealValidator.validate_package_name(data["package_name"])

        if "sale_date" in data:
            validated["sale_date"] = DealValidator.validate_sale_date(data["sale_date"])

        if "price" in data:
            validated["price"] = DealValidator.validate_price(data["price"])

        if "discount" in data:
            validated["discount"] = DealValidator.validate_discount(data["discount"])

        if "tax" in data:
            validated["tax"] = DealValidator.validate_tax(data["tax"])

        if "payment_status" in data:
            validated["payment_status"] = DealValidator.validate_payment_status(data["payment_status"])

        if "deal_status" in data:
            validated["deal_status"] = DealValidator.validate_deal_status(data["deal_status"])

        if "notes" in data:
            validated["notes"] = DealValidator.validate_notes(data["notes"])

        if not validated:
            raise ValueError("No valid fields to update")

        if all(k in validated for k in ("price", "discount", "tax")):
            validated["final_amount"] = round(
                validated["price"] - validated["discount"] + validated["tax"], 2
            )
            if validated["final_amount"] < 0:
                raise ValueError("Final amount cannot be negative")

        return validated
