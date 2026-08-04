"""Inventory service for multi-location stock management business logic."""

from datetime import datetime
from typing import Optional, List, Dict, Any

from backend.config import Config
from backend.modules.inventory.repository import InventoryRepository
from backend.utils.expiration import (
    classify_expiration,
    EXPIRATION_STATUS_EXPIRED,
    EXPIRATION_STATUS_EXPIRING_SOON,
    EXPIRATION_STATUS_NORMAL,
)


VALID_LOCATIONS = {"warehouse", "store"}
VALID_MOVEMENT_TYPES = {"transfer", "sale", "purchase", "return", "damage", "adjustment"}
MAX_LIMIT = 200
VALID_EXPIRATION_FILTERS = {
    EXPIRATION_STATUS_EXPIRED,
    EXPIRATION_STATUS_EXPIRING_SOON,
    EXPIRATION_STATUS_NORMAL,
}
VALID_EXPIRATION_SORTS = {"expiration"}


class InventoryService:
    """Service for inventory business operations.

    Handles all stock management business logic including validation,
    transfers, and movement history. Manual stock corrections are
    intentionally not handled here; they are routed exclusively through
    the Inventory Audit module. Communicates only with
    InventoryRepository for data access.
    """

    def __init__(self, inventory_repository: InventoryRepository) -> None:
        """Initialize InventoryService with an InventoryRepository.

        Args:
            inventory_repository: Repository for inventory database operations.
        """
        self._repository = inventory_repository

    def get_inventory(
        self,
        search: Optional[str] = None,
        expiration_status: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve all products with per-location stock information.

        Classifies each product's expiration date, optionally filters by
        expiration status, and optionally sorts by expiration date.

        Args:
            search: Optional search term.
            expiration_status: Optional filter: expired, expiring_soon, normal.
            sort: Optional sort key: expiration (oldest first).

        Returns:
            List of product dictionaries with stock info and expiration data.

        Raises:
            ValueError: If an invalid filter or sort value is provided.
        """
        if expiration_status is not None:
            if expiration_status not in VALID_EXPIRATION_FILTERS:
                raise ValueError(
                    f"Invalid expiration filter. Must be one of: "
                    f"{', '.join(sorted(VALID_EXPIRATION_FILTERS))}"
                )

        if sort is not None and sort not in VALID_EXPIRATION_SORTS:
            raise ValueError(
                f"Invalid sort. Must be one of: {', '.join(sorted(VALID_EXPIRATION_SORTS))}"
            )

        rows = self._repository.get_inventory_with_stock(search=search)

        for row in rows:
            expiration_date = row.get("expiration_date")
            if expiration_date is not None:
                row["expiration_status"] = classify_expiration(
                    expiration_date, expiring_soon_days=Config.EXPIRING_SOON_DAYS
                )
            else:
                row["expiration_status"] = None

        if expiration_status is not None:
            rows = [
                row for row in rows if row["expiration_status"] == expiration_status
            ]

        if sort == "expiration":
            def _expiration_key(row: Dict[str, Any]):
                return (row.get("expiration_date") is None, row.get("expiration_date"))

            rows.sort(key=_expiration_key)

        return rows

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
