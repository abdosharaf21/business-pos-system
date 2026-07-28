"""Service service for service-related business logic."""

from typing import Optional, List

from backend.modules.services.model import Service
from backend.modules.services.repository import ServiceRepository
from backend.modules.services.validator import ServiceValidator


class ServiceService:
    """Service for service business operations.

    Handles all service-related business logic including creation,
    updates, and category filtering. Communicates only with
    ServiceRepository for data access.
    """

    def __init__(self, service_repository: ServiceRepository) -> None:
        """Initialize ServiceService with a ServiceRepository.

        Args:
            service_repository: Repository for service database operations.
        """
        self._service_repository = service_repository

    def create_service(self, data: dict) -> Service:
        """Create a new service.

        Args:
            data: Dictionary containing service information.

        Returns:
            Created Service instance.

        Raises:
            ValueError: If required fields are missing.
            ValueError: If price is negative.
            ValueError: If validation fails.
        """
        validated = ServiceValidator.validate_create_service(data)

        service = Service(
            category_id=validated["category_id"],
            name=validated["name"],
            description=validated["description"],
            price=validated["price"],
            duration_days=validated["duration_days"],
            status=validated["status"]
        )

        return self._service_repository.create(service)

    def get_service(self, service_id: int) -> Service:
        """Retrieve a service by its unique identifier.

        Args:
            service_id: The unique identifier of the service.

        Returns:
            Service instance if found.

        Raises:
            ValueError: If service not found.
        """
        service = self._service_repository.get_by_id(service_id)
        if service is None:
            raise ValueError("Service not found")
        return service

    def get_all_services(self) -> List[Service]:
        """Retrieve all services.

        Returns:
            List of Service instances.
        """
        return self._service_repository.get_all()

    def get_services_by_category(self, category_id: int) -> List[Service]:
        """Retrieve all services belonging to a specific category.

        Args:
            category_id: The unique identifier of the category.

        Returns:
            List of Service instances for the given category.
        """
        return self._service_repository.get_by_category(category_id)

    def update_service(self, service_id: int, data: dict) -> Service:
        """Update an existing service.

        Args:
            service_id: The unique identifier of the service.
            data: Dictionary containing fields to update.

        Returns:
            Updated Service instance.

        Raises:
            ValueError: If service not found.
            ValueError: If price is negative.
            ValueError: If validation fails.
        """
        validated = ServiceValidator.validate_update_service(data)

        service = self._service_repository.get_by_id(service_id)
        if service is None:
            raise ValueError("Service not found")

        if "name" in validated:
            service.name = validated["name"]
        if "category_id" in validated:
            service.category_id = validated["category_id"]
        if "description" in validated:
            service.description = validated["description"]
        if "price" in validated:
            service.price = validated["price"]
        if "duration_days" in validated:
            service.duration_days = validated["duration_days"]
        if "status" in validated:
            service.status = validated["status"]

        updated = self._service_repository.update(service)
        if updated is None:
            raise ValueError("Failed to update service")
        return updated

    def delete_service(self, service_id: int) -> bool:
        """Delete a service.

        Args:
            service_id: The unique identifier of the service.

        Returns:
            True if service was deleted successfully.

        Raises:
            ValueError: If service not found.
        """
        deleted = self._service_repository.delete(service_id)
        if not deleted:
            raise ValueError("Service not found")
        return True
