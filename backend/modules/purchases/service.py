"""Purchase service for purchase-related business logic."""

from typing import Optional, List, Dict, Any

from backend.modules.purchases.model import Purchase
from backend.modules.purchases.repository import PurchaseRepository
from backend.modules.purchases.validator import PurchaseValidator


class PurchaseService:
    """Service for purchase business operations.

    Handles all purchase-related business logic including creation,
    validation, and retrieval. Communicates only with PurchaseRepository
    for data access.
    """

    def __init__(self, purchase_repository: PurchaseRepository) -> None:
        """Initialize PurchaseService with a PurchaseRepository.

        Args:
            purchase_repository: Repository for purchase database operations.
        """
        self._purchase_repository = purchase_repository

    def create_purchase(self, data: dict, user_id: int) -> Purchase:
        """Create a new purchase.

        Validates all inputs, checks supplier and product existence,
        then creates the purchase with stock updates in one transaction.

        Args:
            data: Dictionary with supplier_id and items.
            user_id: ID of the creating user.

        Returns:
            Created Purchase instance with items.

        Raises:
            ValueError: If validation fails or business rules are violated.
        """
        validated = PurchaseValidator.validate_create_purchase(data)

        supplier = self._purchase_repository.get_supplier_by_id(
            validated["supplier_id"]
        )
        if supplier is None:
            raise ValueError("Supplier not found")

        for item in validated["items"]:
            product = self._purchase_repository.get_product_by_id(
                item["product_id"]
            )
            if product is None:
                raise ValueError(
                    f"Product with id {item['product_id']} not found"
                )

        purchase = self._purchase_repository.create_purchase(
            supplier_id=validated["supplier_id"],
            user_id=user_id,
            items_data=validated["items"],
        )

        if supplier.get("name"):
            purchase.supplier_name = supplier["name"]

        return purchase

    def get_purchase(self, purchase_id: int) -> Purchase:
        """Retrieve a purchase by its unique identifier.

        Args:
            purchase_id: The unique identifier of the purchase.

        Returns:
            Purchase instance with items if found.

        Raises:
            ValueError: If purchase not found.
        """
        purchase = self._purchase_repository.get_by_id(purchase_id)
        if purchase is None:
            raise ValueError("Purchase not found")
        return purchase

    def get_all_purchases(
        self,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Purchase]:
        """Retrieve all purchases with optional search.

        Args:
            search: Optional search term for invoice number or supplier name.
            limit: Maximum number of records.
            offset: Pagination offset.

        Returns:
            List of Purchase instances.
        """
        return self._purchase_repository.get_all(
            search=search, limit=limit, offset=offset
        )

    def get_purchase_invoice(self, purchase_id: int) -> Dict[str, Any]:
        """Retrieve formatted invoice data for a purchase.

        Args:
            purchase_id: The unique identifier of the purchase.

        Returns:
            Dictionary with invoice details.

        Raises:
            ValueError: If purchase not found.
        """
        invoice = self._purchase_repository.get_invoice_data(purchase_id)
        if invoice is None:
            raise ValueError("Purchase not found")
        return invoice

    def create_supplier(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new supplier.

        Validates input, checks for duplicate name and email,
        then creates the supplier.

        Args:
            data: Dictionary with name, phone, email, address.

        Returns:
            Dictionary of the created supplier.

        Raises:
            ValueError: If validation fails or duplicates exist.
        """
        validated = PurchaseValidator.validate_create_supplier(data)

        if self._purchase_repository.exists_by_supplier_name(validated["name"]):
            raise ValueError("A supplier with this name already exists")

        email = validated.get("email")
        if email and self._purchase_repository.exists_by_supplier_email(email):
            raise ValueError("A supplier with this email already exists")

        return self._purchase_repository.create_supplier(validated)

    def get_all_suppliers(self) -> List[Dict[str, Any]]:
        """Retrieve all suppliers for dropdown selection.

        Returns:
            List of supplier dictionaries.
        """
        return self._purchase_repository.get_all_suppliers()

    def search_products(self, search: str) -> List[Dict[str, Any]]:
        """Search products by name or barcode.

        Args:
            search: Search term.

        Returns:
            List of product dictionaries.
        """
        return self._purchase_repository.search_products(search)
