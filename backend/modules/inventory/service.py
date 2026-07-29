"""Inventory service for stock management business logic."""

from typing import Optional, List, Dict, Any

from backend.modules.inventory.repository import InventoryRepository


VALID_TRANSACTION_TYPES = {"purchase", "sale", "adjustment", "return"}


class InventoryService:
    """Service for inventory business operations.

    Handles all stock management business logic including adjustments,
    validation, and transaction logging. Communicates only with
    InventoryRepository for data access.
    """

    def __init__(self, inventory_repository: InventoryRepository) -> None:
        self._repository = inventory_repository

    def get_inventory(
        self, search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve all products with stock information.

        Args:
            search: Optional search term.

        Returns:
            List of product dictionaries with stock info.
        """
        return self._repository.get_products_with_stock(search=search)

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

    def adjust_stock(
        self,
        product_id: int,
        transaction_type: str,
        quantity: int,
        reference_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Adjust product stock and create a transaction record.

        Args:
            product_id: ID of the product to adjust.
            transaction_type: Type of adjustment.
            quantity: Quantity change (positive = add, negative = remove).
            reference_id: Optional reference ID.

        Returns:
            Dictionary with updated product info and transaction.

        Raises:
            ValueError: If product not found.
            ValueError: If transaction type is invalid.
            ValueError: If quantity is zero.
            ValueError: If stock would become negative.
        """
        if not transaction_type or transaction_type not in VALID_TRANSACTION_TYPES:
            raise ValueError(
                f"Invalid transaction type. Must be one of: "
                f"{', '.join(sorted(VALID_TRANSACTION_TYPES))}"
            )

        if quantity == 0:
            raise ValueError("Quantity must be greater than or less than zero")

        product = self._repository.get_product_by_id(product_id)
        if product is None:
            raise ValueError("Product not found")

        if product["status"] == "inactive":
            raise ValueError("Cannot adjust stock for inactive product")

        current_quantity = int(product["quantity"])
        new_quantity = current_quantity + quantity

        if new_quantity < 0:
            raise ValueError(
                f"Insufficient stock. Current: {current_quantity}, "
                f"requested change: {quantity}"
            )

        updated = self._repository.update_product_stock(product_id, new_quantity)
        if not updated:
            raise ValueError("Failed to update product stock")

        transaction = self._repository.create_transaction(
            product_id=product_id,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_id=reference_id,
        )

        return {
            "product": {
                "id": product["id"],
                "name": product["name"],
                "previous_quantity": current_quantity,
                "new_quantity": new_quantity,
            },
            "transaction": transaction.to_dict(),
        }

    def get_transactions(
        self, product_id: Optional[int] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve inventory transaction history.

        Args:
            product_id: Optional filter by product.
            limit: Maximum number of records.

        Returns:
            List of transaction dictionaries.
        """
        return self._repository.get_transactions(product_id=product_id, limit=limit)
