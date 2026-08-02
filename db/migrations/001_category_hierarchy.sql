-- =============================================================================
-- POS System - Migration 002
-- Add hierarchical support to categories
--
-- Adds parent_id column, a self-referencing foreign key, and an index.
-- Existing rows become root categories (parent_id = NULL).
--
-- Idempotent: safe to run multiple times; each step is guarded by an
-- information_schema check.
-- =============================================================================

USE pos_system;

SET @db_name = DATABASE();

-- ---------------------------------------------------------------------------
-- 1) Add parent_id column if it does not exist
-- ---------------------------------------------------------------------------
SET @col_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = @db_name
      AND TABLE_NAME = 'categories'
      AND COLUMN_NAME = 'parent_id'
);

SET @sql = IF(
    @col_exists = 0,
    'ALTER TABLE categories ADD COLUMN parent_id INT DEFAULT NULL AFTER id',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------------
-- 2) Add index on parent_id if it does not exist
-- ---------------------------------------------------------------------------
SET @idx_exists = (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = @db_name
      AND TABLE_NAME = 'categories'
      AND INDEX_NAME = 'idx_categories_parent_id'
);

SET @sql = IF(
    @idx_exists = 0,
    'ALTER TABLE categories ADD INDEX idx_categories_parent_id (parent_id)',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------------
-- 3) Add self-referencing foreign key if it does not exist
-- ---------------------------------------------------------------------------
SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.REFERENTIAL_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = @db_name
      AND TABLE_NAME = 'categories'
      AND CONSTRAINT_NAME = 'fk_categories_parent'
);

SET @sql = IF(
    @fk_exists = 0,
    'ALTER TABLE categories ADD CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES categories (id) ON DELETE RESTRICT ON UPDATE CASCADE',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
