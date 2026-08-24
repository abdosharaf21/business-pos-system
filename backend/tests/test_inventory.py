"""Tests for Inventory API endpoints.

Tests the /api/inventory/* endpoints including per-location stock
retrieval, movement history, transfers, adjustments, and role-based
access control.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import mysql.connector

from backend.modules.inventory.model import StockLevel, StockMovement
from backend.modules.inventory.repository import InventoryRepository
from backend.modules.inventory.service import InventoryService
from backend.shared.expiration import classify_expiration


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


class _FakeCursor:
    """Cursor that records statements and serves canned results."""

    def __init__(self):
        self.executed = []
        self.fetchall_rows = []
        self.fetchone_row = None
        self.rowcount = 0

    def execute(self, sql, params=None):
        self.executed.append((sql, params))
        return None

    def fetchall(self):
        return self.fetchall_rows

    def fetchone(self):
        return self.fetchone_row

    def close(self):
        pass


class _FakeConnection:
    """Context-manager connection for repository tests."""

    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False
        cursor.connection = self

    def cursor(self, dictionary=True):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class _FakeDatabase:
    """Minimal Database stand-in with a configurable connection."""

    def __init__(self, connection):
        self._connection = connection

    def connection(self):
        return self._connection


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


class TestUpdateExpirationDate:
    """Tests for the inventory expiration date editing feature.

    Covers the service that writes the date to the product's purchase_items
    records (whether undated or already dated) and the PUT endpoint that
    exposes it, including validation and role-based access.
    """

    def test_service_applies_expiration_date(self):
        """Test the date is applied to the product's purchase items."""
        repo = MagicMock()
        repo.get_product_by_id.return_value = {"id": 1, "status": "active"}
        repo.update_product_expiration.return_value = {
            "updated_rows": 2,
            "expiration_date": "2027-03-15",
        }
        service = InventoryService(repo)
        result = service.update_expiration_date(1, "2027-03-15")
        assert result["updated_rows"] == 2
        assert result["expiration_date"] == "2027-03-15"
        repo.update_product_expiration.assert_called_once_with(
            product_id=1,
            expiration_date="2027-03-15",
        )

    def test_service_allows_editing_existing_date(self):
        """Test a product whose items already have a date can be re-dated."""
        repo = MagicMock()
        repo.get_product_by_id.return_value = {"id": 1, "status": "active"}
        repo.update_product_expiration.return_value = {
            "updated_rows": 2,
            "expiration_date": "2027-06-30",
        }
        service = InventoryService(repo)
        result = service.update_expiration_date(1, "2027-06-30")
        assert result["updated_rows"] == 2
        assert result["expiration_date"] == "2027-06-30"

    def test_inventory_refresh_returns_updated_expiration(self):
        """Test the inventory list shows the updated date and status."""
        repo = MagicMock()
        repo.get_inventory_with_stock.return_value = [
            {"id": 1, "expiration_date": "2027-03-15", "status": "active"}
        ]
        service = InventoryService(repo)
        rows = service.get_inventory()
        assert rows[0]["expiration_date"] == "2027-03-15"
        assert rows[0]["expiration_status"] == "normal"

    def test_service_rejects_invalid_date(self):
        """Test a malformed date raises ValueError before any write."""
        repo = MagicMock()
        repo.get_product_by_id.return_value = {"id": 1, "status": "active"}
        service = InventoryService(repo)
        try:
            service.update_expiration_date(1, "not-a-date")
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "YYYY-MM-DD" in str(exc)
        repo.update_product_expiration.assert_not_called()

    def test_service_rejects_missing_product(self):
        """Test an unknown product raises ValueError."""
        repo = MagicMock()
        repo.get_product_by_id.return_value = None
        service = InventoryService(repo)
        try:
            service.update_expiration_date(999, "2027-03-15")
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Product not found" in str(exc)

    def test_service_rejects_inactive_product(self):
        """Test an inactive product cannot have its expiration edited."""
        repo = MagicMock()
        repo.get_product_by_id.return_value = {"id": 1, "status": "inactive"}
        service = InventoryService(repo)
        try:
            service.update_expiration_date(1, "2027-03-15")
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "inactive" in str(exc)

    def test_service_rejects_product_without_purchase_items(self):
        """Test a product with no purchase items raises ValueError."""
        repo = MagicMock()
        repo.get_product_by_id.return_value = {"id": 1, "status": "active"}
        repo.update_product_expiration.return_value = {
            "updated_rows": 0,
            "batch_count": 0,
            "expiration_date": None,
        }
        service = InventoryService(repo)
        try:
            service.update_expiration_date(1, "2027-03-15")
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "No purchase items found" in str(exc)

    def test_service_rejects_multiple_batches(self):
        """Test a product with several batches requires batch selection."""
        repo = MagicMock()
        repo.get_product_by_id.return_value = {"id": 1, "status": "active"}
        repo.update_product_expiration.return_value = {
            "updated_rows": 0,
            "batch_count": 3,
            "expiration_date": None,
        }
        service = InventoryService(repo)
        try:
            service.update_expiration_date(1, "2027-03-15")
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Multiple purchase batches" in str(exc)
            assert "batch selection" in str(exc).lower()

    def test_admin_can_update_expiration(self, client, admin_headers):
        """Test an admin can update a product's expiration date."""
        with patch("backend.modules.inventory.service.InventoryService.update_expiration_date") as mock_update:
            mock_update.return_value = {
                "updated_rows": 1,
                "expiration_date": "2027-03-15",
            }
            response = client.put(
                "/api/inventory/1/expiration",
                headers=admin_headers,
                json={"expiration_date": "2027-03-15"},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["expiration_date"] == "2027-03-15"
            mock_update.assert_called_once_with(
                product_id=1,
                expiration_date="2027-03-15",
            )

    def test_manager_can_update_expiration(self, client, manager_headers):
        """Test a manager can update a product's expiration date."""
        with patch("backend.modules.inventory.service.InventoryService.update_expiration_date") as mock_update:
            mock_update.return_value = {
                "updated_rows": 1,
                "expiration_date": "2027-03-15",
            }
            response = client.put(
                "/api/inventory/1/expiration",
                headers=manager_headers,
                json={"expiration_date": "2027-03-15"},
            )
            assert response.status_code == 200
            assert response.get_json()["success"] is True

    def test_employee_forbidden(self, client, employee_headers):
        """Test employees cannot edit expiration dates."""
        response = client.put(
            "/api/inventory/1/expiration",
            headers=employee_headers,
            json={"expiration_date": "2027-03-15"},
        )
        assert response.status_code == 403
        assert response.get_json()["success"] is False

    def test_missing_date_returns_400(self, client, admin_headers):
        """Test a missing expiration date returns 400."""
        response = client.put(
            "/api/inventory/1/expiration",
            headers=admin_headers,
            json={},
        )
        assert response.status_code == 400
        assert response.get_json()["success"] is False

    def test_service_error_returns_400(self, client, admin_headers):
        """Test a service ValueError is surfaced as 400."""
        with patch("backend.modules.inventory.service.InventoryService.update_expiration_date") as mock_update:
            mock_update.side_effect = ValueError(
                "No purchase items found for this product"
            )
            response = client.put(
                "/api/inventory/1/expiration",
                headers=admin_headers,
                json={"expiration_date": "2027-03-15"},
            )
            assert response.status_code == 400
            assert response.get_json()["success"] is False


class TestUpdateExpirationDateRepository:
    """Tests for the SQL behind the expiration date edit.

    Verifies the repository only updates the product's single purchase
    batch, without filtering on ``expiration_date IS NULL``, and that a
    product with multiple batches is never updated so the caller can
    require explicit batch selection. This guards the regression where
    editing a product that already had an expiration date matched nothing.
    """

    def _make_repository(self, cursor):
        """Build an InventoryRepository bound to a fake database.

        Args:
            cursor: Fake cursor serving canned results.

        Returns:
            InventoryRepository instance backed by the fake database.
        """
        fake_db = _FakeDatabase(_FakeConnection(cursor))
        return InventoryRepository(fake_db)

    def _statements(self, cursor):
        """Return the SQL strings executed against the cursor.

        Args:
            cursor: Fake cursor that recorded executed statements.

        Returns:
            List of SQL strings in execution order.
        """
        return [sql for sql, _ in cursor.executed]

    def test_null_to_date_updates_single_batch(self):
        """Test a first expiration date is applied to the single batch."""
        cursor = _FakeCursor()
        cursor.fetchall_rows = [{"id": 7}]
        cursor.fetchone_row = {"min_date": date(2027, 3, 15)}
        repository = self._make_repository(cursor)

        result = repository.update_product_expiration(
            product_id=1, expiration_date="2027-03-15"
        )

        assert result["updated_rows"] == 1
        assert result["batch_count"] == 1
        assert result["expiration_date"] == "2027-03-15"
        statements = self._statements(cursor)
        assert statements[0].startswith("SELECT id FROM purchase_items")
        assert "FOR UPDATE" in statements[0]
        assert "expiration_date IS NULL" not in statements[0]
        assert statements[1].startswith("UPDATE purchase_items SET expiration_date")
        assert "expiration_date IS NULL" not in statements[1]
        assert "WHERE id = %s" in statements[1]
        assert cursor.executed[0][1] == (1,)
        assert cursor.executed[1][1] == ("2027-03-15", 7)
        assert cursor.connection.committed is True

    def test_existing_date_to_different_date_updates_single_batch(self):
        """Test changing an existing date updates the single batch."""
        cursor = _FakeCursor()
        cursor.fetchall_rows = [{"id": 5}]
        cursor.fetchone_row = {"min_date": date(2027, 6, 30)}
        repository = self._make_repository(cursor)

        result = repository.update_product_expiration(
            product_id=1, expiration_date="2027-06-30"
        )

        assert result["updated_rows"] == 1
        assert result["expiration_date"] == "2027-06-30"
        statements = self._statements(cursor)
        assert "expiration_date IS NULL" not in statements[0]
        assert "expiration_date IS NULL" not in statements[1]
        assert cursor.executed[1][1] == ("2027-06-30", 5)

    def test_existing_date_to_another_existing_date_edits(self):
        """Test a product already fully dated can still be re-dated."""
        cursor = _FakeCursor()
        cursor.fetchall_rows = [{"id": 9}]
        cursor.fetchone_row = {"min_date": date(2027, 3, 15)}
        repository = self._make_repository(cursor)

        result = repository.update_product_expiration(
            product_id=1, expiration_date="2027-03-15"
        )

        assert result["updated_rows"] == 1
        assert result["expiration_date"] == "2027-03-15"
        assert cursor.connection.committed is True

    def test_multiple_batches_are_not_updated(self):
        """Test a product with several batches is never modified."""
        cursor = _FakeCursor()
        cursor.fetchall_rows = [{"id": 1}, {"id": 2}, {"id": 3}]
        cursor.fetchone_row = {"min_date": None}
        repository = self._make_repository(cursor)

        result = repository.update_product_expiration(
            product_id=1, expiration_date="2027-03-15"
        )

        assert result["updated_rows"] == 0
        assert result["batch_count"] == 3
        assert result["expiration_date"] is None
        statements = self._statements(cursor)
        assert len(statements) == 2
        assert not any(
            sql.startswith("UPDATE purchase_items") for sql in statements
        )
        assert cursor.connection.committed is True

    def test_inventory_refresh_returns_updated_min_date(self):
        """Test the effective expiration date is the updated MIN date."""
        cursor = _FakeCursor()
        cursor.fetchall_rows = [{"id": 4}]
        cursor.fetchone_row = {"min_date": date(2027, 3, 15)}
        repository = self._make_repository(cursor)

        result = repository.update_product_expiration(
            product_id=7, expiration_date="2027-03-15"
        )

        assert result["updated_rows"] == 1
        assert result["expiration_date"] == "2027-03-15"
        assert cursor.executed[2][0].startswith("SELECT MIN(expiration_date)")
        assert cursor.executed[2][1] == (7,)

    def test_rollback_on_database_error(self):
        """Test the transaction rolls back when a statement fails."""
        cursor = _FakeCursor()
        cursor.fetchall_rows = [{"id": 1}]

        def _boom(sql, params=None):
            if sql.startswith("UPDATE"):
                raise mysql.connector.Error("connection lost")

        cursor.execute = _boom
        repository = self._make_repository(cursor)

        try:
            repository.update_product_expiration(
                product_id=1, expiration_date="2027-03-15"
            )
            assert False, "Expected mysql.connector.Error"
        except mysql.connector.Error:
            pass
        assert cursor.connection.rolled_back is True
        assert cursor.connection.committed is False
