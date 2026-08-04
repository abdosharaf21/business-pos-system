"""Tests for Notification API endpoints and service logic.

Covers the /api/notifications/* endpoints including listing,
unread counting, synchronization, and marking notifications as
read, plus the service-level generation rules (priorities, stock
and expiration classification, stale cleanup, and read state).
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from backend.modules.notifications.model import Notification
from backend.modules.notifications.service import NotificationService


def _stock_product(**kw):
    """Create a fake product-with-stock row dict."""
    defaults = dict(
        id=1,
        name="Keyboard",
        barcode="123",
        sku="KB-1",
        minimum_stock=5,
        total_quantity=10,
    )
    defaults.update(kw)
    return defaults


def _expiry_product(**kw):
    """Create a fake product-with-expiration row dict."""
    defaults = dict(
        id=2,
        name="Milk",
        barcode="456",
        sku="MK-2",
        total_quantity=10,
        expiration_date=date.today() - timedelta(days=1),
    )
    defaults.update(kw)
    return defaults


def _notification(**kw):
    """Create a fake Notification instance."""
    defaults = dict(
        id=1,
        product_id=1,
        notification_type="low_stock",
        priority="warning",
        is_read=False,
        created_at="2026-08-01T10:00:00",
        product_name="Keyboard",
        barcode="123",
        sku="KB-1",
        quantity=3,
    )
    defaults.update(kw)
    return Notification.from_dict(defaults)


class TestSyncNotifications:
    """Tests for the notification generation rules."""

    def test_generates_all_four_types(self):
        """Test all alert types are produced from product state."""
        repo = MagicMock()
        repo.get_products_with_stock.return_value = [
            _stock_product(id=1, total_quantity=0, minimum_stock=5),
            _stock_product(id=2, total_quantity=2, minimum_stock=5),
        ]
        repo.get_products_with_expiration.return_value = [
            _expiry_product(id=3, expiration_date=date.today() - timedelta(days=1)),
            _expiry_product(id=4, expiration_date=date.today() + timedelta(days=10)),
        ]
        repo.get_existing_keys.return_value = []
        service = NotificationService(repo)

        result = service.sync_notifications()

        expected = {
            (1, "out_of_stock"),
            (2, "low_stock"),
            (3, "expired"),
            (4, "expiring_soon"),
        }
        upserted = {
            (call.kwargs["product_id"], call.kwargs["notification_type"]) for call in repo.upsert_notification.call_args_list
        }
        assert upserted == expected
        assert result["created"] == 4
        assert result["deleted"] == 0

    def test_out_of_stock_wins_over_low_stock(self):
        """Test a zero-quantity product gets only out_of_stock."""
        repo = MagicMock()
        repo.get_products_with_stock.return_value = [
            _stock_product(id=1, total_quantity=0, minimum_stock=0),
        ]
        repo.get_products_with_expiration.return_value = []
        repo.get_existing_keys.return_value = []
        service = NotificationService(repo)

        service.sync_notifications()

        calls = repo.upsert_notification.call_args_list
        assert len(calls) == 1
        assert calls[0].kwargs["notification_type"] == "out_of_stock"
        assert calls[0].kwargs["priority"] == "critical"

    def test_low_stock_requires_positive_minimum(self):
        """Test minimum_stock of zero never produces low_stock."""
        repo = MagicMock()
        repo.get_products_with_stock.return_value = [
            _stock_product(id=1, total_quantity=4, minimum_stock=0),
            _stock_product(id=2, total_quantity=4, minimum_stock=5),
        ]
        repo.get_products_with_expiration.return_value = []
        repo.get_existing_keys.return_value = []
        service = NotificationService(repo)

        service.sync_notifications()

        types = {call.kwargs["notification_type"] for call in repo.upsert_notification.call_args_list}
        assert types == {"low_stock"}

    def test_stock_below_minimum_is_low_stock(self):
        """Test total at or below minimum_stock produces low_stock."""
        repo = MagicMock()
        repo.get_products_with_stock.return_value = [
            _stock_product(id=1, total_quantity=5, minimum_stock=5),
            _stock_product(id=2, total_quantity=6, minimum_stock=5),
        ]
        repo.get_products_with_expiration.return_value = []
        repo.get_existing_keys.return_value = []
        service = NotificationService(repo)

        service.sync_notifications()

        types = {call.kwargs["notification_type"] for call in repo.upsert_notification.call_args_list}
        assert types == {"low_stock"}

    def test_expiration_priority_mapping(self):
        """Test expired maps to critical and expiring_soon to warning."""
        repo = MagicMock()
        repo.get_products_with_stock.return_value = []
        repo.get_products_with_expiration.return_value = [
            _expiry_product(id=1, expiration_date=date.today() - timedelta(days=1)),
            _expiry_product(id=2, expiration_date=date.today() + timedelta(days=10)),
        ]
        repo.get_existing_keys.return_value = []
        service = NotificationService(repo)

        service.sync_notifications()

        by_type = {call.kwargs["notification_type"]: call.kwargs["priority"] for call in repo.upsert_notification.call_args_list}
        assert by_type == {"expired": "critical", "expiring_soon": "warning"}

    def test_normal_expiration_clears_stale_rows(self):
        """Test a normal expiration deletes stored expiration alerts."""
        repo = MagicMock()
        repo.get_products_with_stock.return_value = []
        repo.get_products_with_expiration.return_value = [
            _expiry_product(id=1, expiration_date=date.today() + timedelta(days=90)),
        ]
        repo.get_existing_keys.return_value = [(1, "expired")]
        service = NotificationService(repo)

        result = service.sync_notifications()

        assert repo.delete_stale_notifications.call_count == 1
        assert list(repo.delete_stale_notifications.call_args.args[0]) == [(1, "expired")]
        assert result["deleted"] == 1

    def test_resolved_situation_deletes_notification(self):
        """Test a restocked product clears its out-of-stock notification."""
        repo = MagicMock()
        repo.get_products_with_stock.return_value = [
            _stock_product(id=1, total_quantity=50, minimum_stock=5),
        ]
        repo.get_products_with_expiration.return_value = []
        repo.get_existing_keys.return_value = [(1, "out_of_stock")]
        service = NotificationService(repo)

        result = service.sync_notifications()

        assert result["deleted"] == 1
        assert repo.upsert_notification.call_count == 0

    def test_upsert_refreshes_priority_for_existing_row(self):
        """Test an existing row is upserted and counted as updated."""
        repo = MagicMock()
        repo.get_products_with_stock.return_value = [
            _stock_product(id=1, total_quantity=0, minimum_stock=5),
        ]
        repo.get_products_with_expiration.return_value = []
        repo.get_existing_keys.return_value = [(1, "out_of_stock")]
        service = NotificationService(repo)

        result = service.sync_notifications()

        assert result["created"] == 0
        assert result["updated"] == 1
        assert repo.delete_stale_notifications.call_args.args[0] == []


class TestGetNotifications:
    """Tests for listing and filtering notifications."""

    def test_lists_newest_first(self):
        """Test notifications are returned as dicts."""
        repo = MagicMock()
        repo.get_products_with_stock.return_value = []
        repo.get_products_with_expiration.return_value = []
        repo.get_existing_keys.return_value = []
        repo.get_all_notifications.return_value = [_notification()]
        service = NotificationService(repo)

        result = service.get_notifications()

        assert result[0]["notification_type"] == "low_stock"
        assert result[0]["product_name"] == "Keyboard"

    def test_filters_by_type(self):
        """Test listing filters by notification type."""
        repo = MagicMock()
        repo.get_products_with_stock.return_value = []
        repo.get_products_with_expiration.return_value = []
        repo.get_existing_keys.return_value = []
        repo.get_all_notifications.return_value = [
            _notification(id=1, notification_type="low_stock"),
            _notification(id=2, notification_type="expired"),
        ]
        service = NotificationService(repo)

        result = service.get_notifications(notification_type="expired")

        assert len(result) == 1
        assert result[0]["id"] == 2

    def test_filters_by_priority(self):
        """Test listing filters by priority."""
        repo = MagicMock()
        repo.get_products_with_stock.return_value = []
        repo.get_products_with_expiration.return_value = []
        repo.get_existing_keys.return_value = []
        repo.get_all_notifications.return_value = [
            _notification(id=1, priority="warning"),
            _notification(id=2, priority="critical"),
        ]
        service = NotificationService(repo)

        result = service.get_notifications(priority="critical")

        assert len(result) == 1
        assert result[0]["id"] == 2

    def test_filters_unread_only(self):
        """Test listing with unread_only excludes read notifications."""
        repo = MagicMock()
        repo.get_products_with_stock.return_value = []
        repo.get_products_with_expiration.return_value = []
        repo.get_existing_keys.return_value = []
        repo.get_all_notifications.return_value = [
            _notification(id=1, is_read=False),
            _notification(id=2, is_read=True),
        ]
        service = NotificationService(repo)

        result = service.get_notifications(unread_only=True)

        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_invalid_type_rejected(self):
        """Test an invalid notification type raises ValueError."""
        service = NotificationService(MagicMock())
        try:
            service.get_notifications(notification_type="bogus")
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Invalid notification type" in str(exc)

    def test_invalid_priority_rejected(self):
        """Test an invalid priority raises ValueError."""
        service = NotificationService(MagicMock())
        try:
            service.get_notifications(priority="urgent")
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Invalid priority" in str(exc)


class TestReadOperations:
    """Tests for unread counting and marking as read."""

    def test_unread_count(self):
        """Test unread count is returned."""
        repo = MagicMock()
        repo.get_unread_count.return_value = 3
        service = NotificationService(repo)

        assert service.get_unread_count() == 3

    def test_mark_as_read_success(self):
        """Test marking a notification as read returns its state."""
        repo = MagicMock()
        repo.mark_as_read.return_value = True
        service = NotificationService(repo)

        result = service.mark_as_read(7)

        assert result["id"] == 7
        assert result["is_read"] is True

    def test_mark_as_read_not_found(self):
        """Test marking a missing notification raises ValueError."""
        repo = MagicMock()
        repo.mark_as_read.return_value = False
        service = NotificationService(repo)

        try:
            service.mark_as_read(999)
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "Notification not found" in str(exc)

    def test_mark_all_as_read(self):
        """Test marking all returns the number updated."""
        repo = MagicMock()
        repo.mark_all_as_read.return_value = 4
        service = NotificationService(repo)

        assert service.mark_all_as_read() == 4


class TestNotificationRoutes:
    """Tests for the /api/notifications/* endpoints."""

    def test_list_success(self, client, admin_headers):
        """Test admin can list notifications."""
        notifications = [
            {
                "id": 1,
                "product_id": 1,
                "notification_type": "low_stock",
                "priority": "warning",
                "is_read": False,
                "product_name": "Keyboard",
                "quantity": 3,
            }
        ]
        with patch(
            "backend.modules.notifications.service.NotificationService.get_notifications"
        ) as mock_get:
            mock_get.return_value = notifications
            response = client.get(
                "/api/notifications/", headers=admin_headers
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"][0]["notification_type"] == "low_stock"

    def test_list_forwards_filters(self, client, admin_headers):
        """Test list endpoint forwards type, priority, and limit params."""
        with patch(
            "backend.modules.notifications.service.NotificationService.get_notifications"
        ) as mock_get:
            mock_get.return_value = []
            response = client.get(
                "/api/notifications/?notification_type=expired&priority=critical&limit=10",
                headers=admin_headers,
            )
            assert response.status_code == 200
            kwargs = mock_get.call_args.kwargs
            assert kwargs["notification_type"] == "expired"
            assert kwargs["priority"] == "critical"
            assert kwargs["limit"] == 10

    def test_list_invalid_type(self, client, admin_headers):
        """Test invalid notification_type returns 400."""
        with patch(
            "backend.modules.notifications.service.NotificationService.get_notifications"
        ) as mock_get:
            mock_get.side_effect = ValueError("Invalid notification type")
            response = client.get(
                "/api/notifications/?notification_type=bogus",
                headers=admin_headers,
            )
            assert response.status_code == 400
            assert response.get_json()["success"] is False

    def test_unread_count_success(self, client, admin_headers):
        """Test admin can get the unread count."""
        with patch(
            "backend.modules.notifications.service.NotificationService.get_unread_count"
        ) as mock_count:
            mock_count.return_value = 2
            response = client.get(
                "/api/notifications/unread-count", headers=admin_headers
            )
            assert response.status_code == 200
            assert response.get_json()["data"]["unread_count"] == 2

    def test_sync_admin_allowed(self, client, admin_headers):
        """Test admin can trigger a notification sync."""
        with patch(
            "backend.modules.notifications.service.NotificationService.sync_notifications"
        ) as mock_sync:
            mock_sync.return_value = {"created": 3, "updated": 1, "deleted": 0}
            response = client.post(
                "/api/notifications/sync", headers=admin_headers
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["created"] == 3

    def test_sync_employee_forbidden(self, client, employee_headers):
        """Test employees cannot trigger a notification sync."""
        response = client.post(
            "/api/notifications/sync", headers=employee_headers
        )
        assert response.status_code == 403

    def test_mark_as_read_success(self, client, admin_headers):
        """Test admin can mark a notification as read."""
        with patch(
            "backend.modules.notifications.service.NotificationService.mark_as_read"
        ) as mock_read:
            mock_read.return_value = {"id": 1, "is_read": True}
            response = client.post(
                "/api/notifications/1/read", headers=admin_headers
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["is_read"] is True

    def test_mark_as_read_not_found(self, client, admin_headers):
        """Test marking a missing notification returns 404."""
        with patch(
            "backend.modules.notifications.service.NotificationService.mark_as_read"
        ) as mock_read:
            mock_read.side_effect = ValueError("Notification not found")
            response = client.post(
                "/api/notifications/999/read", headers=admin_headers
            )
            assert response.status_code == 404
            assert response.get_json()["success"] is False

    def test_mark_all_as_read_success(self, client, admin_headers):
        """Test admin can mark all notifications as read."""
        with patch(
            "backend.modules.notifications.service.NotificationService.mark_all_as_read"
        ) as mock_all:
            mock_all.return_value = 3
            response = client.post(
                "/api/notifications/read-all", headers=admin_headers
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["updated"] == 3

    def test_list_no_token(self, client):
        """Test unauthenticated cannot list notifications."""
        response = client.get("/api/notifications/")
        assert response.status_code == 401
