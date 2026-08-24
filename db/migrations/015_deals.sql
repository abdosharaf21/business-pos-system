-- =============================================================================
-- Migration 015: Deals / Sales Table
-- =============================================================================
-- Adds the deals table used to track sales transactions between clients
-- and services in the Business Development module.
--
-- Safe to run on an existing database. Table is created only if missing.
-- =============================================================================

CREATE TABLE IF NOT EXISTS deals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    deal_number VARCHAR(50) NOT NULL,
    client_id INT NOT NULL,
    service_id INT NOT NULL,
    package_name VARCHAR(200) DEFAULT NULL,
    sale_date DATE NOT NULL,
    amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    discount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    tax DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    final_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    payment_status ENUM('pending', 'partial', 'paid', 'refunded') NOT NULL DEFAULT 'pending',
    deal_status ENUM('draft', 'confirmed', 'delivered', 'cancelled') NOT NULL DEFAULT 'draft',
    notes TEXT DEFAULT NULL,
    created_by INT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_deals_number (deal_number),
    INDEX idx_deals_client (client_id),
    INDEX idx_deals_service (service_id),
    INDEX idx_deals_sale_date (sale_date),
    INDEX idx_deals_payment_status (payment_status),
    INDEX idx_deals_deal_status (deal_status),
    INDEX idx_deals_created_by (created_by),
    CONSTRAINT fk_deals_client
        FOREIGN KEY (client_id)
        REFERENCES clients (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_deals_service
        FOREIGN KEY (service_id)
        REFERENCES services (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_deals_created_by
        FOREIGN KEY (created_by)
        REFERENCES users (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
