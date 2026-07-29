"""POS product model representing products available for sale."""
from typing import Optional


class PosProduct:
    """Represents a product displayed in the POS interface.

    Attributes:
        id: Product ID.
        barcode: Product barcode.
        name: Product name.
        category: Category name.
        selling_price: Unit selling price.
        quantity: Current stock quantity.
        minimum_stock: Minimum stock threshold.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        barcode: Optional[str] = None,
        name: Optional[str] = None,
        category: Optional[str] = None,
        selling_price: float = 0.0,
        quantity: int = 0,
        minimum_stock: int = 0,
    ) -> None:
        self.id = id
        self.barcode = barcode or ""
        self.name = name or ""
        self.category = category or ""
        self.selling_price = selling_price
        self.quantity = quantity
        self.minimum_stock = minimum_stock

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "barcode": self.barcode,
            "name": self.name,
            "category": self.category,
            "selling_price": float(self.selling_price),
            "quantity": self.quantity,
            "minimum_stock": self.minimum_stock,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PosProduct":
        return cls(
            id=data.get("id"),
            barcode=data.get("barcode"),
            name=data.get("name"),
            category=data.get("category"),
            selling_price=float(data.get("selling_price", 0)),
            quantity=int(data.get("quantity", 0)),
            minimum_stock=int(data.get("minimum_stock", 0)),
        )

    def __str__(self) -> str:
        return f"PosProduct(id={self.id}, name={self.name})"

    def __repr__(self) -> str:
        return f"PosProduct(id={self.id}, name={self.name})"
