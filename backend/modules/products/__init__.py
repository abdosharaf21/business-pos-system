"""Products module for product management."""

from backend.modules.products.model import Product
from backend.modules.products.repository import ProductRepository
from backend.modules.products.service import ProductService

__all__ = ["Product", "ProductRepository", "ProductService"]
