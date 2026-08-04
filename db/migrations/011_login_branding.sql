-- =============================================================================
-- Migration 011: Login Page Branding
-- =============================================================================
-- Adds backward-compatible columns to the store_settings table for
-- customizing the login page:
--   * login_background_path — filename of the uploaded login background image
--   * login_logo_path       — filename of the uploaded login logo image
--   * login_title           — welcome title shown on the login page
--   * login_subtitle        — welcome subtitle shown on the login page
--
-- Safe to run on an existing database. Columns are additive only.
-- =============================================================================

ALTER TABLE store_settings
    ADD COLUMN login_background_path VARCHAR(255) NOT NULL DEFAULT '' AFTER logo_path,
    ADD COLUMN login_logo_path VARCHAR(255) NOT NULL DEFAULT '' AFTER login_background_path,
    ADD COLUMN login_title VARCHAR(150) NOT NULL DEFAULT '' AFTER login_logo_path,
    ADD COLUMN login_subtitle VARCHAR(255) NOT NULL DEFAULT '' AFTER login_title;
