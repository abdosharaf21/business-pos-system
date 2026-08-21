-- =============================================================================
-- POS System - Migration 014
-- Warehouses, per-warehouse stock, and stock transfers
--
-- IMPORTANT
-- --------
-- Run this migration once on EXISTING databases to enable the multi-warehouse
-- inventory model. Fresh databases import db/pos_system.sql directly and do
-- not need this file.
--
-- What the application bootstrap (schema reconcile) does automatically on an
-- existing database:
--   * creates the warehouses, transfers, transfer_items tables
--   * adds the warehouse_id columns to inventory, stock_movements, inventory_audits
-- What ONLY this migration does:
--   * seeds the two built-in warehouses (WH-MAIN, STORE)
--   * backfills inventory.warehouse_id from each row's location
--   * swaps the inventory unique key from (product_id, location) to
--     (product_id, warehouse_id) so a product can hold stock in many
--     warehouses (not just one warehouse-location row + one store row)
--
-- The file is idempotent and safe to run more than once.
-- =============================================================================

USE pos_system;

-- ---------------------------------------------------------------------------
-- Helpers guarded by information_schema checks (MySQL has no IF NOT EXISTS
-- for ADD COLUMN / ADD INDEX / DROP INDEX).
-- ---------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_014_add_column_if_missing;
DELIMITER $$
CREATE PROCEDURE sp_014_add_column_if_missing(
    IN p_table VARCHAR(64),
    IN p_column VARCHAR(64),
    IN p_definition TEXT
)
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = p_table
          AND COLUMN_NAME = p_column
    ) THEN
        SET @sql = CONCAT('ALTER TABLE `', p_table, '` ADD COLUMN `', p_column, '` ', p_definition);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_014_add_index_if_missing;
DELIMITER $$
CREATE PROCEDURE sp_014_add_index_if_missing(
    IN p_table VARCHAR(64),
    IN p_index VARCHAR(64),
    IN p_columns VARCHAR(255)
)
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = p_table
          AND INDEX_NAME = p_index
        LIMIT 1
    ) THEN
        SET @sql = CONCAT('ALTER TABLE `', p_table, '` ADD INDEX `', p_index, '` (', p_columns, ')');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_014_drop_index_if_exists;
DELIMITER $$
CREATE PROCEDURE sp_014_drop_index_if_exists(
    IN p_table VARCHAR(64),
    IN p_index VARCHAR(64)
)
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = p_table
          AND INDEX_NAME = p_index
        LIMIT 1
    ) THEN
        SET @sql = CONCAT('ALTER TABLE `', p_table, '` DROP INDEX `', p_index, '`');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$
DELIMITER ;

-- ---------------------------------------------------------------------------
-- 1) warehouses table and seed
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS warehouses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50) NOT NULL,
    address VARCHAR(255) DEFAULT NULL,
    manager_name VARCHAR(150) DEFAULT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_warehouses_code (code),
    INDEX idx_warehouses_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO warehouses (name, code, address, manager_name, phone, status)
VALUES
    ('Main Warehouse', 'WH-MAIN', '', '', '', 'active'),
    ('Store', 'STORE', '', '', '', 'active')
ON DUPLICATE KEY UPDATE id = id;

-- ---------------------------------------------------------------------------
-- 2) warehouse_id columns
-- ---------------------------------------------------------------------------
CALL sp_014_add_column_if_missing('inventory', 'warehouse_id', 'INT DEFAULT NULL');
CALL sp_014_add_column_if_missing('stock_movements', 'warehouse_id', 'INT DEFAULT NULL');
CALL sp_014_add_column_if_missing('inventory_audits', 'warehouse_id', 'INT DEFAULT NULL');

CALL sp_014_add_index_if_missing('inventory', 'idx_inventory_warehouse', 'warehouse_id');
CALL sp_014_add_index_if_missing('stock_movements', 'idx_movements_warehouse', 'warehouse_id');
CALL sp_014_add_index_if_missing('inventory_audits', 'idx_audits_warehouse', 'warehouse_id');

-- ---------------------------------------------------------------------------
-- 3) backfill inventory.warehouse_id from each row's location
-- ---------------------------------------------------------------------------
UPDATE inventory i
LEFT JOIN warehouses w ON w.code = IF(i.location = 'store', 'STORE', 'WH-MAIN')
SET i.warehouse_id = w.id
WHERE i.warehouse_id IS NULL AND w.id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 4) swap inventory unique key to (product_id, warehouse_id)
--
-- Add the new unique key FIRST. InnoDB keeps an index per foreign key; the
-- fk_inventory_product(product_id) constraint currently relies on the old
-- (product_id, location) unique index, so dropping it before the replacement
-- exists fails with error 1553. Adding the new (product_id, warehouse_id)
-- unique key first (product_id is its leading column) satisfies the FK, then
-- the legacy unique key can be dropped safely.
-- ---------------------------------------------------------------------------
SET @has_new_key = (
    SELECT COUNT(*) FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'inventory'
      AND INDEX_NAME = 'uq_inventory_product_warehouse'
    LIMIT 1
);
SET @sql = IF(@has_new_key = 0,
    'ALTER TABLE `inventory` ADD UNIQUE KEY `uq_inventory_product_warehouse` (product_id, warehouse_id)',
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

CALL sp_014_drop_index_if_exists('inventory', 'uq_inventory_product_location');

-- ---------------------------------------------------------------------------
-- 5) transfers + transfer_items tables
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transfers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transfer_number VARCHAR(50) NOT NULL,
    source_warehouse_id INT NOT NULL,
    destination_warehouse_id INT NOT NULL,
    status ENUM('pending', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
    created_by INT NOT NULL,
    completed_by INT DEFAULT NULL,
    completed_at TIMESTAMP NULL DEFAULT NULL,
    notes VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_transfers_number (transfer_number),
    INDEX idx_transfers_source (source_warehouse_id),
    INDEX idx_transfers_destination (destination_warehouse_id),
    INDEX idx_transfers_status (status),
    CONSTRAINT fk_transfers_source
        FOREIGN KEY (source_warehouse_id)
        REFERENCES warehouses (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_transfers_destination
        FOREIGN KEY (destination_warehouse_id)
        REFERENCES warehouses (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_transfers_created_by
        FOREIGN KEY (created_by)
        REFERENCES users (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_transfers_completed_by
        FOREIGN KEY (completed_by)
        REFERENCES users (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS transfer_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transfer_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    UNIQUE KEY uq_transfer_items_transfer_product (transfer_id, product_id),
    INDEX idx_transfer_items_product (product_id),
    CONSTRAINT fk_transfer_items_transfer
        FOREIGN KEY (transfer_id)
        REFERENCES transfers (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_transfer_items_product
        FOREIGN KEY (product_id)
        REFERENCES products (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 6) clean up helper procedures
-- ---------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_014_add_column_if_missing;
DROP PROCEDURE IF EXISTS sp_014_add_index_if_missing;
DROP PROCEDURE IF EXISTS sp_014_drop_index_if_exists;
