-- =============================================================================
-- Migration 009: Notification Center
-- =============================================================================
-- Adds the notifications table used by the in-app Notification Center.
-- Notifications are generated dynamically from inventory and expiration
-- data and materialized here so read state and deduplication (unique
-- product + type) can be tracked.
--
--   * product_id        — the product the alert refers to
--   * notification_type — low_stock | out_of_stock | expired | expiring_soon
--   * priority          — critical | warning
--   * is_read           — whether the user has seen it
--
-- Safe to run on an existing database. Additive only.
-- =============================================================================

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    notification_type ENUM('low_stock', 'out_of_stock', 'expired', 'expiring_soon') NOT NULL,
    priority ENUM('critical', 'warning') NOT NULL,
    is_read TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_notifications_product_type (product_id, notification_type),
    INDEX idx_notifications_type (notification_type),
    INDEX idx_notifications_priority (priority),
    INDEX idx_notifications_read (is_read),
    CONSTRAINT fk_notifications_product
        FOREIGN KEY (product_id)
        REFERENCES products (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
