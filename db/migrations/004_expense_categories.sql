-- =============================================================================
-- POS System - Migration 004
-- Normalize expenses to use a dedicated expense_categories table.
--
-- Migration 003 created expenses with a fixed ENUM category column. This
-- migration introduces the expense_categories lookup table (seeded with the
-- 11 default categories) and replaces the ENUM column with a category_id
-- foreign key.
--
-- The migration is fully idempotent:
--   * expense_categories is created only if it does not exist.
--   * Seed rows use INSERT IGNORE so duplicates are skipped.
--   * The category_id column, index and FK are added only when missing.
--   * The legacy category column and its index are dropped only when present.
-- =============================================================================

USE pos_system;

-- ---------------------------------------------------------------------------
-- 1. Expense categories table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expense_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_expense_categories_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 2. Seed the 11 default categories (skips existing rows)
-- ---------------------------------------------------------------------------
INSERT IGNORE INTO expense_categories (name, description) VALUES
    ('Rent', 'Payments for business premises'),
    ('Electricity', 'Electricity and utility bills'),
    ('Water', 'Water supply bills'),
    ('Internet', 'Internet and telecommunication bills'),
    ('Transportation', 'Shipping, delivery and travel costs'),
    ('Maintenance', 'Equipment and building maintenance'),
    ('Marketing', 'Advertising and promotional costs'),
    ('Taxes', 'Tax payments and government fees'),
    ('Purchases', 'Operational purchases'),
    ('Salaries', 'Employee wages and salaries'),
    ('Other', 'Other business expenses');

-- ---------------------------------------------------------------------------
-- 3. Add category_id column when missing
-- ---------------------------------------------------------------------------
SET @has_category_id := (
    SELECT COUNT(*) FROM information_schema.columns
    WHERE table_schema = 'pos_system'
      AND table_name = 'expenses'
      AND column_name = 'category_id'
);

SET @sql := IF(
    @has_category_id = 0,
    'ALTER TABLE expenses ADD COLUMN category_id INT NULL AFTER title',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------------
-- 4. Backfill category_id from the legacy ENUM category column
-- ---------------------------------------------------------------------------
SET @has_category_col := (
    SELECT COUNT(*) FROM information_schema.columns
    WHERE table_schema = 'pos_system'
      AND table_name = 'expenses'
      AND column_name = 'category'
);

SET @sql := IF(
    @has_category_col > 0,
    'UPDATE expenses e JOIN expense_categories ec ON ec.name = e.category SET e.category_id = ec.id',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------------
-- 5. Make category_id NOT NULL once backfilled
-- ---------------------------------------------------------------------------
SET @sql := IF(
    @has_category_id = 0,
    'ALTER TABLE expenses MODIFY category_id INT NOT NULL',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------------
-- 6. Drop the legacy category column and its index when present
-- ---------------------------------------------------------------------------
SET @has_legacy_index := (
    SELECT COUNT(*) FROM information_schema.statistics
    WHERE table_schema = 'pos_system'
      AND table_name = 'expenses'
      AND index_name = 'idx_expenses_category'
);

SET @sql := IF(
    @has_legacy_index > 0,
    'ALTER TABLE expenses DROP INDEX idx_expenses_category',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql := IF(
    @has_category_col > 0,
    'ALTER TABLE expenses DROP COLUMN category',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------------
-- 7. Add category_id index and foreign key when missing
-- ---------------------------------------------------------------------------
SET @has_category_index := (
    SELECT COUNT(*) FROM information_schema.statistics
    WHERE table_schema = 'pos_system'
      AND table_name = 'expenses'
      AND index_name = 'idx_expenses_category_id'
);

SET @sql := IF(
    @has_category_index = 0,
    'ALTER TABLE expenses ADD INDEX idx_expenses_category_id (category_id)',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @has_category_fk := (
    SELECT COUNT(*) FROM information_schema.table_constraints
    WHERE constraint_schema = 'pos_system'
      AND table_name = 'expenses'
      AND constraint_name = 'fk_expenses_category'
      AND constraint_type = 'FOREIGN KEY'
);

SET @sql := IF(
    @has_category_fk = 0,
    'ALTER TABLE expenses ADD CONSTRAINT fk_expenses_category '
    'FOREIGN KEY (category_id) REFERENCES expense_categories (id) '
    'ON DELETE RESTRICT ON UPDATE CASCADE',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
