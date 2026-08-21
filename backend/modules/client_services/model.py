"""ClientService model representing the client_services table."""

from datetime import datetime
from typing import Optional


class ClientService:
    """Represents a client service record in the client_services table.

    Attributes:
        id: Unique identifier for the client service record.
        client_id: Foreign key to the clients table.
        service_id: Foreign key to the services table.
        start_date: Start date of the service assignment.
        end_date: End date of the service assignment.
        status: Status of the client service (active, completed, cancelled).
        created_at: Timestamp when the record was created.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        client_id: Optional[int] = None,
        service_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: str = "active",
        created_at: Optional[datetime] = None
    ) -> None:
        """Initialize a ClientService instance.

        Args:
            id: Unique identifier for the client service record.
            client_id: Foreign key to the clients table.
            service_id: Foreign key to the services table.
            start_date: Start date of the service assignment.
            end_date: End date of the service assignment.
            status: Status of the client service (active, completed, cancelled).
            created_at: Timestamp when the record was created.
        """
        self.id = id
        self.client_id = client_id
        self.service_id = service_id
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert ClientService instance to dictionary.

        Returns:
            Dictionary representation of the client service.
        """
        return {
            "id": self.id,
            "client_id": self.client_id,
            "service_id": self.service_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ClientService":
        """Create a ClientService instance from a dictionary.

        Args:
            data: Dictionary containing client service data.

        Returns:
            ClientService instance created from the dictionary.
        """
        start_date = data.get("start_date")
        if start_date and isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)

        end_date = data.get("end_date")
        if end_date and isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)

        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            id=data.get("id"),
            client_id=data.get("client_id"),
            service_id=data.get("service_id"),
            start_date=start_date,
            end_date=end_date,
            status=data.get("status", "active"),
            created_at=created_at
        )

    def __str__(self) -> str:
        """Return string representation of the ClientService.

        Returns:
            String with client service id, client id, and service id.
        """
        return f"ClientService(id={self.id}, client_id={self.client_id}, service_id={self.service_id})"

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()
