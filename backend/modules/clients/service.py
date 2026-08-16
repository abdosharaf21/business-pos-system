"""Client service for client-related business logic."""

from typing import Optional, List

from backend.modules.clients.model import Client
from backend.modules.clients.repository import ClientRepository
from backend.modules.clients.validator import ClientValidator


class ClientService:
    """Service for client business operations.

    Handles all client-related business logic including creation,
    updates, and status management. Communicates only with
    ClientRepository for data access.
    """

    def __init__(self, client_repository: ClientRepository) -> None:
        """Initialize ClientService with a ClientRepository.

        Args:
            client_repository: Repository for client database operations.
        """
        self._client_repository = client_repository

    def create_client(self, client_data: dict) -> Client:
        """Create a new client.

        Args:
            client_data: Dictionary containing client information.

        Returns:
            Created Client instance.

        Raises:
            ValueError: If required fields are missing.
            ValueError: If validation fails.
        """
        validated = ClientValidator.validate_create_client(client_data)

        client = Client(
            company_name=validated["company_name"],
            contact_person=validated["contact_person"],
            email=validated["email"],
            phone=validated["phone"],
            address=validated["address"],
            status=validated["status"]
        )

        return self._client_repository.create(client)

    def get_client(self, client_id: int) -> Client:
        """Retrieve a client by their unique identifier.

        Args:
            client_id: The unique identifier of the client.

        Returns:
            Client instance if found.

        Raises:
            ValueError: If client not found.
        """
        client = self._client_repository.get_by_id(client_id)
        if client is None:
            raise ValueError("Client not found")
        return client

    def get_all_clients(self) -> List[Client]:
        """Retrieve all clients.

        Returns:
            List of Client instances.
        """
        return self._client_repository.get_all()

    def update_client(self, client_id: int, data: dict) -> Client:
        """Update an existing client.

        Args:
            client_id: The unique identifier of the client.
            data: Dictionary containing fields to update.

        Returns:
            Updated Client instance.

        Raises:
            ValueError: If client not found.
            ValueError: If validation fails.
        """
        validated = ClientValidator.validate_update_client(data)

        client = self._client_repository.get_by_id(client_id)
        if client is None:
            raise ValueError("Client not found")

        if "company_name" in validated:
            client.company_name = validated["company_name"]
        if "contact_person" in validated:
            client.contact_person = validated["contact_person"]
        if "email" in validated:
            client.email = validated["email"]
        if "phone" in validated:
            client.phone = validated["phone"]
        if "address" in validated:
            client.address = validated["address"]
        if "status" in validated:
            client.status = validated["status"]

        updated = self._client_repository.update(client)
        if updated is None:
            raise ValueError("Failed to update client")
        return updated

    def delete_client(self, client_id: int) -> bool:
        """Delete a client.

        Args:
            client_id: The unique identifier of the client.

        Returns:
            True if client was deleted successfully.

        Raises:
            ValueError: If client not found.
        """
        deleted = self._client_repository.delete(client_id)
        if not deleted:
            raise ValueError("Client not found")
        return True

    def change_status(self, client_id: int, status: str) -> Client:
        """Change a client's status.

        Args:
            client_id: The unique identifier of the client.
            status: The new status value.

        Returns:
            Updated Client instance.

        Raises:
            ValueError: If client not found.
            ValueError: If status is invalid.
        """
        status = ClientValidator.validate_status(status)

        client = self._client_repository.get_by_id(client_id)
        if client is None:
            raise ValueError("Client not found")

        client.status = status
        updated = self._client_repository.update(client)
        if updated is None:
            raise ValueError("Failed to update client status")
        return updated
