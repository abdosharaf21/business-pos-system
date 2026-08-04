-- =============================================================================
-- Migration 007: Add Vodafone Cash as a supported sales payment method
-- =============================================================================
-- Backward compatible: extends the existing ENUM with a new value; all
-- previously stored values keep working unchanged.
-- =============================================================================

ALTER TABLE sales
    MODIFY COLUMN payment_method ENUM('cash', 'card', 'transfer', 'mixed', 'vodafone_cash')
        NOT NULL DEFAULT 'cash';
