"""Tests for Inventory API endpoints.

Tests the /api/inventory/* endpoints including per-location stock
retrieval, movement history, transfers, adjustments, and role-based
access control.
"""

from unittest.mock import patch

from backend.modules.inventory.model import StockLevel, StockMovement


def _stock_row(**kw):
    """Create a fake inventory row dict."""
    defaults = dict(
        id=1,
        product_id=1,
        name="Keyboard",
        barcode="123",
        category_name="Accessories",
        warehouse_qty=50,
        store_qty=10,
        total=60,
        minimum_stock=5,
        status="active",
    )
    defaults.update(kw)
    return defaults


class TestGetInventory:
    """Tests for GET /api/inventory/ endpoint."""

    def test_get_inventory_success(self, client, admin_headers):
        """Test admin can list inventory with per-location stock."""
        rows = [_stock_row()]
        with patch("backend.modules.inventory.service.InventoryService.get_inventory") as mock_get:
            mock_get.return_value = rows
            response = client.get("/api/inventory/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["data"][0]["warehouse_qty"] == 50
            assert data["data"][0]["store_qty"] == 10

    def test_get_inventory_no_token(self, client):
        """Test unauthenticated cannot list inventory."""
        response = client.get("/api/inventory/")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestGetSummary:
    """Tests for GET /api/inventory/summary endpoint."""

    def test_summary_success(self, client, admin_headers):
        """Test summary includes per-location totals."""
        summary = {
            "total_products": 3,
            "total_quantity": 60,
            "warehouse_total": 50,
            "store_total": 10,
            "total_value": 900.0,
            "low_stock_count": 1,
        }
        with patch("backend.modules.inventory.service.InventoryService.get_summary") as mock_summary:
            mock_summary.return_value = summary
            response = client.get("/api/inventory/summary", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["data"]["warehouse_total"] == 50
            assert data["data"]["store_total"] == 10


class TestGetMovements:
    """Tests for GET /api/inventory/movements endpoint."""

    def test_movements_success(self, client, admin_headers):
        """Test movement history with filters."""
        movements = [
            {
                "id": 1,
                "product_id": 1,
                "product_name": "Keyboard",
                "from_location": "warehouse",
                "to_location": "store",
                "quantity": 5,
                "movement_type": "transfer",
                "created_at": "2026-08-01T10:00:00",
            }
        ]
        with patch("backend.modules.inventory.service.InventoryService.get_movements") as mock_get:
            mock_get.return_value = movements
            response = client.get(
                "/api/inventory/movements",
                headers=admin_headers,
                query_string={"movement_type": "transfer"},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"][0]["movement_type"] == "transfer"
            mock_get.assert_called_once()

    def test_movements_invalid_type(self, client, admin_headers):
        """Test invalid movement type returns 400."""
        with patch("backend.modules.inventory.service.InventoryService.get_movements") as mock_get:
            mock_get.side_effect = ValueError("Invalid movement type")
            response = client.get(
                "/api/inventory/movements",
                headers=admin_headers,
                query_string={"movement_type": "bogus"},
            )
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False


class TestTransferStock:
    """Tests for POST /api/inventory/transfer endpoint."""

    def test_transfer_success(self, client, admin_headers):
        """Test admin can transfer stock from warehouse to store."""
        result = {
            "product_id": 1,
            "quantity": 10,
            "from_location": "warehouse",
            "to_location": "store",
        }
        with patch("backend.modules.inventory.service.InventoryService.transfer_stock") as mock_transfer:
            mock_transfer.return_value = result
            response = client.post(
                "/api/inventory/transfer",
                headers=admin_headers,
                json={"product_id": 1, "quantity": 10},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["to_location"] == "store"

    def test_transfer_insufficient_stock(self, client, admin_headers):
        """Test transfer exceeding warehouse stock returns 400."""
        with patch("backend.modules.inventory.service.InventoryService.transfer_stock") as mock_transfer:
            mock_transfer.side_effect = ValueError(
                "Insufficient warehouse stock: available 5, requested 10"
            )
            response = client.post(
                "/api/inventory/transfer",
                headers=admin_headers,
                json={"product_id": 1, "quantity": 10},
            )
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_transfer_missing_quantity(self, client, admin_headers):
        """Test transfer without quantity returns 400."""
        response = client.post(
            "/api/inventory/transfer",
            headers=admin_headers,
            json={"product_id": 1},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_transfer_employee_forbidden(self, client, employee_headers):
        """Test employees cannot transfer stock."""
        response = client.post(
            "/api/inventory/transfer",
            headers=employee_headers,
            json={"product_id": 1, "quantity": 5},
        )
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestAdjustStock:
    """Tests for POST /api/inventory/adjust endpoint."""

    def test_adjust_success(self, client, admin_headers):
        """Test admin can adjust stock at a location."""
        result = {
            "product_id": 1,
            "location": "store",
            "quantity": 5,
            "movement_type": "adjustment",
            "new_quantity": 15,
        }
        with patch("backend.modules.inventory.service.InventoryService.adjust_stock") as mock_adjust:
            mock_adjust.return_value = result
            response = client.post(
                "/api/inventory/adjust",
                headers=admin_headers,
                json={
                    "product_id": 1,
                    "location": "store",
                    "quantity": 5,
                    "movement_type": "adjustment",
                },
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["new_quantity"] == 15

    def test_adjust_invalid_location(self, client, admin_headers):
        """Test invalid location returns 400."""
        with patch("backend.modules.inventory.service.InventoryService.adjust_stock") as mock_adjust:
            mock_adjust.side_effect = ValueError("Invalid location")
            response = client.post(
                "/api/inventory/adjust",
                headers=admin_headers,
                json={
                    "product_id": 1,
                    "location": "yard",
                    "quantity": 5,
                    "movement_type": "adjustment",
                },
            )
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_adjust_missing_location(self, client, admin_headers):
        """Test adjustment without location returns 400."""
        response = client.post(
            "/api/inventory/adjust",
            headers=admin_headers,
            json={"product_id": 1, "quantity": 5},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_adjust_employee_forbidden(self, client, employee_headers):
        """Test employees cannot adjust stock."""
        response = client.post(
            "/api/inventory/adjust",
            headers=employee_headers,
            json={
                "product_id": 1,
                "location": "store",
                "quantity": 5,
                "movement_type": "adjustment",
            },
        )
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False
