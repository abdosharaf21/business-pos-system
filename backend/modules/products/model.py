"""Product model representing the products table."""

from datetime import datetime
from typing import Optional


class Product:
    """Represents a product record in the products table.

    Attributes:
        id: Unique identifier for the product.
        category_id: Foreign key to categories table.
        name: Name of the product.
        sku: Stock keeping unit code.
        barcode: Unique barcode for the product.
        description: Description of the product.
        purchase_price: Purchase cost of the product.
        selling_price: Selling price of the product.
        quantity: Current stock quantity.
        minimum_stock: Minimum stock level before alert.
        status: Product status (active/inactive).
        category_name: Optional category name from join.
        created_at: Timestamp when the product was created.
        updated_at: Timestamp when the product was last updated.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        category_id: Optional[int] = None,
        name: Optional[str] = None,
        sku: Optional[str] = None,
        barcode: Optional[str] = None,
        description: Optional[str] = None,
        purchase_price: float = 0.0,
        selling_price: float = 0.0,
        quantity: int = 0,
        minimum_stock: int = 0,
        status: str = "active",
        category_name: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        """Initialize a Product instance.

        Args:
            id: Unique identifier for the product.
            category_id: Foreign key to categories table.
            name: Name of the product.
            sku: Stock keeping unit code.
            barcode: Unique barcode for the product.
            description: Description of the product.
            purchase_price: Purchase cost of the product.
            selling_price: Selling price of the product.
            quantity: Current stock quantity.
            minimum_stock: Minimum stock level before alert.
            status: Product status.
            category_name: Optional category name from join.
            created_at: Timestamp when the product was created.
            updated_at: Timestamp when the product was last updated.
        """
        self.id = id
        self.category_id = category_id
        self.name = name
        self.sku = sku
        self.barcode = barcode
        self.description = description
        self.purchase_price = purchase_price
        self.selling_price = selling_price
        self.quantity = quantity
        self.minimum_stock = minimum_stock
        self.status = status
        self.category_name = category_name
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert Product instance to dictionary.

        Returns:
            Dictionary representation of the product.
        """
        result = {
            "id": self.id,
            "category_id": self.category_id,
            "name": self.name,
            "sku": self.sku,
            "barcode": self.barcode,
            "description": self.description,
            "purchase_price": float(self.purchase_price) if self.purchase_price else 0.0,
            "selling_price": float(self.selling_price) if self.selling_price else 0.0,
            "quantity": self.quantity,
            "minimum_stock": self.minimum_stock,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if self.category_name is not None:
            result["category_name"] = self.category_name
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Create a Product instance from a dictionary.

        Args:
            data: Dictionary containing product data.

        Returns:
            Product instance created from the dictionary.
        """
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return cls(
            id=data.get("id"),
            category_id=data.get("category_id"),
            name=data.get("name"),
            sku=data.get("sku"),
            barcode=data.get("barcode"),
            description=data.get("description"),
            purchase_price=float(data.get("purchase_price", 0)),
            selling_price=float(data.get("selling_price", 0)),
            quantity=data.get("quantity", 0),
            minimum_stock=data.get("minimum_stock", 0),
            status=data.get("status", "active"),
            category_name=data.get("category_name"),
            created_at=created_at,
            updated_at=updated_at,
        )

    def __str__(self) -> str:
        """Return string representation of the Product.

        Returns:
            String with product id and name.
        """
        return f"Product(id={self.id}, name={self.name})"

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()
