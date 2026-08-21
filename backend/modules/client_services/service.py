"""ClientServiceAssignment service for assignment-related business logic."""

from typing import Optional, List

from backend.modules.client_services.model import ClientService
from backend.modules.client_services.repository import ClientServiceRepository
from backend.modules.client_services.validator import ClientServiceValidator


class ClientServiceAssignmentService:
    """Service for client service assignment business operations.

    Handles all assignment-related business logic including creating,
    updating, and removing service assignments. Communicates only with
    ClientServiceRepository for data access.
    """

    def __init__(self, assignment_repository: ClientServiceRepository) -> None:
        """Initialize ClientServiceAssignmentService with a ClientServiceRepository.

        Args:
            assignment_repository: Repository for client service database operations.
        """
        self._assignment_repository = assignment_repository

    def assign_service(self, client_id: int, service_id: int, data: dict) -> ClientService:
        """Assign a service to a client.

        Args:
            client_id: The unique identifier of the client.
            service_id: The unique identifier of the service.
            data: Dictionary containing assignment details.

        Returns:
            Created ClientService instance.

        Raises:
            ValueError: If required fields are missing.
            ValueError: If validation fails.
        """
        client_id = ClientServiceValidator.validate_client_id(client_id)
        service_id = ClientServiceValidator.validate_service_id(service_id)
        validated = ClientServiceValidator.validate_assign_service(data or {})

        assignment = ClientService(
            client_id=client_id,
            service_id=service_id,
            start_date=validated["start_date"],
            end_date=validated["end_date"],
            status=validated["status"]
        )

        return self._assignment_repository.create(assignment)

    def update_assignment(self, assignment_id: int, data: dict) -> ClientService:
        """Update an existing service assignment.

        Args:
            assignment_id: The unique identifier of the assignment.
            data: Dictionary containing fields to update.

        Returns:
            Updated ClientService instance.

        Raises:
            ValueError: If assignment not found.
            ValueError: If validation fails.
        """
        validated = ClientServiceValidator.validate_update_assignment(data)

        assignment = self._assignment_repository.get_by_id(assignment_id)
        if assignment is None:
            raise ValueError("Assignment not found")

        if "client_id" in validated:
            assignment.client_id = validated["client_id"]
        if "service_id" in validated:
            assignment.service_id = validated["service_id"]
        if "start_date" in validated:
            assignment.start_date = validated["start_date"]
        if "end_date" in validated:
            assignment.end_date = validated["end_date"]
        if "status" in validated:
            assignment.status = validated["status"]

        updated = self._assignment_repository.update(assignment)
        if updated is None:
            raise ValueError("Failed to update assignment")
        return updated

    def remove_assignment(self, assignment_id: int) -> bool:
        """Remove a service assignment.

        Args:
            assignment_id: The unique identifier of the assignment.

        Returns:
            True if assignment was removed successfully.

        Raises:
            ValueError: If assignment not found.
        """
        deleted = self._assignment_repository.delete(assignment_id)
        if not deleted:
            raise ValueError("Assignment not found")
        return True

    def get_client_services(self, client_id: int) -> List[ClientService]:
        """Retrieve all service assignments for a specific client.

        Args:
            client_id: The unique identifier of the client.

        Returns:
            List of ClientService instances for the given client.
        """
        return self._assignment_repository.get_by_client(client_id)

    def get_service_clients(self, service_id: int) -> List[ClientService]:
        """Retrieve all client assignments for a specific service.

        Args:
            service_id: The unique identifier of the service.

        Returns:
            List of ClientService instances for the given service.
        """
        return self._assignment_repository.get_by_service(service_id)
