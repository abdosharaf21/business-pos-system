"""Tests for Inventory API endpoints.

Tests the /api/inventory/* endpoints including per-location stock
retrieval, movement history, transfers, adjustments, and role-based
access control.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from backend.modules.inventory.model import StockLevel, StockMovement
from backend.modules.inventory.service import InventoryService
from backend.utils.expiration import classify_expiration


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


class TestNoDirectAdjustment:
    """Tests that direct stock adjustment is removed.

    Inventory quantity must never be edited directly. The only manual
    stock corrections flow through the Inventory Audit module, so the
    legacy /api/inventory/adjust endpoint must not exist.
    """

    def test_adjust_endpoint_removed(self, client, admin_headers):
        """Test the direct adjustment endpoint returns 404."""
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
        assert response.status_code == 404

    def test_adjust_endpoint_removed_for_employee(self, client, employee_headers):
        """Test the direct adjustment endpoint is gone for every role."""
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
        assert response.status_code == 404


class TestExpirationClassification:
    """Tests for the expiration status classifier."""

    def test_expired_past_date(self):
        """Test a date before today is classified expired."""
        assert classify_expiration(date.today() - timedelta(days=1)) == "expired"

    def test_expiring_soon_within_threshold(self):
        """Test a date within the default 30-day threshold."""
        assert classify_expiration(date.today() + timedelta(days=10)) == "expiring_soon"

    def test_expiring_soon_on_threshold_boundary(self):
        """Test a date exactly on the threshold boundary is expiring soon."""
        assert classify_expiration(date.today() + timedelta(days=30)) == "expiring_soon"

    def test_normal_beyond_threshold(self):
        """Test a date beyond the threshold is normal."""
        assert classify_expiration(date.today() + timedelta(days=60)) == "normal"

    def test_normal_today_classified_expiring_soon(self):
        """Test today's date is classified expiring soon."""
        assert classify_expiration(date.today()) == "expiring_soon"

    def test_none_returns_none(self):
        """Test no expiration date returns None."""
        assert classify_expiration(None) is None

    def test_custom_threshold(self):
        """Test a custom threshold changes the classification."""
        assert classify_expiration(
            date.today() + timedelta(days=60), expiring_soon_days=90
        ) == "expiring_soon"

    def test_iso_string_input(self):
        """Test a YYYY-MM-DD string is classified correctly."""
        future = date.today() + timedelta(days=5)
        assert classify_expiration(future.isoformat()) == "expiring_soon"


class TestGetInventoryExpiration:
    """Tests for expiration classification, filtering, and sorting."""

    def _expiry_row(self, name, expiration_date, **kw):
        """Create an inventory row dict with an expiration date."""
        defaults = _stock_row(name=name)
        defaults["expiration_date"] = expiration_date
        defaults.update(kw)
        return defaults

    def test_classifies_expiration_status(self):
        """Test rows get an expiration_status from their date."""
        repo = MagicMock()
        repo.get_inventory_with_stock.return_value = [
            self._expiry_row("Expired", date.today() - timedelta(days=5)),
            self._expiry_row("Soon", date.today() + timedelta(days=5)),
            self._expiry_row("Valid", date.today() + timedelta(days=90)),
            self._expiry_row("No Date", None),
        ]
        service = InventoryService(repo)
        rows = service.get_inventory()
        statuses = {row["name"]: row["expiration_status"] for row in rows}
        assert statuses["Expired"] == "expired"
        assert statuses["Soon"] == "expiring_soon"
        assert statuses["Valid"] == "normal"
        assert statuses["No Date"] is None

    def test_filters_by_expiration_status(self):
        """Test filtering by expiration_status returns only matching rows."""
        repo = MagicMock()
        repo.get_inventory_with_stock.return_value = [
            self._expiry_row("Expired", date.today() - timedelta(days=5)),
            self._expiry_row("Soon", date.today() + timedelta(days=5)),
            self._expiry_row("Valid", date.today() + timedelta(days=90)),
        ]
        service = InventoryService(repo)
        rows = service.get_inventory(expiration_status="expired")
        assert [row["name"] for row in rows] == ["Expired"]

        rows = service.get_inventory(expiration_status="expiring_soon")
        assert [row["name"] for row in rows] == ["Soon"]

        rows = service.get_inventory(expiration_status="normal")
        assert [row["name"] for row in rows] == ["Valid"]

    def test_invalid_expiration_filter_rejected(self):
        """Test an invalid expiration_status value raises ValueError."""
        repo = MagicMock()
        service = InventoryService(repo)
        try:
            service.get_inventory(expiration_status="almost_expired")
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Invalid expiration filter" in str(exc)

    def test_sorts_by_expiration_date(self):
        """Test sort=expiration orders oldest dates first and None last."""
        repo = MagicMock()
        repo.get_inventory_with_stock.return_value = [
            self._expiry_row("No Date", None),
            self._expiry_row("Valid", date.today() + timedelta(days=90)),
            self._expiry_row("Soon", date.today() + timedelta(days=5)),
            self._expiry_row("Expired", date.today() - timedelta(days=5)),
        ]
        service = InventoryService(repo)
        rows = service.get_inventory(sort="expiration")
        assert [row["name"] for row in rows] == ["Expired", "Soon", "Valid", "No Date"]

    def test_invalid_sort_rejected(self):
        """Test an invalid sort value raises ValueError."""
        repo = MagicMock()
        service = InventoryService(repo)
        try:
            service.get_inventory(sort="quantity")
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Invalid sort" in str(exc)

    def test_route_forwards_filter_and_sort(self, client, admin_headers):
        """Test GET /api/inventory/ forwards filter and sort params."""
        with patch("backend.modules.inventory.service.InventoryService.get_inventory") as mock_get:
            mock_get.return_value = [_stock_row()]
            response = client.get(
                "/api/inventory/?expiration_status=expired&sort=expiration",
                headers=admin_headers,
            )
            assert response.status_code == 200
            kwargs = mock_get.call_args.kwargs
            assert kwargs["expiration_status"] == "expired"
            assert kwargs["sort"] == "expiration"

    def test_route_rejects_invalid_filter(self, client, admin_headers):
        """Test an invalid filter value returns 400."""
        with patch("backend.modules.inventory.service.InventoryService.get_inventory") as mock_get:
            mock_get.side_effect = ValueError("Invalid expiration filter. Must be one of: expired, expiring_soon, normal")
            response = client.get(
                "/api/inventory/?expiration_status=bogus",
                headers=admin_headers,
            )
            assert response.status_code == 400
            assert response.get_json()["success"] is False
