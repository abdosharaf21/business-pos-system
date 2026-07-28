"""Client model representing the clients table."""

from datetime import datetime
from typing import Optional


class Client:
    """Represents a client record in the clients table.

    Attributes:
        id: Unique identifier for the client.
        company_name: Name of the client's company.
        contact_person: Name of the primary contact person.
        email: Client's email address.
        phone: Client's phone number.
        address: Client's physical address.
        status: Client's status (lead, prospect, customer).
        created_at: Timestamp when the client was created.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        company_name: Optional[str] = None,
        contact_person: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        status: str = "lead",
        created_at: Optional[datetime] = None
    ) -> None:
        """Initialize a Client instance.

        Args:
            id: Unique identifier for the client.
            company_name: Name of the client's company.
            contact_person: Name of the primary contact person.
            email: Client's email address.
            phone: Client's phone number.
            address: Client's physical address.
            status: Client's status (lead, prospect, customer).
            created_at: Timestamp when the client was created.
        """
        self.id = id
        self.company_name = company_name
        self.contact_person = contact_person
        self.email = email
        self.phone = phone
        self.address = address
        self.status = status
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert Client instance to dictionary.

        Returns:
            Dictionary representation of the client.
        """
        return {
            "id": self.id,
            "company_name": self.company_name,
            "contact_person": self.contact_person,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Client":
        """Create a Client instance from a dictionary.

        Args:
            data: Dictionary containing client data.

        Returns:
            Client instance created from the dictionary.
        """
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            id=data.get("id"),
            company_name=data.get("company_name"),
            contact_person=data.get("contact_person"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            status=data.get("status", "lead"),
            created_at=created_at
        )

    def __str__(self) -> str:
        """Return string representation of the Client.

        Returns:
            String with client id, company name, and contact person.
        """
        return f"Client(id={self.id}, company={self.company_name}, contact={self.contact_person})"

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()
