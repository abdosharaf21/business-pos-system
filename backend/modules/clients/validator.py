"""Client validator for client input validation."""

import re
from typing import Dict, Any


class ClientValidator:
    """Validator for client input data.

    Handles all validation logic for client-related operations.
    Does not access the database or execute business logic.
    """

    VALID_STATUSES = ["lead", "prospect", "customer"]
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_REGEX = r'^\+?[0-9]{10,15}$'
    MAX_COMPANY_NAME_LENGTH = 150
    MAX_CONTACT_PERSON_LENGTH = 100
    MAX_EMAIL_LENGTH = 150
    MAX_PHONE_LENGTH = 20
    MAX_ADDRESS_LENGTH = 1000

    @staticmethod
    def validate_company_name(company_name: str) -> str:
        """Validate company name format and length.

        Args:
            company_name: Company name to validate.

        Returns:
            Stripped and validated company name.

        Raises:
            ValueError: If company name is invalid.
        """
        if not company_name:
            raise ValueError("Company name is required")

        company_name = company_name.strip()

        if len(company_name) == 0:
            raise ValueError("Company name cannot be empty")

        if len(company_name) > ClientValidator.MAX_COMPANY_NAME_LENGTH:
            raise ValueError(f"Company name must not exceed {ClientValidator.MAX_COMPANY_NAME_LENGTH} characters")

        return company_name

    @staticmethod
    def validate_contact_person(contact_person: str) -> str:
        """Validate contact person name format and length.

        Args:
            contact_person: Contact person name to validate.

        Returns:
            Stripped and validated contact person name.

        Raises:
            ValueError: If contact person name is invalid.
        """
        if not contact_person:
            raise ValueError("Contact person is required")

        contact_person = contact_person.strip()

        if len(contact_person) == 0:
            raise ValueError("Contact person cannot be empty")

        if len(contact_person) > ClientValidator.MAX_CONTACT_PERSON_LENGTH:
            raise ValueError(f"Contact person must not exceed {ClientValidator.MAX_CONTACT_PERSON_LENGTH} characters")

        return contact_person

    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format and length.

        Args:
            email: Email address to validate.

        Returns:
            Stripped and validated email.

        Raises:
            ValueError: If email is invalid.
        """
        if not email:
            return None

        email = email.strip()

        if len(email) > ClientValidator.MAX_EMAIL_LENGTH:
            raise ValueError(f"Email must not exceed {ClientValidator.MAX_EMAIL_LENGTH} characters")

        if not re.match(ClientValidator.EMAIL_REGEX, email):
            raise ValueError("Invalid email format")

        return email

    @staticmethod
    def validate_phone(phone: str) -> str:
        """Validate phone format and length.

        Args:
            phone: Phone number to validate.

        Returns:
            Stripped and validated phone.

        Raises:
            ValueError: If phone is invalid.
        """
        if not phone:
            return None

        phone = phone.strip()

        if len(phone) > ClientValidator.MAX_PHONE_LENGTH:
            raise ValueError(f"Phone must not exceed {ClientValidator.MAX_PHONE_LENGTH} characters")

        if not re.match(ClientValidator.PHONE_REGEX, phone):
            raise ValueError("Invalid phone format")

        return phone

    @staticmethod
    def validate_address(address: str) -> str:
        """Validate address format and length.

        Args:
            address: Address to validate.

        Returns:
            Stripped and validated address.

        Raises:
            ValueError: If address is invalid.
        """
        if not address:
            return None

        address = address.strip()

        if len(address) > ClientValidator.MAX_ADDRESS_LENGTH:
            raise ValueError(f"Address must not exceed {ClientValidator.MAX_ADDRESS_LENGTH} characters")

        return address

    @staticmethod
    def validate_status(status: str) -> str:
        """Validate client status.

        Args:
            status: Status to validate.

        Returns:
            Validated status.

        Raises:
            ValueError: If status is invalid.
        """
        if not status:
            return "lead"

        status = status.strip().lower()

        if status not in ClientValidator.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(ClientValidator.VALID_STATUSES)}")

        return status

    @staticmethod
    def validate_create_client(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate create client data.

        Args:
            data: Dictionary containing client information.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Client data is required")

        validated = {
            "company_name": ClientValidator.validate_company_name(data.get("company_name")),
            "contact_person": ClientValidator.validate_contact_person(data.get("contact_person")),
            "email": ClientValidator.validate_email(data.get("email")),
            "phone": ClientValidator.validate_phone(data.get("phone")),
            "address": ClientValidator.validate_address(data.get("address")),
            "status": ClientValidator.validate_status(data.get("status"))
        }

        return validated

    @staticmethod
    def validate_update_client(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update client data.

        Args:
            data: Dictionary containing client fields to update.

        Returns:
            Validated data dictionary.

        Raises:
            ValueError: If validation fails.
        """
        if not data:
            raise ValueError("Update data is required")

        validated = {}

        if "company_name" in data:
            validated["company_name"] = ClientValidator.validate_company_name(data["company_name"])

        if "contact_person" in data:
            validated["contact_person"] = ClientValidator.validate_contact_person(data["contact_person"])

        if "email" in data:
            validated["email"] = ClientValidator.validate_email(data["email"])

        if "phone" in data:
            validated["phone"] = ClientValidator.validate_phone(data["phone"])

        if "address" in data:
            validated["address"] = ClientValidator.validate_address(data["address"])

        if "status" in data:
            validated["status"] = ClientValidator.validate_status(data["status"])

        if not validated:
            raise ValueError("No valid fields to update")

        return validated
