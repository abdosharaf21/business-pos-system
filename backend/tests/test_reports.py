"""Tests for Reports API endpoints with expiration status.

Uses mocked services so no real database is needed. Follows the same
pattern as other module tests (service patched, routes exercised).
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from backend.modules.reports.service import ReportService
from backend.modules.reports.repository import ReportRepository


def _inventory_row(name, expiration_date):
    """Build a fake inventory report row dict."""
    return {
        "id": 1,
        "name": name,
        "sku": "SKU-1",
        "barcode": "123",
        "category_name": "Dairy",
        "minimum_stock": 5,
        "purchase_price": 10.0,
        "warehouse_qty": 10,
        "store_qty": 5,
        "total": 15,
        "expiration_date": expiration_date,
    }


class TestInventoryReport:
    """Tests for GET /api/reports/inventory."""

    def test_report_includes_expiration_status(self, client, admin_headers):
        """Test inventory report rows carry a classified expiration status."""
        rows = [
            dict(_inventory_row("Expired", date.today() - timedelta(days=5)), expiration_status="expired"),
            dict(_inventory_row("Soon", date.today() + timedelta(days=5)), expiration_status="expiring_soon"),
            dict(_inventory_row("Valid", date.today() + timedelta(days=90)), expiration_status="normal"),
            dict(_inventory_row("No Date", None), expiration_status=None),
        ]
        with patch("backend.modules.reports.service.ReportService.get_inventory_report") as mock_get:
            mock_get.return_value = {"inventory": rows}
            response = client.get("/api/reports/inventory-report", headers=admin_headers)
            assert response.status_code == 200
            inventory = response.get_json()["data"]["inventory"]
            statuses = {row["name"]: row["expiration_status"] for row in inventory}
            assert statuses["Expired"] == "expired"
            assert statuses["Soon"] == "expiring_soon"
            assert statuses["Valid"] == "normal"
            assert statuses["No Date"] is None

    def test_report_without_expiration_dates(self, client, admin_headers):
        """Test legacy inventory rows without expiration stay valid."""
        legacy = [
            {
                "id": 1,
                "name": "Legacy",
                "sku": "SKU-L",
                "barcode": "999",
                "category_name": None,
                "minimum_stock": 2,
                "purchase_price": 5.0,
                "warehouse_qty": 3,
                "store_qty": 1,
                "total": 4,
            }
        ]
        with patch("backend.modules.reports.service.ReportService.get_inventory_report") as mock_get:
            mock_get.return_value = {"inventory": legacy}
            response = client.get("/api/reports/inventory-report", headers=admin_headers)
            assert response.status_code == 200
            inventory = response.get_json()["data"]["inventory"]
            assert inventory[0]["name"] == "Legacy"
            assert inventory[0].get("expiration_date") is None
            assert inventory[0].get("expiration_status") is None

    def test_service_classifies_expiration(self):
        """Test ReportService classifies expiration dates on repository rows."""
        repo = MagicMock(spec=ReportRepository)
        repo.get_inventory_report.return_value = [
            _inventory_row("Soon", date.today() + timedelta(days=10)),
        ]
        service = ReportService(repo, MagicMock(), MagicMock())
        result = service.get_inventory_report()
        assert result["inventory"][0]["expiration_status"] == "expiring_soon"
