"""Inventory audit service for stock count business logic."""

from math import ceil
from typing import Any, Dict, List, Optional

from backend.modules.inventory_audits.repository import InventoryAuditRepository
from backend.modules.inventory_audits.model import InventoryAudit
from backend.modules.inventory_audits.validator import InventoryAuditValidator


class InventoryAuditService:
    """Service for inventory audit business operations.

    Handles all audit business logic including validation, creation,
    counted quantity updates, completion, and deletion. Communicates only
    with InventoryAuditRepository for data access.
    """

    MAX_PER_PAGE = 100

    def __init__(self, repository: InventoryAuditRepository) -> None:
        """Initialize InventoryAuditService with a repository.

        Args:
            repository: Repository for inventory audit database operations.
        """
        self._repository = repository

    def create_audit(self, data: Dict[str, Any], user_id: int) -> InventoryAudit:
        """Create a new audit snapshotting all active products at a location.

        Args:
            data: Dictionary with name and location.
            user_id: ID of the user creating the audit.

        Returns:
            The created InventoryAudit instance.

        Raises:
            ValueError: If the input data is invalid.
        """
        validated = InventoryAuditValidator.validate_create_audit(data)
        warehouse_id = validated.get("warehouse_id")
        products = self._repository.get_products_for_audit(
            validated["location"], warehouse_id=warehouse_id
        )

        audit = InventoryAudit(
            name=validated["name"],
            location=validated["location"],
            warehouse_id=warehouse_id,
            status="open",
            created_by=user_id,
        )

        return self._repository.create_with_items(audit, products)

    def list_audits(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """List audits with filtering, sorting, and pagination.

        Args:
            filters: Dictionary with search, location, status, sort, order,
                page, and per_page keys.

        Returns:
            Dictionary with items, total, page, per_page, and pages.

        Raises:
            ValueError: If a filter value is invalid.
        """
        sort = filters.get("sort", "created_at")
        order = filters.get("order", "desc")

        if sort not in self._repository.SORTABLE_COLUMNS:
            raise ValueError(f"Invalid sort column: {sort}")

        if order not in ("asc", "desc"):
            raise ValueError("Order must be 'asc' or 'desc'")

        location = filters.get("location")
        if location:
            InventoryAuditValidator.validate_location(location)

        status = filters.get("status")
        if status:
            InventoryAuditValidator.validate_status(status)

        page = max(int(filters.get("page", 1)), 1)
        per_page = min(
            max(int(filters.get("per_page", 20)), 1), self.MAX_PER_PAGE
        )

        items, total = self._repository.list_audits({
            "search": filters.get("search"),
            "location": location,
            "status": status,
            "sort": sort,
            "order": order,
            "page": page,
            "per_page": per_page,
        })

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": ceil(total / per_page) if total else 0,
        }

    def get_audit(self, audit_id: int) -> InventoryAudit:
        """Retrieve a single audit.

        Args:
            audit_id: The unique identifier of the audit.

        Returns:
            The InventoryAudit instance.

        Raises:
            ValueError: If the audit does not exist.
        """
        audit = self._repository.get_audit(audit_id)
        if audit is None:
            raise ValueError("Audit not found")
        return audit

    def get_items(self, audit_id: int) -> List[Dict[str, Any]]:
        """Retrieve the items of an audit.

        Args:
            audit_id: The unique identifier of the audit.

        Returns:
            List of audit item dictionaries.

        Raises:
            ValueError: If the audit does not exist.
        """
        self.get_audit(audit_id)
        return self._repository.get_items(audit_id)

    def update_audit(
        self, audit_id: int, data: Dict[str, Any]
    ) -> InventoryAudit:
        """Update an open audit's name, status, or counted quantities.

        Args:
            audit_id: The unique identifier of the audit.
            data: Dictionary with optional name, status, or items keys.

        Returns:
            The updated InventoryAudit instance.

        Raises:
            ValueError: If the audit is not editable or the data is invalid.
        """
        validated = InventoryAuditValidator.validate_update_audit(data)
        audit = self._repository.get_audit(audit_id)
        if audit is None:
            raise ValueError("Audit not found")
        if audit.status == "completed":
            raise ValueError("Cannot edit a completed audit")

        if "items" in validated:
            if audit.status != "open":
                raise ValueError("Counts can only be updated on open audits")
            self._repository.update_items(audit_id, validated["items"])

        if "status" in validated:
            if audit.status != "open":
                raise ValueError("Status can only be changed on open audits")
            if validated["status"] != "cancelled":
                raise ValueError("Only the 'cancelled' status can be applied")
            self._repository.update_audit(audit_id, {"status": "cancelled"})

        if "name" in validated:
            self._repository.update_audit(audit_id, {"name": validated["name"]})

        return self._repository.get_audit(audit_id)

    def complete_audit(self, audit_id: int, user_id: Optional[int]) -> Dict[str, Any]:
        """Complete an open audit and apply adjustments to inventory.

        Args:
            audit_id: The unique identifier of the audit.
            user_id: ID of the user completing the audit.

        Returns:
            Dictionary describing the completion result.

        Raises:
            ValueError: If the audit does not exist or is not open.
        """
        audit = self._repository.get_audit(audit_id)
        if audit is None:
            raise ValueError("Audit not found")
        if audit.status != "open":
            raise ValueError("Only open audits can be completed")

        adjusted_items = self._repository.complete_audit(audit_id, user_id)
        completed = self._repository.get_audit(audit_id)
        return {
            "adjusted_items": adjusted_items,
            "audit": completed.to_dict(),
        }

    def delete_audit(self, audit_id: int) -> None:
        """Delete an audit.

        Args:
            audit_id: The unique identifier of the audit.

        Raises:
            ValueError: If the audit does not exist or is completed.
        """
        audit = self._repository.get_audit(audit_id)
        if audit is None:
            raise ValueError("Audit not found")
        if audit.status == "completed":
            raise ValueError("Cannot delete a completed audit")
        self._repository.delete_audit(audit_id)
