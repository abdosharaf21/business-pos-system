"""Deal service for deal-related business logic."""

from typing import Optional, List

from backend.modules.deals.model import Deal
from backend.modules.deals.repository import DealRepository
from backend.modules.deals.validator import DealValidator


class DealService:
    """Service for deal business operations.

    Handles all deal-related business logic including creation,
    updates, and status management. Communicates only with
    DealRepository for data access.
    """

    def __init__(self, deal_repository: DealRepository) -> None:
        """Initialize DealService with a DealRepository.

        Args:
            deal_repository: Repository for deal database operations.
        """
        self._deal_repository = deal_repository

    def create_deal(self, deal_data: dict, created_by: Optional[int] = None) -> Deal:
        """Create a new deal.

        Args:
            deal_data: Dictionary containing deal information.
            created_by: ID of the user creating the deal.

        Returns:
            Created Deal instance.

        Raises:
            ValueError: If required fields are missing.
            ValueError: If validation fails.
        """
        validated = DealValidator.validate_create_deal(deal_data)

        deal_number = self._deal_repository.get_next_deal_number()

        deal = Deal(
            deal_number=deal_number,
            client_id=validated["client_id"],
            service_id=validated["service_id"],
            package_name=validated["package_name"],
            sale_date=validated["sale_date"],
            price=validated["price"],
            discount=validated["discount"],
            tax=validated["tax"],
            final_amount=validated["final_amount"],
            payment_status=validated["payment_status"],
            deal_status=validated["deal_status"],
            notes=validated["notes"],
            created_by=created_by,
        )

        return self._deal_repository.create(deal)

    def get_deal(self, deal_id: int) -> Deal:
        """Retrieve a deal by its unique identifier.

        Args:
            deal_id: The unique identifier of the deal.

        Returns:
            Deal instance if found.

        Raises:
            ValueError: If deal not found.
        """
        deal = self._deal_repository.get_by_id(deal_id)
        if deal is None:
            raise ValueError("Deal not found")
        return deal

    def get_all_deals(self) -> List[Deal]:
        """Retrieve all deals.

        Returns:
            List of Deal instances.
        """
        return self._deal_repository.get_all()

    def update_deal(self, deal_id: int, data: dict) -> Deal:
        """Update an existing deal.

        Args:
            deal_id: The unique identifier of the deal.
            data: Dictionary containing fields to update.

        Returns:
            Updated Deal instance.

        Raises:
            ValueError: If deal not found.
            ValueError: If validation fails.
        """
        validated = DealValidator.validate_update_deal(data)

        deal = self._deal_repository.get_by_id(deal_id)
        if deal is None:
            raise ValueError("Deal not found")

        if "package_name" in validated:
            deal.package_name = validated["package_name"]
        if "sale_date" in validated:
            deal.sale_date = validated["sale_date"]
        if "price" in validated:
            deal.price = validated["price"]
        if "discount" in validated:
            deal.discount = validated["discount"]
        if "tax" in validated:
            deal.tax = validated["tax"]
        if "final_amount" in validated:
            deal.final_amount = validated["final_amount"]
        if "payment_status" in validated:
            deal.payment_status = validated["payment_status"]
        if "deal_status" in validated:
            deal.deal_status = validated["deal_status"]
        if "notes" in validated:
            deal.notes = validated["notes"]

        updated = self._deal_repository.update(deal)
        if updated is None:
            raise ValueError("Failed to update deal")
        return updated

    def delete_deal(self, deal_id: int) -> bool:
        """Delete a deal.

        Args:
            deal_id: The unique identifier of the deal.

        Returns:
            True if deal was deleted successfully.

        Raises:
            ValueError: If deal not found.
        """
        deal = self._deal_repository.get_by_id(deal_id)
        if deal is None:
            raise ValueError("Deal not found")

        deleted = self._deal_repository.delete(deal_id)
        if not deleted:
            raise ValueError("Failed to delete deal")
        return True

    def change_deal_status(self, deal_id: int, status: str) -> Deal:
        """Change a deal's status.

        Args:
            deal_id: The unique identifier of the deal.
            status: The new deal status.

        Returns:
            Updated Deal instance.

        Raises:
            ValueError: If deal not found.
            ValueError: If status is invalid.
        """
        status = DealValidator.validate_deal_status(status)

        deal = self._deal_repository.get_by_id(deal_id)
        if deal is None:
            raise ValueError("Deal not found")

        deal.deal_status = status
        updated = self._deal_repository.update(deal)
        if updated is None:
            raise ValueError("Failed to update deal status")
        return updated

    def change_payment_status(self, deal_id: int, status: str) -> Deal:
        """Change a deal's payment status.

        Args:
            deal_id: The unique identifier of the deal.
            status: The new payment status.

        Returns:
            Updated Deal instance.

        Raises:
            ValueError: If deal not found.
            ValueError: If status is invalid.
        """
        status = DealValidator.validate_payment_status(status)

        deal = self._deal_repository.get_by_id(deal_id)
        if deal is None:
            raise ValueError("Deal not found")

        deal.payment_status = status
        updated = self._deal_repository.update(deal)
        if updated is None:
            raise ValueError("Failed to update payment status")
        return updated

    def get_deals_by_client(self, client_id: int) -> List[Deal]:
        """Retrieve all deals for a specific client.

        Args:
            client_id: The unique identifier of the client.

        Returns:
            List of Deal instances.
        """
        return self._deal_repository.get_deals_by_client(client_id)

    def get_deals_by_service(self, service_id: int) -> List[Deal]:
        """Retrieve all deals for a specific service.

        Args:
            service_id: The unique identifier of the service.

        Returns:
            List of Deal instances.
        """
        return self._deal_repository.get_deals_by_service(service_id)

    def get_statistics(self) -> dict:
        """Get aggregated deal statistics for the dashboard.

        Returns:
            Dictionary with deal statistics.
        """
        return self._deal_repository.get_statistics()

    def search_deals(self, search_term: str) -> List[Deal]:
        """Search deals by deal number, package name, or client company.

        Args:
            search_term: The search string.

        Returns:
            List of matching Deal instances.
        """
        return self._deal_repository.search_deals(search_term)
