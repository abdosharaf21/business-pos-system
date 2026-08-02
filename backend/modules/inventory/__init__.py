"""Inventory module for multi-location stock management and tracking."""

from backend.modules.inventory.model import StockLevel, StockMovement
from backend.modules.inventory.repository import InventoryRepository
from backend.modules.inventory.service import InventoryService

__all__ = ["StockLevel", "StockMovement", "InventoryRepository", "InventoryService"]
