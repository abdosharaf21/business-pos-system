"""Inventory service for multi-location stock management business logic."""

import re
from datetime import datetime
from typing import Optional, List, Dict, Any

from backend.config import Config
from backend.modules.inventory.repository import InventoryRepository
from backend.modules.inventory.warehouse_repository import WarehouseRepository
from backend.modules.inventory.transfer_repository import TransferRepository
from backend.modules.inventory.transfer_model import Transfer, TransferItem
from backend.modules.inventory.warehouse_model import Warehouse
from backend.shared.expiration import (
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
VALID_TRANSFER_STATUSES = {"pending", "completed", "cancelled"}
BUILTIN_WAREHOUSE_CODES = {"WH-MAIN", "STORE"}


class InventoryService:
    """Service for inventory business operations.

    Handles all stock management business logic including validation,
    warehouses, transfers, and movement history. Manual stock corrections
    are intentionally not handled here; they are routed exclusively through
    the Inventory Audit module. Communicates only with InventoryRepository,
    WarehouseRepository, and TransferRepository for data access.
    """

    MAX_NAME_LENGTH = 150
    MAX_CODE_LENGTH = 50
    MAX_NOTES_LENGTH = 255
    MAX_PHONE_LENGTH = 20
    MAX_PER_PAGE = 100
    CODE_PATTERN = re.compile(r"^[A-Z0-9_-]+$")

    def __init__(
        self,
        inventory_repository: InventoryRepository,
        warehouse_repository: Optional[WarehouseRepository] = None,
        transfer_repository: Optional[TransferRepository] = None,
    ) -> None:
        """Initialize InventoryService with the required repositories.

        Args:
            inventory_repository: Repository for inventory database operations.
            warehouse_repository: Repository for warehouse database operations.
            transfer_repository: Repository for stock transfer database operations.
        """
        self._repository = inventory_repository
        self._warehouse_repository = warehouse_repository
        self._transfer_repository = transfer_repository

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

        Extends the repository summary with product-level counts derived
        from the live inventory listing: out-of-stock items, expired
        items, and items expiring soon. Expiration classification is
        business logic, so it lives here rather than in the repository.

        Returns:
            Dictionary with inventory summary.
        """
        summary = self._repository.get_inventory_summary()

        out_of_stock_count = 0
        expired_count = 0
        expiring_soon_count = 0

        rows = self._repository.get_inventory_with_stock()
        for row in rows:
            if row.get("status") != "active":
                continue

            total = int(row.get("total") or 0)
            if total <= 0:
                out_of_stock_count += 1

            expiration_date = row.get("expiration_date")
            if expiration_date is None:
                continue
            status = classify_expiration(
                expiration_date, expiring_soon_days=Config.EXPIRING_SOON_DAYS
            )
            if status == EXPIRATION_STATUS_EXPIRED:
                expired_count += 1
            elif status == EXPIRATION_STATUS_EXPIRING_SOON:
                expiring_soon_count += 1

        summary["out_of_stock_count"] = out_of_stock_count
        summary["expired_count"] = expired_count
        summary["expiring_soon_count"] = expiring_soon_count

        return summary

    def update_expiration_date(
        self,
        product_id: int,
        expiration_date: str,
    ) -> Dict[str, Any]:
        """Set an expiration date for a product's stock.

        Applies the date to the product's single active purchase batch,
        whether that batch already has an expiration date or not. The
        resulting effective expiration date returned by the repository
        stays consistent with the MIN aggregation used by the inventory
        listing.

        Args:
            product_id: ID of the product to update.
            expiration_date: Expiration date as a YYYY-MM-DD string.

        Returns:
            Dictionary with the number of updated rows and the product's
            effective expiration date.

        Raises:
            ValueError: If the product is missing or inactive, the date is
                malformed, the product has no purchase items, or the
                product has multiple purchase batches that make the
                current inventory ambiguous.
        """
        product = self._repository.get_product_by_id(product_id)
        if product is None:
            raise ValueError("Product not found")
        if product["status"] != "active":
            raise ValueError("Cannot update expiration for inactive product")

        try:
            datetime.strptime(expiration_date, "%Y-%m-%d")
        except (TypeError, ValueError):
            raise ValueError(
                "Expiration date must be a valid date in YYYY-MM-DD format"
            )

        result = self._repository.update_product_expiration(
            product_id=product_id,
            expiration_date=expiration_date,
        )
        if result.get("batch_count", 1) > 1:
            raise ValueError(
                "Multiple purchase batches found for this product. "
                "Batch selection is required because the system cannot "
                "determine which batch represents the current inventory."
            )
        if result["updated_rows"] == 0:
            raise ValueError(
                "No purchase items found for this product"
            )
        return {
            "updated_rows": result["updated_rows"],
            "expiration_date": result["expiration_date"],
        }

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
        warehouse_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        """Retrieve stock movement history with optional filters.

        Args:
            product_id: Optional filter by product ID.
            movement_type: Optional filter by movement type.
            warehouse_id: Optional filter by warehouse ID.
            start_date: Optional start date (YYYY-MM-DD).
            end_date: Optional end date (YYYY-MM-DD).
            page: Page number (1-based).
            per_page: Items per page.

        Returns:
            Dictionary with items, total, page, pages, and per_page.

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

        if warehouse_id is not None:
            try:
                warehouse_id = int(warehouse_id)
            except (TypeError, ValueError):
                raise ValueError("Warehouse ID must be an integer")

        page = max(int(page), 1)
        per_page = min(max(int(per_page), 1), self.MAX_PER_PAGE)
        limit = min(max(per_page, 1), MAX_LIMIT)
        offset = (page - 1) * per_page

        total = self._repository.count_movements(
            product_id=product_id,
            movement_type=movement_type,
            warehouse_id=warehouse_id,
            start_date=start_date,
            end_date=end_date,
        )
        items = self._repository.get_movements(
            product_id=product_id,
            movement_type=movement_type,
            warehouse_id=warehouse_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        pages = (total + per_page - 1) // per_page if total else 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "pages": pages,
            "per_page": per_page,
        }

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

    # ------------------------------------------------------------------
    # Warehouses
    # ------------------------------------------------------------------

    def _require_warehouse_repository(self) -> WarehouseRepository:
        """Return the warehouse repository or raise a wiring error.

        Returns:
            The configured WarehouseRepository instance.

        Raises:
            RuntimeError: If the warehouse repository is not configured.
        """
        if self._warehouse_repository is None:
            raise RuntimeError("Warehouse repository is not configured")
        return self._warehouse_repository

    def _require_transfer_repository(self) -> TransferRepository:
        """Return the transfer repository or raise a wiring error.

        Returns:
            The configured TransferRepository instance.

        Raises:
            RuntimeError: If the transfer repository is not configured.
        """
        if self._transfer_repository is None:
            raise RuntimeError("Transfer repository is not configured")
        return self._transfer_repository

    def list_warehouses(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """Retrieve all warehouses with their total stock.

        Args:
            active_only: When True, only return active warehouses.

        Returns:
            List of warehouse dictionaries.
        """
        return self._require_warehouse_repository().list_warehouses(
            active_only=active_only
        )

    def get_warehouse(self, warehouse_id: int) -> Dict[str, Any]:
        """Retrieve a single warehouse.

        Args:
            warehouse_id: The unique identifier of the warehouse.

        Returns:
            Warehouse dictionary.

        Raises:
            ValueError: If the warehouse does not exist.
        """
        warehouse = self._require_warehouse_repository().get_by_id(warehouse_id)
        if warehouse is None:
            raise ValueError("Warehouse not found")
        return warehouse

    def _validate_warehouse_name(self, name: str) -> str:
        """Validate a warehouse name.

        Args:
            name: Warehouse name to validate.

        Returns:
            Stripped and validated name.

        Raises:
            ValueError: If the name is invalid.
        """
        if not name:
            raise ValueError("Warehouse name is required")
        name = str(name).strip()
        if not name:
            raise ValueError("Warehouse name cannot be empty")
        if len(name) > self.MAX_NAME_LENGTH:
            raise ValueError(
                f"Warehouse name must not exceed {self.MAX_NAME_LENGTH} characters"
            )
        return name

    def _validate_warehouse_code(self, code: str) -> str:
        """Validate a warehouse code.

        Args:
            code: Warehouse code to validate.

        Returns:
            Uppercase validated code.

        Raises:
            ValueError: If the code is invalid.
        """
        if not code:
            raise ValueError("Warehouse code is required")
        code = str(code).strip().upper()
        if len(code) > self.MAX_CODE_LENGTH:
            raise ValueError(
                f"Warehouse code must not exceed {self.MAX_CODE_LENGTH} characters"
            )
        if not self.CODE_PATTERN.match(code):
            raise ValueError(
                "Warehouse code may only contain letters, numbers, underscores, and hyphens"
            )
        return code

    def create_warehouse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new warehouse.

        Args:
            data: Dictionary with name, code, address, manager_name, phone.

        Returns:
            Dictionary of the created warehouse.

        Raises:
            ValueError: If the input data is invalid or the name/code is taken.
        """
        repo = self._require_warehouse_repository()
        name = self._validate_warehouse_name(data.get("name"))
        code = self._validate_warehouse_code(data.get("code"))

        if repo.exists_by_name(name):
            raise ValueError("A warehouse with this name already exists")
        if repo.exists_by_code(code):
            raise ValueError("A warehouse with this code already exists")

        return repo.create({
            "name": name,
            "code": code,
            "address": str(data.get("address") or "").strip() or None,
            "manager_name": str(data.get("manager_name") or "").strip() or None,
            "phone": str(data.get("phone") or "").strip() or None,
        })

    def update_warehouse(self, warehouse_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing warehouse.

        Args:
            warehouse_id: The unique identifier of the warehouse.
            data: Dictionary with optional name, code, address, manager_name,
                phone keys.

        Returns:
            Dictionary of the updated warehouse.

        Raises:
            ValueError: If the warehouse does not exist or data is invalid.
        """
        repo = self._require_warehouse_repository()
        current = repo.get_by_id(warehouse_id)
        if current is None:
            raise ValueError("Warehouse not found")

        fields: Dict[str, Any] = {}

        if "name" in data:
            name = self._validate_warehouse_name(data.get("name"))
            if repo.exists_by_name(name, exclude_id=warehouse_id):
                raise ValueError("A warehouse with this name already exists")
            fields["name"] = name

        if "code" in data:
            code = self._validate_warehouse_code(data.get("code"))
            if code != current["code"] and current["code"] in BUILTIN_WAREHOUSE_CODES:
                raise ValueError("Built-in warehouse codes cannot be changed")
            if repo.exists_by_code(code, exclude_id=warehouse_id):
                raise ValueError("A warehouse with this code already exists")
            fields["code"] = code

        if "address" in data:
            fields["address"] = str(data.get("address") or "").strip() or None
        if "manager_name" in data:
            fields["manager_name"] = str(data.get("manager_name") or "").strip() or None
        if "phone" in data:
            fields["phone"] = str(data.get("phone") or "").strip() or None

        updated = repo.update(warehouse_id, fields)
        if updated is None:
            raise ValueError("Warehouse not found")
        return updated

    def toggle_warehouse(self, warehouse_id: int, status: str) -> Dict[str, Any]:
        """Activate or deactivate a warehouse.

        Args:
            warehouse_id: The unique identifier of the warehouse.
            status: active or inactive.

        Returns:
            Dictionary of the updated warehouse.

        Raises:
            ValueError: If the warehouse does not exist, the status is
                invalid, or the warehouse is a built-in location.
        """
        repo = self._require_warehouse_repository()
        current = repo.get_by_id(warehouse_id)
        if current is None:
            raise ValueError("Warehouse not found")
        if status not in ("active", "inactive"):
            raise ValueError("Status must be 'active' or 'inactive'")
        if current["code"] in BUILTIN_WAREHOUSE_CODES and status == "inactive":
            raise ValueError("Built-in warehouses cannot be deactivated")

        updated = repo.set_status(warehouse_id, status)
        if updated is None:
            raise ValueError("Warehouse not found")
        return updated

    def delete_warehouse(self, warehouse_id: int) -> None:
        """Delete an empty, non-built-in warehouse.

        Args:
            warehouse_id: The unique identifier of the warehouse.

        Raises:
            ValueError: If the warehouse does not exist, is built-in, or
                still holds stock.
        """
        repo = self._require_warehouse_repository()
        current = repo.get_by_id(warehouse_id)
        if current is None:
            raise ValueError("Warehouse not found")
        if current["code"] in BUILTIN_WAREHOUSE_CODES:
            raise ValueError("Built-in warehouses cannot be deleted")
        if repo.stock_row_count(warehouse_id) > 0:
            raise ValueError(
                "Cannot delete a warehouse that holds stock; transfer the "
                "stock out first"
            )
        repo.delete(warehouse_id)

    def get_warehouse_stock(
        self, warehouse_id: int, search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve the stock held by a specific warehouse.

        Args:
            warehouse_id: The unique identifier of the warehouse.
            search: Optional search term for product name or barcode.

        Returns:
            List of product dictionaries with per-warehouse quantities.

        Raises:
            ValueError: If the warehouse does not exist.
        """
        self.get_warehouse(warehouse_id)
        return self._require_warehouse_repository().get_stock(
            warehouse_id, search=search
        )

    # ------------------------------------------------------------------
    # Transfers
    # ------------------------------------------------------------------

    def list_transfers(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """List transfers with filtering and pagination.

        Args:
            filters: Dictionary with search, status, sort, order, page,
                per_page keys.

        Returns:
            Dictionary with items, total, page, per_page, and pages.

        Raises:
            ValueError: If a filter value is invalid.
        """
        from math import ceil

        repo = self._require_transfer_repository()

        sort = filters.get("sort", "created_at")
        order = filters.get("order", "desc")
        if sort not in repo.SORTABLE_COLUMNS:
            raise ValueError(f"Invalid sort column: {sort}")
        if order not in ("asc", "desc"):
            raise ValueError("Order must be 'asc' or 'desc'")

        status = filters.get("status")
        if status and status not in VALID_TRANSFER_STATUSES:
            raise ValueError(
                f"Invalid status. Must be one of: {', '.join(sorted(VALID_TRANSFER_STATUSES))}"
            )

        page = max(int(filters.get("page", 1)), 1)
        per_page = min(
            max(int(filters.get("per_page", 20)), 1), self.MAX_PER_PAGE
        )

        items, total = repo.list_transfers({
            "search": filters.get("search"),
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

    def get_transfer(self, transfer_id: int) -> Dict[str, Any]:
        """Retrieve a single transfer with its items.

        Args:
            transfer_id: The unique identifier of the transfer.

        Returns:
            Transfer dictionary with items.

        Raises:
            ValueError: If the transfer does not exist.
        """
        transfer = self._require_transfer_repository().get_with_items(transfer_id)
        if transfer is None:
            raise ValueError("Transfer not found")
        return transfer

    def _validate_transfer_items(
        self, items: Any
    ) -> List[Dict[str, Any]]:
        """Validate transfer line items.

        Args:
            items: List of item dictionaries with product_id, quantity, cost_price.

        Returns:
            List of validated item dictionaries.

        Raises:
            ValueError: If items are missing or invalid.
        """
        if not items or not isinstance(items, list):
            raise ValueError("Transfer items are required")
        if len(items) > 100:
            raise ValueError("A transfer cannot contain more than 100 items")

        seen: set = set()
        validated: List[Dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Each transfer item must be an object")

            try:
                product_id = int(item.get("product_id"))
            except (TypeError, ValueError):
                raise ValueError("Each transfer item must have a valid product_id")
            if product_id <= 0:
                raise ValueError("Each transfer item must have a valid product_id")
            if product_id in seen:
                raise ValueError(
                    f"Duplicate product {product_id} in transfer items"
                )
            seen.add(product_id)

            try:
                quantity = int(item.get("quantity"))
            except (TypeError, ValueError):
                raise ValueError("Each transfer item must have a valid quantity")
            if quantity < 1:
                raise ValueError("Transfer quantity must be greater than zero")

            try:
                cost_price = float(item.get("cost_price") or 0)
            except (TypeError, ValueError):
                cost_price = 0.0
            if cost_price < 0:
                cost_price = 0.0

            validated.append({
                "product_id": product_id,
                "quantity": quantity,
                "cost_price": cost_price,
            })

        missing = self._require_transfer_repository().missing_product_ids(
            [item["product_id"] for item in validated]
        )
        if missing:
            raise ValueError(
                "Transfer contains unknown product id(s): "
                + ", ".join(str(pid) for pid in missing)
            )
        return validated

    def create_transfer(self, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create a pending transfer without moving stock yet.

        Args:
            data: Dictionary with source_warehouse_id, destination_warehouse_id,
                items, notes.
            user_id: ID of the user creating the transfer.

        Returns:
            Dictionary of the created transfer.

        Raises:
            ValueError: If the input data is invalid.
        """
        repo = self._require_transfer_repository()
        warehouse_repo = self._require_warehouse_repository()

        try:
            source_id = int(data.get("source_warehouse_id"))
            destination_id = int(data.get("destination_warehouse_id"))
        except (TypeError, ValueError):
            raise ValueError("Source and destination warehouses are required")

        if source_id <= 0 or destination_id <= 0:
            raise ValueError("Source and destination warehouses are required")
        if source_id == destination_id:
            raise ValueError("Source and destination warehouses must be different")

        source = warehouse_repo.get_by_id(source_id)
        if source is None:
            raise ValueError("Source warehouse not found")
        if source["status"] != "active":
            raise ValueError("Source warehouse is inactive")

        destination = warehouse_repo.get_by_id(destination_id)
        if destination is None:
            raise ValueError("Destination warehouse not found")
        if destination["status"] != "active":
            raise ValueError("Destination warehouse is inactive")

        items = self._validate_transfer_items(data.get("items"))

        notes = str(data.get("notes") or "").strip() or None
        if notes and len(notes) > self.MAX_NOTES_LENGTH:
            raise ValueError(
                f"Notes must not exceed {self.MAX_NOTES_LENGTH} characters"
            )

        transfer = Transfer(
            source_warehouse_id=source_id,
            destination_warehouse_id=destination_id,
            notes=notes,
            created_by=user_id,
            items=[
                TransferItem(
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    cost_price=item["cost_price"],
                )
                for item in items
            ],
        )

        created = repo.create(transfer)
        return created.to_dict()

    def complete_transfer(self, transfer_id: int, user_id: int) -> Dict[str, Any]:
        """Complete a pending transfer, moving stock between warehouses.

        Args:
            transfer_id: The unique identifier of the transfer.
            user_id: ID of the user completing the transfer.

        Returns:
            Dictionary of the completed transfer.

        Raises:
            ValueError: If the transfer is not pending or stock is insufficient.
        """
        repo = self._require_transfer_repository()
        existing = repo.get_with_items(transfer_id)
        if existing is None:
            raise ValueError("Transfer not found")
        if existing["status"] != "pending":
            raise ValueError("Only pending transfers can be completed")

        completed = repo.complete(transfer_id, user_id)
        return completed.to_dict()

    def cancel_transfer(self, transfer_id: int) -> Dict[str, Any]:
        """Cancel a pending transfer without moving stock.

        Args:
            transfer_id: The unique identifier of the transfer.

        Returns:
            Dictionary of the cancelled transfer.

        Raises:
            ValueError: If the transfer does not exist or is not pending.
        """
        repo = self._require_transfer_repository()
        existing = repo.get_with_items(transfer_id)
        if existing is None:
            raise ValueError("Transfer not found")
        if existing["status"] != "pending":
            raise ValueError("Only pending transfers can be cancelled")

        cancelled = repo.cancel(transfer_id)
        if cancelled is None:
            raise ValueError("Transfer not found")
        return cancelled.to_dict()
