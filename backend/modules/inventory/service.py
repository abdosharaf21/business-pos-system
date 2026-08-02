"""Inventory service for multi-location stock management business logic."""

from datetime import datetime
from typing import Optional, List, Dict, Any

from backend.modules.inventory.repository import InventoryRepository


VALID_LOCATIONS = {"warehouse", "store"}
VALID_MOVEMENT_TYPES = {"transfer", "sale", "purchase", "return", "damage", "adjustment"}
ADJUSTMENT_TYPES = {"adjustment", "damage", "return"}
MAX_LIMIT = 200


class InventoryService:
    """Service for inventory business operations.

    Handles all stock management business logic including validation,
    transfers, adjustments, and movement history. Communicates only
    with InventoryRepository for data access.
    """

    def __init__(self, inventory_repository: InventoryRepository) -> None:
        """Initialize InventoryService with an InventoryRepository.

        Args:
            inventory_repository: Repository for inventory database operations.
        """
        self._repository = inventory_repository

    def get_inventory(
        self, search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve all products with per-location stock information.

        Args:
            search: Optional search term.

        Returns:
            List of product dictionaries with stock info.
        """
        return self._repository.get_inventory_with_stock(search=search)

    def get_summary(self) -> Dict[str, Any]:
        """Get aggregate inventory statistics.

        Returns:
            Dictionary with inventory summary.
        """
        return self._repository.get_inventory_summary()

    def get_low_stock(self) -> List[Dict[str, Any]]:
        """Retrieve products with low stock.

        Returns:
            List of low stock product dictionaries.
        """
        return self._repository.get_low_stock_products()

    def get_movements(
        self,
        product_id: Optional[int] = None,
        movement_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Retrieve stock movement history with optional filters.

        Args:
            product_id: Optional filter by product ID.
            movement_type: Optional filter by movement type.
            start_date: Optional start date (YYYY-MM-DD).
            end_date: Optional end date (YYYY-MM-DD).
            limit: Maximum number of records (default 50, max 200).
            offset: Pagination offset.

        Returns:
            List of movement dictionaries.

        Raises:
            ValueError: If a filter value is invalid.
        """
        if movement_type is not None and movement_type not in VALID_MOVEMENT_TYPES:
            raise ValueError(
                f"Invalid movement type. Must be one of: "
                f"{', '.join(sorted(VALID_MOVEMENT_TYPES))}"
            )

        if start_date is not None or end_date is not None:
            if not start_date or not end_date:
                raise ValueError("Both start_date and end_date are required together")
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")

        limit = min(max(int(limit), 1), MAX_LIMIT)
        offset = max(int(offset), 0)

        return self._repository.get_movements(
            product_id=product_id,
            movement_type=movement_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

    def transfer_stock(
        self,
        product_id: int,
        quantity: int,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Transfer stock from the warehouse to the store.

        Args:
            product_id: ID of the product to transfer.
            quantity: Units to transfer.
            user_id: ID of the user performing the transfer.

        Returns:
            Dictionary describing the transfer.

        Raises:
            ValueError: If the product or quantity is invalid.
        """
        if quantity is None or quantity < 1:
            raise ValueError("Transfer quantity must be greater than zero")

        product = self._repository.get_product_by_id(product_id)
        if product is None:
            raise ValueError("Product not found")
        if product["status"] != "active":
            raise ValueError("Cannot transfer stock for inactive product")

        if int(product["warehouse_qty"]) < quantity:
            raise ValueError(
                f"Insufficient warehouse stock: available "
                f"{product['warehouse_qty']}, requested {quantity}"
            )

        return self._repository.transfer(
            product_id=product_id,
            quantity=int(quantity),
            user_id=user_id,
        )

    def adjust_stock(
        self,
        product_id: int,
        location: str,
        quantity: int,
        movement_type: str,
        user_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Adjust stock at a location and record the movement.

        Args:
            product_id: ID of the product to adjust.
            location: Location to adjust (warehouse or store).
            quantity: Quantity (signed for adjustment, positive for damage/return).
            movement_type: Type of movement (adjustment, damage, return).
            user_id: ID of the user performing the adjustment.
            notes: Optional note.

        Returns:
            Dictionary describing the adjustment.

        Raises:
            ValueError: If any input is invalid.
        """
        if movement_type not in ADJUSTMENT_TYPES:
            raise ValueError(
                f"Invalid adjustment type. Must be one of: "
                f"{', '.join(sorted(ADJUSTMENT_TYPES))}"
            )

        if location not in VALID_LOCATIONS:
            raise ValueError(
                f"Invalid location. Must be one of: "
                f"{', '.join(sorted(VALID_LOCATIONS))}"
            )

        if quantity is None or quantity == 0:
            raise ValueError("Quantity must be greater than or less than zero")

        product = self._repository.get_product_by_id(product_id)
        if product is None:
            raise ValueError("Product not found")
        if product["status"] != "active":
            raise ValueError("Cannot adjust stock for inactive product")

        if movement_type == "return":
            location = "store"
            delta = abs(int(quantity))
        elif movement_type == "damage":
            delta = -abs(int(quantity))
        else:
            delta = int(quantity)

        return self._repository.adjust(
            product_id=product_id,
            location=location,
            quantity=delta,
            movement_type=movement_type,
            user_id=user_id,
            notes=notes,
        )
