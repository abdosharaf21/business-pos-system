-- =============================================================================
-- Migration 010: Store Settings
-- Single-row settings table for business information used across the app
-- (invoices, receipts, and future reports).
-- =============================================================================

CREATE TABLE IF NOT EXISTS store_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    store_name VARCHAR(150) NOT NULL DEFAULT '',
    owner_name VARCHAR(150) NOT NULL DEFAULT '',
    phone VARCHAR(20) NOT NULL DEFAULT '',
    email VARCHAR(150) NOT NULL DEFAULT '',
    address VARCHAR(255) NOT NULL DEFAULT '',
    website VARCHAR(150) NOT NULL DEFAULT '',
    tax_number VARCHAR(50) NOT NULL DEFAULT '',
    currency VARCHAR(10) NOT NULL DEFAULT 'EGP',
    receipt_footer VARCHAR(500) NOT NULL DEFAULT '',
    logo_path VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO store_settings (id, store_name, owner_name, phone, email, address, website, tax_number, currency, receipt_footer, logo_path)
VALUES (1, '', '', '', '', '', '', '', 'EGP', '', '')
ON DUPLICATE KEY UPDATE id = id;
