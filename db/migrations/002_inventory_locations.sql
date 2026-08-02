-- =============================================================================
-- POS System - Migration 002
-- Add multi-location inventory support
--
-- Adds an `inventory` table holding per-product stock for the two
-- fixed locations (warehouse, store) and a `stock_movements` table
-- that logs every movement between and into/out of locations.
--
-- Existing products keep their current stock: it is seeded into the
-- warehouse location (store starts at 0). Rows are created with
-- INSERT IGNORE so the migration is idempotent.
-- =============================================================================

USE pos_system;

-- ---------------------------------------------------------------------------
-- 1) inventory table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    location ENUM('warehouse', 'store') NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_inventory_product_location (product_id, location),
    INDEX idx_inventory_location (location),
    CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_id)
        REFERENCES products (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 2) stock_movements table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stock_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    from_location ENUM('warehouse', 'store') DEFAULT NULL,
    to_location ENUM('warehouse', 'store') DEFAULT NULL,
    quantity INT NOT NULL DEFAULT 0,
    movement_type ENUM('transfer', 'sale', 'purchase', 'return', 'damage', 'adjustment') NOT NULL,
    reference VARCHAR(50) DEFAULT NULL,
    notes VARCHAR(255) DEFAULT NULL,
    user_id INT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_movements_product (product_id),
    INDEX idx_movements_type (movement_type),
    INDEX idx_movements_created (created_at),
    INDEX idx_movements_from (from_location),
    INDEX idx_movements_to (to_location),
    CONSTRAINT fk_movements_product
        FOREIGN KEY (product_id)
        REFERENCES products (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_movements_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 3) Seed existing stock into the warehouse location
--    (store starts empty). INSERT IGNORE keeps this idempotent.
-- ---------------------------------------------------------------------------
INSERT IGNORE INTO inventory (product_id, location, quantity)
SELECT id, 'warehouse', quantity FROM products;

INSERT IGNORE INTO inventory (product_id, location, quantity)
SELECT id, 'store', 0 FROM products;
