-- =============================================================================
-- POS System - Migration 003
-- Rebuild the expenses table with the full expenses management schema.
--
-- The original expenses table only stored a title, amount and description.
-- This migration replaces it with the production schema that adds a fixed
-- category list, payment method, notes, expense date, created_by and an
-- updated_at timestamp. The old table is dropped; it is not referenced by
-- any other table and contains no application data in a fresh install.
--
-- DROP + CREATE is used because the column set changed substantially.
-- The migration is idempotent: CREATE TABLE IF NOT EXISTS after the drop.
-- =============================================================================

USE pos_system;

DROP TABLE IF EXISTS expenses;

CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    category ENUM('Rent', 'Salaries', 'Electricity', 'Water', 'Internet',
                  'Transportation', 'Maintenance', 'Taxes', 'Purchases',
                  'Marketing', 'Other') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    payment_method ENUM('Cash', 'Bank', 'Visa', 'Other') NOT NULL DEFAULT 'Cash',
    notes TEXT DEFAULT NULL,
    expense_date DATE NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_expenses_date (expense_date),
    INDEX idx_expenses_category (category),
    INDEX idx_expenses_created_by (created_by),
    CONSTRAINT fk_expenses_created_by
        FOREIGN KEY (created_by)
        REFERENCES users (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
