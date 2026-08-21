"""Deals module for sales/deal management operations."""

from backend.modules.deals.model import Deal
from backend.modules.deals.repository import DealRepository
from backend.modules.deals.service import DealService

__all__ = ["Deal", "DealRepository", "DealService"]
