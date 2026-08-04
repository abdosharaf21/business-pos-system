"""Tests for Product API endpoints with expiration enrichment.

Uses mocked services so no real database is needed. Follows the same
pattern as other module tests (service patched, routes exercised).
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from backend.modules.products.model import Product
from backend.modules.products.repository import ProductRepository
from backend.modules.products.service import ProductService


def _product(product_id=1, **overrides):
    """Build a Product model instance with standard attribute values."""
    data = dict(
        id=product_id,
        category_id=1,
        name="Milk",
        sku="SKU-1",
        barcode="111",
        description=None,
        purchase_price=40.0,
        selling_price=55.0,
        quantity=20,
        minimum_stock=5,
        status="active",
        category_name="Dairy",
    )
    data.update(overrides)
    return Product(**data)


class TestGetProductExpiration:
    """Tests for product detail expiration enrichment."""

    def test_service_enriches_expiration(self):
        """Test get_product attaches oldest batch expiration and status."""
        repo = MagicMock(spec=ProductRepository)
        repo.get_by_id.return_value = _product()
        repo.get_oldest_expiration.return_value = date.today() + timedelta(days=10)

        service = ProductService(repo, MagicMock())
        product = service.get_product(1)

        assert product.expiration_date == date.today() + timedelta(days=10)
        assert product.expiration_status == "expiring_soon"

    def test_service_keeps_product_without_expiration(self):
        """Test products without expiration keep null expiration fields."""
        repo = MagicMock(spec=ProductRepository)
        repo.get_by_id.return_value = _product()
        repo.get_oldest_expiration.return_value = None

        service = ProductService(repo, MagicMock())
        product = service.get_product(1)

        assert product.expiration_date is None
        assert product.expiration_status is None

    def test_route_includes_expiration(self, client, admin_headers):
        """Test GET /api/products/<id> exposes expiration data."""
        product = _product()
        product.expiration_date = "2026-09-01"
        product.expiration_status = "expiring_soon"
        with patch("backend.modules.products.service.ProductService.get_product") as mock_get:
            mock_get.return_value = product
            response = client.get("/api/products/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["expiration_date"] == "2026-09-01"
            assert data["expiration_status"] == "expiring_soon"
