"""Worker management validator for input validation.

Contains all validation rules for workers, attendance records, salary
records and advances. Does not access the database or execute business
logic; it only validates and normalizes incoming data.
"""

import re
from datetime import date as date_type
from typing import Any, Dict, Optional


class WorkerValidator:
    """Validator for worker and payroll related input data."""

    MAX_FULL_NAME_LENGTH = 150
    MAX_PHONE_LENGTH = 20
    MAX_EMAIL_LENGTH = 150
    MAX_JOB_TITLE_LENGTH = 100
    MAX_DEPARTMENT_LENGTH = 100
    MAX_NOTES_LENGTH = 1000

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    PERIOD_REGEX = re.compile(r"^\d{4}-\d{2}$")

    WORKER_STATUSES = ("active", "inactive")
    ATTENDANCE_STATUSES = ("present", "absent", "late", "half_day", "leave")
    SALARY_STATUSES = ("paid", "pending", "partial")
    ADVANCE_STATUSES = ("pending", "paid", "settled")

    @staticmethod
    def _required_text(value: Any, field_name: str, max_length: int, required: bool) -> Optional[str]:
        """Validate a generic required or optional text field.

        Args:
            value: The raw input value.
            field_name: Human readable field name for error messages.
            max_length: Maximum allowed length.
            required: Whether the field is mandatory.

        Returns:
            Stripped text value, or None for empty optional fields.

        Raises:
            ValueError: If validation fails.
        """
        if value is None or value == "":
            if required:
                raise ValueError(f"{field_name} is required")
            return None

        text = str(value).strip()
        if len(text) == 0:
            if required:
                raise ValueError(f"{field_name} cannot be empty")
            return None

        if len(text) > max_length:
            raise ValueError(f"{field_name} must not exceed {max_length} characters")

        return text

    @staticmethod
    def _optional_decimal(value: Any, field_name: str) -> Optional[float]:
        """Validate an optional non-negative decimal value.

        Args:
            value: The raw input value.
            field_name: Human readable field name for error messages.

        Returns:
            Float value, or None for empty optional fields.

        Raises:
            ValueError: If validation fails.
        """
        if value is None or value == "":
            return None

        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field_name} must be a valid number")

        if number < 0:
            raise ValueError(f"{field_name} must not be negative")

        return round(number, 2)

    @staticmethod
    def _optional_date(value: Any, field_name: str) -> Optional[str]:
        """Validate an optional date string.

        Args:
            value: The raw input value (YYYY-MM-DD).
            field_name: Human readable field name for error messages.

        Returns:
            ISO date string, or None for empty optional fields.

        Raises:
            ValueError: If validation fails.
        """
        if value is None or value == "":
            return None

        text = str(value).strip()
        if not re.compile(r"^\d{4}-\d{2}-\d{2}$").match(text):
            raise ValueError(f"{field_name} must be a valid date (YYYY-MM-DD)")

        year, month, day = text.split("-")
        try:
            date_type(int(year), int(month), int(day))
        except ValueError:
            raise ValueError(f"{field_name} must be a valid date (YYYY-MM-DD)")

        return text

    @staticmethod
    def _optional_period(value: Any, field_name: str) -> Optional[str]:
        """Validate an optional salary period string.

        Args:
            value: The raw input value (YYYY-MM).
            field_name: Human readable field name for error messages.

        Returns:
            Normalized period string, or None for empty optional fields.

        Raises:
            ValueError: If validation fails.
        """
        if value is None or value == "":
            return None

        text = str(value).strip()
        if not WorkerValidator.PERIOD_REGEX.match(text):
            raise ValueError(f"{field_name} must be in YYYY-MM format")

        return text

    @staticmethod
    def _optional_time(value: Any, field_name: str) -> Optional[str]:
        """Validate an optional time string.

        Args:
            value: The raw input value (HH:MM or HH:MM:SS).
            field_name: Human readable field name for error messages.

        Returns:
            Normalized ``HH:MM:SS`` string, or None for empty optional fields.

        Raises:
            ValueError: If validation fails.
        """
        if value is None or value == "":
            return None

        text = str(value).strip()
        match = re.compile(r"^(\d{2}):(\d{2})(:(\d{2}))?$").match(text)
        if not match:
            raise ValueError(f"{field_name} must be a valid time (HH:MM)")

        hour, minute = int(match.group(1)), int(match.group(2))
        second = int(match.group(4) or 0)
        if hour > 23 or minute > 59 or second > 59:
            raise ValueError(f"{field_name} must be a valid time (HH:MM)")

        return f"{hour:02d}:{minute:02d}:{second:02d}"

    @staticmethod
    def _choice(value: Any, allowed: tuple, field_name: str, default: str) -> str:
        """Validate a value against an allowed choice set.

        Args:
            value: The raw input value.
            allowed: Tuple of allowed values.
            field_name: Human readable field name for error messages.
            default: Default value when the input is empty.

        Returns:
            Validated choice value.

        Raises:
            ValueError: If the value is not allowed.
        """
        if value is None or value == "":
            return default

        text = str(value).strip()
        if text not in allowed:
            raise ValueError(
                f"{field_name} must be one of: {', '.join(allowed)}"
            )
        return text

    @staticmethod
    def validate_worker(data: Dict[str, Any], partial: bool = False) -> Dict[str, Any]:
        """Validate worker input data.

        Args:
            data: Dictionary containing worker information.
            partial: True when only a subset of fields is provided.

        Returns:
            Validated and normalized data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Worker data is required")

        def pick(key):
            return key in data if partial else True

        validated = {}

        if pick("full_name"):
            validated["full_name"] = WorkerValidator._required_text(
                data.get("full_name"), "Full name", WorkerValidator.MAX_FULL_NAME_LENGTH, True
            )

        if pick("phone"):
            validated["phone"] = WorkerValidator._required_text(
                data.get("phone"), "Phone", WorkerValidator.MAX_PHONE_LENGTH, True
            )

        if pick("email"):
            email = WorkerValidator._required_text(
                data.get("email"), "Email", WorkerValidator.MAX_EMAIL_LENGTH, False
            )
            if email and not WorkerValidator.EMAIL_REGEX.match(email):
                raise ValueError("Invalid email format")
            validated["email"] = email

        if pick("job_title"):
            validated["job_title"] = WorkerValidator._required_text(
                data.get("job_title"), "Job title", WorkerValidator.MAX_JOB_TITLE_LENGTH, False
            )

        if pick("department"):
            validated["department"] = WorkerValidator._required_text(
                data.get("department"), "Department", WorkerValidator.MAX_DEPARTMENT_LENGTH, False
            )

        if pick("hire_date"):
            validated["hire_date"] = WorkerValidator._optional_date(data.get("hire_date"), "Hire date")

        if pick("base_salary"):
            validated["base_salary"] = WorkerValidator._optional_decimal(
                data.get("base_salary"), "Base salary"
            )

        if pick("status"):
            validated["status"] = WorkerValidator._choice(
                data.get("status"), WorkerValidator.WORKER_STATUSES, "Status", "active"
            )

        if pick("notes"):
            validated["notes"] = WorkerValidator._required_text(
                data.get("notes"), "Notes", WorkerValidator.MAX_NOTES_LENGTH, False
            )

        if partial and not validated:
            raise ValueError("No valid fields to update")

        return validated

    @staticmethod
    def validate_attendance(data: Dict[str, Any], partial: bool = False) -> Dict[str, Any]:
        """Validate attendance input data.

        Args:
            data: Dictionary containing attendance information.
            partial: True when only a subset of fields is provided.

        Returns:
            Validated and normalized data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Attendance data is required")

        def pick(key):
            return key in data if partial else True

        validated = {}

        if pick("worker_id"):
            try:
                worker_id = int(data.get("worker_id"))
            except (TypeError, ValueError):
                raise ValueError("worker_id must be a valid integer")
            if worker_id <= 0:
                raise ValueError("worker_id must be positive")
            validated["worker_id"] = worker_id

        if pick("attendance_date"):
            validated["attendance_date"] = WorkerValidator._optional_date(
                data.get("attendance_date"), "Attendance date"
            )

        if pick("status"):
            validated["status"] = WorkerValidator._choice(
                data.get("status"), WorkerValidator.ATTENDANCE_STATUSES, "Status", "present"
            )

        if pick("check_in"):
            validated["check_in"] = WorkerValidator._optional_time(data.get("check_in"), "Check in")

        if pick("check_out"):
            validated["check_out"] = WorkerValidator._optional_time(data.get("check_out"), "Check out")

        if pick("notes"):
            validated["notes"] = WorkerValidator._required_text(
                data.get("notes"), "Notes", 255, False
            )

        if partial and not validated:
            raise ValueError("No valid fields to update")

        return validated

    @staticmethod
    def validate_salary(data: Dict[str, Any], partial: bool = False) -> Dict[str, Any]:
        """Validate salary input data.

        Args:
            data: Dictionary containing salary information.
            partial: True when only a subset of fields is provided.

        Returns:
            Validated and normalized data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Salary data is required")

        def pick(key):
            return key in data if partial else True

        validated = {}

        if pick("worker_id"):
            try:
                worker_id = int(data.get("worker_id"))
            except (TypeError, ValueError):
                raise ValueError("worker_id must be a valid integer")
            if worker_id <= 0:
                raise ValueError("worker_id must be positive")
            validated["worker_id"] = worker_id

        if pick("salary_period"):
            validated["salary_period"] = WorkerValidator._optional_period(
                data.get("salary_period"), "Salary period"
            )

        if pick("base_salary"):
            validated["base_salary"] = WorkerValidator._optional_decimal(
                data.get("base_salary"), "Base salary"
            )

        if pick("bonuses"):
            validated["bonuses"] = WorkerValidator._optional_decimal(data.get("bonuses"), "Bonuses")

        if pick("deductions"):
            validated["deductions"] = WorkerValidator._optional_decimal(
                data.get("deductions"), "Deductions"
            )

        if pick("advances_deduction"):
            validated["advances_deduction"] = WorkerValidator._optional_decimal(
                data.get("advances_deduction"), "Advances deduction"
            )

        if pick("net_amount"):
            validated["net_amount"] = WorkerValidator._optional_decimal(
                data.get("net_amount"), "Net amount"
            )

        if pick("payment_status"):
            validated["payment_status"] = WorkerValidator._choice(
                data.get("payment_status"), WorkerValidator.SALARY_STATUSES, "Payment status", "pending"
            )

        if pick("payment_date"):
            validated["payment_date"] = WorkerValidator._optional_date(
                data.get("payment_date"), "Payment date"
            )

        if pick("notes"):
            validated["notes"] = WorkerValidator._required_text(
                data.get("notes"), "Notes", 255, False
            )

        if partial and not validated:
            raise ValueError("No valid fields to update")

        return validated

    @staticmethod
    def validate_advance(data: Dict[str, Any], partial: bool = False) -> Dict[str, Any]:
        """Validate advance input data.

        Args:
            data: Dictionary containing advance information.
            partial: True when only a subset of fields is provided.

        Returns:
            Validated and normalized data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Advance data is required")

        def pick(key):
            return key in data if partial else True

        validated = {}

        if pick("worker_id"):
            try:
                worker_id = int(data.get("worker_id"))
            except (TypeError, ValueError):
                raise ValueError("worker_id must be a valid integer")
            if worker_id <= 0:
                raise ValueError("worker_id must be positive")
            validated["worker_id"] = worker_id

        if pick("amount"):
            amount = WorkerValidator._optional_decimal(data.get("amount"), "Amount")
            if amount is None:
                raise ValueError("Amount is required")
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")
            validated["amount"] = amount

        if pick("advance_date"):
            validated["advance_date"] = WorkerValidator._optional_date(
                data.get("advance_date"), "Advance date"
            )

        if pick("status"):
            validated["status"] = WorkerValidator._choice(
                data.get("status"), WorkerValidator.ADVANCE_STATUSES, "Status", "pending"
            )

        if pick("notes"):
            validated["notes"] = WorkerValidator._required_text(
                data.get("notes"), "Notes", 255, False
            )

        if partial and not validated:
            raise ValueError("No valid fields to update")

        return validated
