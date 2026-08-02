"""Expense validator for expense input validation."""

from datetime import datetime
from typing import Dict, Any, Optional


class ExpenseValidator:
    """Validator for expense input data.

    Handles all validation logic for expense-related operations.
    Does not access the database or execute business logic.
    """

    MAX_TITLE_LENGTH = 200
    MAX_NOTES_LENGTH = 2000

    PAYMENT_METHODS = ("Cash", "Bank", "Visa", "Other")

    @staticmethod
    def validate_title(title: str) -> str:
        """Validate expense title format and length.

        Args:
            title: Expense title to validate.

        Returns:
            Stripped and validated title.

        Raises:
            ValueError: If title is missing or too long.
        """
        if not title:
            raise ValueError("Expense title is required")

        title = title.strip()

        if len(title) == 0:
            raise ValueError("Expense title cannot be empty")

        if len(title) > ExpenseValidator.MAX_TITLE_LENGTH:
            raise ValueError(
                f"Expense title must not exceed {ExpenseValidator.MAX_TITLE_LENGTH} characters"
            )

        return title

    @staticmethod
    def validate_amount(amount: Any) -> float:
        """Validate expense amount is a positive number.

        Args:
            amount: Expense amount to validate.

        Returns:
            Validated positive float amount.

        Raises:
            ValueError: If amount is missing or not a positive number.
        """
        if amount is None or amount == "":
            raise ValueError("Expense amount is required")

        try:
            value = float(amount)
        except (TypeError, ValueError):
            raise ValueError("Expense amount must be a valid number")

        if value <= 0:
            raise ValueError("Expense amount must be greater than zero")

        return round(value, 2)

    @staticmethod
    def validate_category_id(category_id: Any) -> int:
        """Validate expense category id is a positive integer.

        Args:
            category_id: Expense category id to validate.

        Returns:
            Validated positive integer category id.

        Raises:
            ValueError: If category id is missing or not a positive integer.
        """
        if category_id is None or category_id == "":
            raise ValueError("Expense category is required")

        try:
            value = int(category_id)
        except (TypeError, ValueError):
            raise ValueError("Expense category must be a valid id")

        if value <= 0:
            raise ValueError("Expense category must be a valid id")

        return value

    @staticmethod
    def validate_payment_method(payment_method: str) -> str:
        """Validate payment method is one of the supported methods.

        Args:
            payment_method: Payment method to validate.

        Returns:
            Validated payment method string.

        Raises:
            ValueError: If payment method is invalid or unsupported.
        """
        if not payment_method:
            return "Cash"

        payment_method = payment_method.strip()

        if payment_method not in ExpenseValidator.PAYMENT_METHODS:
            raise ValueError(
                f"Invalid payment method. Must be one of: "
                f"{', '.join(ExpenseValidator.PAYMENT_METHODS)}"
            )

        return payment_method

    @staticmethod
    def validate_notes(notes: str) -> Optional[str]:
        """Validate expense notes format and length.

        Args:
            notes: Expense notes to validate.

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

        if len(notes) > ExpenseValidator.MAX_NOTES_LENGTH:
            raise ValueError(
                f"Notes must not exceed {ExpenseValidator.MAX_NOTES_LENGTH} characters"
            )

        return notes

    @staticmethod
    def validate_expense_date(expense_date: str) -> str:
        """Validate expense date is a valid calendar date.

        Args:
            expense_date: Date string in YYYY-MM-DD format.

        Returns:
            Normalized date string in YYYY-MM-DD format.

        Raises:
            ValueError: If date is missing or invalid.
        """
        if not expense_date:
            raise ValueError("Expense date is required")

        expense_date = expense_date.strip()

        try:
            parsed = datetime.strptime(expense_date, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            raise ValueError("Expense date must be a valid date in YYYY-MM-DD format")

        return parsed.isoformat()

    @staticmethod
    def validate_create_expense(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate create expense data.

        Args:
            data: Dictionary containing expense information.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Expense data is required")

        validated = {
            "title": ExpenseValidator.validate_title(data.get("title")),
            "category_id": ExpenseValidator.validate_category_id(data.get("category_id")),
            "amount": ExpenseValidator.validate_amount(data.get("amount")),
            "payment_method": ExpenseValidator.validate_payment_method(data.get("payment_method")),
            "notes": ExpenseValidator.validate_notes(data.get("notes")),
            "expense_date": ExpenseValidator.validate_expense_date(data.get("expense_date")),
        }

        return validated

    @staticmethod
    def validate_update_expense(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update expense data.

        Args:
            data: Dictionary containing expense fields to update.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Update data is required")

        validated = {}

        if "title" in data:
            validated["title"] = ExpenseValidator.validate_title(data["title"])

        if "category_id" in data:
            validated["category_id"] = ExpenseValidator.validate_category_id(data["category_id"])

        if "amount" in data:
            validated["amount"] = ExpenseValidator.validate_amount(data["amount"])

        if "payment_method" in data:
            validated["payment_method"] = ExpenseValidator.validate_payment_method(
                data["payment_method"]
            )

        if "notes" in data:
            validated["notes"] = ExpenseValidator.validate_notes(data["notes"])

        if "expense_date" in data:
            validated["expense_date"] = ExpenseValidator.validate_expense_date(
                data["expense_date"]
            )

        if not validated:
            raise ValueError("No valid fields to update")

        return validated
