-- =============================================================================
-- Migration 008: Add expiration date to purchase items
-- =============================================================================
-- Adds a backward-compatible column to the purchase_items table:
--   * expiration_date  — optional product expiration date for the batch
--                        (DATE, null allowed). Used to classify products as
--                        Normal / Expiring Soon / Expired.
--
-- Safe to run on an existing database. The column is additive only.
-- =============================================================================

ALTER TABLE purchase_items
    ADD COLUMN expiration_date DATE NULL AFTER subtotal;
