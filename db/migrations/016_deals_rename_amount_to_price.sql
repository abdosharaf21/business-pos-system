-- =============================================================================
-- Migration 016: Rename deals.amount to deals.price
-- =============================================================================
-- Renames the base-amount column to 'price' to align with the Service model's
-- price field and clarify that the value originates from the service catalog.
--
-- Safe to run on an existing database. Uses a column-rename so no data loss.
-- =============================================================================

SET @table_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME   = 'deals'
      AND COLUMN_NAME  = 'amount'
);

SET @sql = IF(
    @table_exists > 0,
    'ALTER TABLE deals RENAME COLUMN amount TO price',
    'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
