-- =============================================================================
-- POS System - Migration 005
-- Inventory Audit (Stock Count) module.
--
-- Adds two tables:
--   * inventory_audits        - an audit header for a physical stock count at
--                               a single location (warehouse or store).
--   * inventory_audit_items   - per-product counted quantities with the
--                               computed difference from the system stock.
--
-- Completing an open audit applies the counted quantities back to the
-- inventory rows and logs a stock_movements row (movement_type 'adjustment')
-- per product whose difference is non-zero, referencing the audit id.
--
-- The migration is fully idempotent: both tables are created only when they
-- do not already exist.
-- =============================================================================

USE pos_system;

-- ---------------------------------------------------------------------------
-- 1. Inventory audits table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inventory_audits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location ENUM('warehouse', 'store') NOT NULL,
    status ENUM('open', 'completed', 'cancelled') NOT NULL DEFAULT 'open',
    created_by INT NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audits_name (name),
    INDEX idx_audits_location (location),
    INDEX idx_audits_status (status),
    INDEX idx_audits_created_by (created_by),
    INDEX idx_audits_created_at (created_at),
    CONSTRAINT fk_audits_user
        FOREIGN KEY (created_by)
        REFERENCES users (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 2. Inventory audit items table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inventory_audit_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    audit_id INT NOT NULL,
    product_id INT NOT NULL,
    system_quantity INT NOT NULL DEFAULT 0,
    counted_quantity INT NULL DEFAULT NULL,
    difference INT NOT NULL DEFAULT 0,
    notes VARCHAR(255) DEFAULT NULL,
    UNIQUE KEY uq_audit_items_audit_product (audit_id, product_id),
    INDEX idx_audit_items_product (product_id),
    CONSTRAINT fk_audit_items_audit
        FOREIGN KEY (audit_id)
        REFERENCES inventory_audits (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_audit_items_product
        FOREIGN KEY (product_id)
        REFERENCES products (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
