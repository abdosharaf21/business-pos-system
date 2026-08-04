"""Notification service for generating and managing in-app alerts."""

from datetime import date
from typing import Any, Dict, List, Optional

from backend.config import Config
from backend.modules.notifications.model import Notification
from backend.modules.notifications.repository import NotificationRepository
from backend.utils.expiration import (
    EXPIRATION_STATUS_EXPIRED,
    EXPIRATION_STATUS_EXPIRING_SOON,
    EXPIRATION_STATUS_NORMAL,
    classify_expiration,
)

VALID_NOTIFICATION_TYPES = {
    Notification.TYPE_LOW_STOCK,
    Notification.TYPE_OUT_OF_STOCK,
    Notification.TYPE_EXPIRED,
    Notification.TYPE_EXPIRING_SOON,
}
VALID_PRIORITIES = {
    Notification.PRIORITY_CRITICAL,
    Notification.PRIORITY_WARNING,
}
TYPE_PRIORITY = {
    Notification.TYPE_OUT_OF_STOCK: Notification.PRIORITY_CRITICAL,
    Notification.TYPE_EXPIRED: Notification.PRIORITY_CRITICAL,
    Notification.TYPE_LOW_STOCK: Notification.PRIORITY_WARNING,
    Notification.TYPE_EXPIRING_SOON: Notification.PRIORITY_WARNING,
}
MAX_LIMIT = 200


class NotificationService:
    """Service for notification business operations.

    Generates notifications from live inventory and expiration data,
    keeps them in sync so resolved situations clear their read state,
    and handles listing, counting, and marking notifications as read.
    Communicates only with NotificationRepository for data access.
    """

    def __init__(self, notification_repository: NotificationRepository) -> None:
        """Initialize NotificationService with a NotificationRepository.

        Args:
            notification_repository: Repository for notification database operations.
        """
        self._repository = notification_repository

    # ------------------------------------------------------------------
    # Generation / synchronization
    # ------------------------------------------------------------------

    def sync_notifications(self, today: Optional[date] = None) -> Dict[str, int]:
        """Regenerate notifications from current product state.

        Computes every alert that currently applies (out of stock,
        low stock, expired, expiring soon), upserts those rows, and
        deletes rows for situations that have resolved so their read
        state clears. Out-of-stock takes precedence over low-stock.

        Args:
            today: Reference date for expiration classification.

        Returns:
            Dictionary with created, updated, and deleted counts.
        """
        desired_keys = self._compute_desired_keys(today)

        current_keys = set(self._repository.get_existing_keys())
        stale_keys = current_keys - desired_keys

        created = 0
        updated = 0
        for product_id, notification_type in sorted(desired_keys):
            priority = TYPE_PRIORITY[notification_type]
            was_present = (product_id, notification_type) in current_keys
            self._repository.upsert_notification(
                product_id=product_id,
                notification_type=notification_type,
                priority=priority,
            )
            if was_present:
                updated += 1
            else:
                created += 1

        self._repository.delete_stale_notifications(sorted(stale_keys))

        return {
            "created": created,
            "updated": updated,
            "deleted": len(stale_keys),
        }

    def _compute_desired_keys(self, today: Optional[date]) -> set:
        """Compute the set of (product_id, notification_type) alerts.

        Args:
            today: Reference date for expiration classification.

        Returns:
            Set of tuples describing every currently applicable alert.
        """
        desired_keys = set()

        for product in self._repository.get_products_with_stock():
            product_id = int(product["id"])
            total_quantity = int(product.get("total_quantity") or 0)
            minimum_stock = int(product.get("minimum_stock") or 0)

            if total_quantity <= 0:
                desired_keys.add(
                    (product_id, Notification.TYPE_OUT_OF_STOCK)
                )
            elif minimum_stock > 0 and total_quantity <= minimum_stock:
                desired_keys.add((product_id, Notification.TYPE_LOW_STOCK))

        for product in self._repository.get_products_with_expiration():
            product_id = int(product["id"])
            expiration_date = product.get("expiration_date")
            if expiration_date is None:
                continue

            status = classify_expiration(
                expiration_date,
                expiring_soon_days=Config.EXPIRING_SOON_DAYS,
                today=today,
            )
            if status == EXPIRATION_STATUS_EXPIRED:
                desired_keys.add((product_id, Notification.TYPE_EXPIRED))
            elif status == EXPIRATION_STATUS_EXPIRING_SOON:
                desired_keys.add((product_id, Notification.TYPE_EXPIRING_SOON))
            elif status == EXPIRATION_STATUS_NORMAL:
                # Situation resolved: the product now expires within a
                # safe window, so any stored expiration alert is stale
                # and will be removed by the stale-key deletion pass.
                continue

        return desired_keys

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_notifications(
        self,
        notification_type: Optional[str] = None,
        priority: Optional[str] = None,
        unread_only: bool = False,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve notifications with optional filters.

        Newest notifications first.

        Args:
            notification_type: Optional filter by notification type.
            priority: Optional filter by priority.
            unread_only: When True, return only unread notifications.
            limit: Optional maximum number of notifications to return.

        Returns:
            List of notification dictionaries.

        Raises:
            ValueError: If an invalid filter value is provided.
        """
        self.sync_notifications()

        if notification_type is not None and notification_type not in VALID_NOTIFICATION_TYPES:
            raise ValueError(
                f"Invalid notification type. Must be one of: "
                f"{', '.join(sorted(VALID_NOTIFICATION_TYPES))}"
            )
        if priority is not None and priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority. Must be one of: "
                f"{', '.join(sorted(VALID_PRIORITIES))}"
            )

        if limit is not None:
            limit = min(max(int(limit), 1), MAX_LIMIT)

        notifications = self._repository.get_all_notifications()

        if notification_type is not None:
            notifications = [
                item for item in notifications
                if item.notification_type == notification_type
            ]
        if priority is not None:
            notifications = [
                item for item in notifications
                if item.priority == priority
            ]
        if unread_only:
            notifications = [item for item in notifications if not item.is_read]

        if limit is not None:
            notifications = notifications[:limit]

        return [item.to_dict() for item in notifications]

    def get_unread_count(self) -> int:
        """Count unread notifications.

        Regenerates alerts from live inventory state before counting so
        the badge always reflects current conditions.

        Returns:
            Number of unread notifications.
        """
        self.sync_notifications()
        return self._repository.get_unread_count()

    def mark_as_read(self, notification_id: int) -> Dict[str, Any]:
        """Mark a single notification as read.

        Args:
            notification_id: ID of the notification to mark read.

        Returns:
            Dictionary describing the updated notification.

        Raises:
            ValueError: If the notification does not exist.
        """
        if not self._repository.mark_as_read(notification_id):
            raise ValueError("Notification not found")
        return {"id": notification_id, "is_read": True}

    def mark_all_as_read(self) -> int:
        """Mark every notification as read.

        Returns:
            Number of notifications updated.
        """
        return self._repository.mark_all_as_read()
