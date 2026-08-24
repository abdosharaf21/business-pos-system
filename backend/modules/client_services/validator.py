"""Client service assignment validator for assignment input validation."""

from datetime import datetime
from typing import Dict, Any


class ClientServiceValidator:
    """Validator for client service assignment input data.

    Handles all validation logic for assignment-related operations.
    Does not access the database or execute business logic.
    """

    VALID_STATUSES = ["pending", "in_progress", "completed", "cancelled"]

    @staticmethod
    def validate_client_id(client_id) -> int:
        """Validate client ID.

        Args:
            client_id: Client ID to validate.

        Returns:
            Validated client ID as integer.

        Raises:
            ValueError: If client ID is invalid.
        """
        if client_id is None:
            raise ValueError("Client ID is required")

        try:
            client_id = int(client_id)
        except (ValueError, TypeError):
            raise ValueError("Client ID must be a valid integer")

        if client_id <= 0:
            raise ValueError("Client ID must be a positive number")

        return client_id

    @staticmethod
    def validate_service_id(service_id) -> int:
        """Validate service ID.

        Args:
            service_id: Service ID to validate.

        Returns:
            Validated service ID as integer.

        Raises:
            ValueError: If service ID is invalid.
        """
        if service_id is None:
            raise ValueError("Service ID is required")

        try:
            service_id = int(service_id)
        except (ValueError, TypeError):
            raise ValueError("Service ID must be a valid integer")

        if service_id <= 0:
            raise ValueError("Service ID must be a positive number")

        return service_id

    @staticmethod
    def validate_date(date_value, field_name: str):
        """Validate and parse a date value.

        Args:
            date_value: Date value to validate.
            field_name: Name of the field for error messages.

        Returns:
            Parsed datetime or None.

        Raises:
            ValueError: If date is invalid.
        """
        if date_value is None:
            return None

        if isinstance(date_value, datetime):
            return date_value

        if isinstance(date_value, str):
            try:
                return datetime.fromisoformat(date_value)
            except ValueError:
                raise ValueError(f"Invalid {field_name} format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

        raise ValueError(f"Invalid {field_name} type")

    @staticmethod
    def validate_status(status: str) -> str:
        """Validate assignment status.

        Args:
            status: Status to validate.

        Returns:
            Validated status.

        Raises:
            ValueError: If status is invalid.
        """
        if not status:
            return "pending"

        status = status.strip().lower()

        if status not in ClientServiceValidator.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(ClientServiceValidator.VALID_STATUSES)}")

        return status

    @staticmethod
    def validate_assign_service(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate assign service data.

        Args:
            data: Dictionary containing assignment information.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Assignment data is required")

        start_date = ClientServiceValidator.validate_date(data.get("start_date"), "start_date")
        end_date = ClientServiceValidator.validate_date(data.get("end_date"), "end_date")

        if start_date and end_date and start_date > end_date:
            raise ValueError("Start date must be before end date")

        validated = {
            "start_date": start_date,
            "end_date": end_date,
            "status": ClientServiceValidator.validate_status(data.get("status"))
        }

        return validated

    @staticmethod
    def validate_update_assignment(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update assignment data.

        Args:
            data: Dictionary containing assignment fields to update.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Update data is required")

        validated = {}

        if "client_id" in data:
            validated["client_id"] = ClientServiceValidator.validate_client_id(data["client_id"])

        if "service_id" in data:
            validated["service_id"] = ClientServiceValidator.validate_service_id(data["service_id"])

        if "start_date" in data:
            validated["start_date"] = ClientServiceValidator.validate_date(data["start_date"], "start_date")

        if "end_date" in data:
            validated["end_date"] = ClientServiceValidator.validate_date(data["end_date"], "end_date")

        if "status" in data:
            validated["status"] = ClientServiceValidator.validate_status(data["status"])

        if not validated:
            raise ValueError("No valid fields to update")

        if "start_date" in validated and "end_date" in validated:
            if validated["start_date"] and validated["end_date"]:
                if validated["start_date"] > validated["end_date"]:
                    raise ValueError("Start date must be before end date")

        return validated
