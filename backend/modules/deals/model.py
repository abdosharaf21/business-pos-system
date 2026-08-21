"""Deal model representing the deals table."""

from datetime import datetime, date
from typing import Optional


class Deal:
    """Represents a deal record in the deals table.

    Attributes:
        id: Unique identifier for the deal.
        deal_number: Human-readable deal number.
        client_id: Foreign key to the clients table.
        service_id: Foreign key to the services table.
        package_name: Name of the package sold.
        sale_date: Date the deal was made.
        price: Base price from the service catalog.
        discount: Discount applied to the deal.
        tax: Tax applied to the deal.
        final_amount: Final amount after discount and tax.
        payment_status: Payment status (pending, partial, paid, refunded).
        deal_status: Deal status (draft, confirmed, delivered, cancelled).
        notes: Optional notes about the deal.
        created_by: Foreign key to the user who created the deal.
        created_at: Timestamp when the deal was created.
        updated_at: Timestamp when the deal was last updated.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        deal_number: Optional[str] = None,
        client_id: Optional[int] = None,
        service_id: Optional[int] = None,
        package_name: Optional[str] = None,
        sale_date: Optional[date] = None,
        price: float = 0.00,
        discount: float = 0.00,
        tax: float = 0.00,
        final_amount: float = 0.00,
        payment_status: str = "pending",
        deal_status: str = "draft",
        notes: Optional[str] = None,
        created_by: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        """Initialize a Deal instance.

        Args:
            id: Unique identifier for the deal.
            deal_number: Human-readable deal number.
            client_id: Foreign key to the clients table.
            service_id: Foreign key to the services table.
            package_name: Name of the package sold.
            sale_date: Date the deal was made.
            price: Base price from the service catalog.
            discount: Discount applied to the deal.
            tax: Tax applied to the deal.
            final_amount: Final amount after discount and tax.
            payment_status: Payment status.
            deal_status: Deal status.
            notes: Optional notes about the deal.
            created_by: Foreign key to the user who created the deal.
            created_at: Timestamp when the deal was created.
            updated_at: Timestamp when the deal was last updated.
        """
        self.id = id
        self.deal_number = deal_number
        self.client_id = client_id
        self.service_id = service_id
        self.package_name = package_name
        self.sale_date = sale_date or date.today()
        self.price = price
        self.discount = discount
        self.tax = tax
        self.final_amount = final_amount
        self.payment_status = payment_status
        self.deal_status = deal_status
        self.notes = notes
        self.created_by = created_by
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert Deal instance to dictionary.

        Returns:
            Dictionary representation of the deal.
        """
        return {
            "id": self.id,
            "deal_number": self.deal_number,
            "client_id": self.client_id,
            "service_id": self.service_id,
            "package_name": self.package_name,
            "sale_date": self.sale_date.isoformat() if hasattr(self.sale_date, "isoformat") else str(self.sale_date) if self.sale_date else None,
            "price": float(self.price),
            "discount": float(self.discount),
            "tax": float(self.tax),
            "final_amount": float(self.final_amount),
            "payment_status": self.payment_status,
            "deal_status": self.deal_status,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Deal":
        """Create a Deal instance from a dictionary.

        Args:
            data: Dictionary containing deal data.

        Returns:
            Deal instance created from the dictionary.
        """
        sale_date = data.get("sale_date")
        if sale_date and isinstance(sale_date, str):
            sale_date = date.fromisoformat(sale_date)

        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return cls(
            id=data.get("id"),
            deal_number=data.get("deal_number"),
            client_id=data.get("client_id"),
            service_id=data.get("service_id"),
            package_name=data.get("package_name"),
            sale_date=sale_date,
            price=data.get("price", 0.00),
            discount=data.get("discount", 0.00),
            tax=data.get("tax", 0.00),
            final_amount=data.get("final_amount", 0.00),
            payment_status=data.get("payment_status", "pending"),
            deal_status=data.get("deal_status", "draft"),
            notes=data.get("notes"),
            created_by=data.get("created_by"),
            created_at=created_at,
            updated_at=updated_at,
        )

    def __str__(self) -> str:
        """Return string representation of the Deal.

        Returns:
            String with deal id, number, and final amount.
        """
        return f"Deal(id={self.id}, number={self.deal_number}, amount={self.final_amount})"

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()
