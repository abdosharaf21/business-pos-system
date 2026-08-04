"""Notification model representing a generated in-app alert."""

from datetime import datetime
from typing import Optional


class Notification:
    """Model for an in-app inventory or expiration notification.

    Represents a row in the notifications table plus the product
    context joined at read time (name, barcode, sku, quantity and
    expiration date). Contains no SQL or business logic.

    Attributes:
        TYPE_LOW_STOCK: Notification type for products at or below
            their minimum stock level (warning priority).
        TYPE_OUT_OF_STOCK: Notification type for products with zero
            quantity (critical priority).
        TYPE_EXPIRED: Notification type for products whose oldest batch
            has passed its expiration date (critical priority).
        TYPE_EXPIRING_SOON: Notification type for products whose oldest
            batch expires within the configured threshold (warning).
        PRIORITY_CRITICAL: Highest priority; out of stock and expired.
        PRIORITY_WARNING: Medium priority; low stock and expiring soon.
    """

    TYPE_LOW_STOCK = "low_stock"
    TYPE_OUT_OF_STOCK = "out_of_stock"
    TYPE_EXPIRED = "expired"
    TYPE_EXPIRING_SOON = "expiring_soon"

    PRIORITY_CRITICAL = "critical"
    PRIORITY_WARNING = "warning"

    def __init__(
        self,
        id: Optional[int] = None,
        product_id: Optional[int] = None,
        notification_type: Optional[str] = None,
        priority: Optional[str] = None,
        is_read: bool = False,
        created_at: Optional[datetime] = None,
        product_name: Optional[str] = None,
        barcode: Optional[str] = None,
        sku: Optional[str] = None,
        quantity: Optional[int] = None,
        expiration_date: Optional[str] = None,
    ) -> None:
        """Initialize a Notification instance.

        Args:
            id: Unique notification identifier.
            product_id: ID of the related product.
            notification_type: One of the TYPE_* constants.
            priority: One of the PRIORITY_* constants.
            is_read: Whether the notification has been seen.
            created_at: Timestamp when the notification was generated.
            product_name: Related product name (joined at read time).
            barcode: Related product barcode (joined at read time).
            sku: Related product SKU (joined at read time).
            quantity: Current total stock of the related product.
            expiration_date: Oldest batch expiration date, if any.
        """
        self.id = id
        self.product_id = product_id
        self.notification_type = notification_type
        self.priority = priority
        self.is_read = is_read
        self.created_at = created_at
        self.product_name = product_name
        self.barcode = barcode
        self.sku = sku
        self.quantity = quantity
        self.expiration_date = expiration_date

    def to_dict(self) -> dict:
        """Convert Notification instance to dictionary.

        Returns:
            Dictionary representation of the notification.
        """
        result = {
            "id": self.id,
            "product_id": self.product_id,
            "notification_type": self.notification_type,
            "priority": self.priority,
            "is_read": bool(self.is_read),
        }
        if self.created_at is not None:
            result["created_at"] = (
                self.created_at.isoformat()
                if isinstance(self.created_at, datetime)
                else self.created_at
            )
        if self.product_name is not None:
            result["product_name"] = self.product_name
        if self.barcode is not None:
            result["barcode"] = self.barcode
        if self.sku is not None:
            result["sku"] = self.sku
        if self.quantity is not None:
            result["quantity"] = self.quantity
        if self.expiration_date is not None:
            result["expiration_date"] = self.expiration_date
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Notification":
        """Build a Notification instance from a dictionary.

        Args:
            data: Dictionary with notification fields.

        Returns:
            Notification instance populated from the data.
        """
        return cls(
            id=data.get("id"),
            product_id=data.get("product_id"),
            notification_type=data.get("notification_type"),
            priority=data.get("priority"),
            is_read=bool(data.get("is_read", False)),
            created_at=data.get("created_at"),
            product_name=data.get("product_name"),
            barcode=data.get("barcode"),
            sku=data.get("sku"),
            quantity=data.get("quantity"),
            expiration_date=data.get("expiration_date"),
        )

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            String describing the notification.
        """
        return (
            f"Notification(id={self.id!r}, product_id={self.product_id!r}, "
            f"type={self.notification_type!r}, priority={self.priority!r})"
        )
