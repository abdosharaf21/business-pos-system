"""Customer service for customer-related business logic."""

from typing import Optional, List

from backend.modules.customers.model import Customer
from backend.modules.customers.repository import CustomerRepository
from backend.modules.customers.validator import CustomerValidator


class CustomerService:
    """Service for customer business operations.

    Handles all customer-related business logic including creation,
    updates, and deletion. Communicates only with CustomerRepository
    for data access.
    """

    def __init__(self, customer_repository: CustomerRepository) -> None:
        """Initialize CustomerService with a CustomerRepository.

        Args:
            customer_repository: Repository for customer database operations.
        """
        self._customer_repository = customer_repository

    def create_customer(self, data: dict) -> Customer:
        """Create a new customer.

        Args:
            data: Dictionary containing customer information.

        Returns:
            Created Customer instance.

        Raises:
            ValueError: If validation fails or business rules are violated.
        """
        validated = CustomerValidator.validate_create_customer(data)

        if self._customer_repository.exists_by_phone(validated["phone"]):
            raise ValueError("A customer with this phone number already exists")

        if validated["email"] and self._customer_repository.exists_by_email(validated["email"]):
            raise ValueError("A customer with this email already exists")

        customer = Customer(
            name=validated["name"],
            phone=validated["phone"],
            email=validated["email"],
            address=validated["address"],
        )

        return self._customer_repository.create(customer)

    def get_customer(self, customer_id: int) -> Customer:
        """Retrieve a customer by its unique identifier.

        Args:
            customer_id: The unique identifier of the customer.

        Returns:
            Customer instance if found.

        Raises:
            ValueError: If customer not found.
        """
        customer = self._customer_repository.get_by_id(customer_id)
        if customer is None:
            raise ValueError("Customer not found")
        return customer

    def get_all_customers(self, search: Optional[str] = None) -> List[Customer]:
        """Retrieve all customers with optional search.

        Args:
            search: Optional search term for name or phone.

        Returns:
            List of Customer instances.
        """
        return self._customer_repository.get_all(search=search)

    def update_customer(self, customer_id: int, data: dict) -> Customer:
        """Update an existing customer.

        Args:
            customer_id: The unique identifier of the customer.
            data: Dictionary containing fields to update.

        Returns:
            Updated Customer instance.

        Raises:
            ValueError: If customer not found or validation fails.
        """
        validated = CustomerValidator.validate_update_customer(data)

        customer = self._customer_repository.get_by_id(customer_id)
        if customer is None:
            raise ValueError("Customer not found")

        if "phone" in validated:
            existing = self._customer_repository.exists_by_phone(validated["phone"])
            if existing and validated["phone"] != customer.phone:
                raise ValueError("A customer with this phone number already exists")
            customer.phone = validated["phone"]

        if "email" in validated:
            if validated["email"]:
                existing = self._customer_repository.exists_by_email(validated["email"])
                if existing and validated["email"] != customer.email:
                    raise ValueError("A customer with this email already exists")
            customer.email = validated["email"]

        if "name" in validated:
            customer.name = validated["name"]

        if "address" in validated:
            customer.address = validated["address"]

        updated = self._customer_repository.update(customer)
        if updated is None:
            raise ValueError("Failed to update customer")
        return updated

    def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer.

        Args:
            customer_id: The unique identifier of the customer.

        Returns:
            True if customer was deleted successfully.

        Raises:
            ValueError: If customer not found.
        """
        deleted = self._customer_repository.delete(customer_id)
        if not deleted:
            raise ValueError("Customer not found")
        return True
