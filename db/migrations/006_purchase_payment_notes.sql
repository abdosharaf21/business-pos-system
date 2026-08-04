-- =============================================================================
-- 006_purchase_payment_notes.sql
--
-- Adds backward-compatible columns to the purchases table:
--   * payment_method  — payment method used for the purchase
--                       (cash, card, transfer, mixed). Defaults to 'cash' so
--                       existing rows remain valid.
--   * notes           — free-text notes attached to the purchase (optional).
--
-- Safe to run on an existing database. Columns are additive only.
-- =============================================================================

ALTER TABLE purchases
    ADD COLUMN payment_method VARCHAR(20) NOT NULL DEFAULT 'cash' AFTER status,
    ADD COLUMN notes TEXT NULL AFTER payment_method;
