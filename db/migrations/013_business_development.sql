-- =============================================================================
-- Migration 013: Business Development Module Tables
-- =============================================================================
-- Adds the four Business Development tables (clients, service_categories,
-- services, client_services) used to manage leads/prospects/customers and
-- service offerings. The schema is imported unchanged from the Business
-- Development application's maindb.sql so that existing data can be migrated
-- into the unified pos_system database without loss.
--
-- Safe to run on an existing database. All tables are created only if missing.
-- =============================================================================

-- =============================================================================
-- Clients
-- =============================================================================
CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    email VARCHAR(150) DEFAULT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    address TEXT DEFAULT NULL,
    status ENUM('lead', 'prospect', 'customer') NOT NULL DEFAULT 'lead',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_clients_status (status),
    INDEX idx_clients_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Service Categories
-- =============================================================================
CREATE TABLE IF NOT EXISTS service_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Services
-- =============================================================================
CREATE TABLE IF NOT EXISTS services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT DEFAULT NULL,
    price DECIMAL(10, 2) DEFAULT NULL,
    duration_days INT DEFAULT NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_services_category (category_id),
    INDEX idx_services_status (status),
    CONSTRAINT fk_services_category
        FOREIGN KEY (category_id)
        REFERENCES service_categories (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Client Services (Assignments)
-- =============================================================================
CREATE TABLE IF NOT EXISTS client_services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    service_id INT NOT NULL,
    assigned_by INT DEFAULT NULL,
    start_date DATE DEFAULT NULL,
    end_date DATE DEFAULT NULL,
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cs_client (client_id),
    INDEX idx_cs_service (service_id),
    INDEX idx_cs_assigned_by (assigned_by),
    INDEX idx_cs_status (status),
    CONSTRAINT fk_cs_client
        FOREIGN KEY (client_id)
        REFERENCES clients (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_cs_service
        FOREIGN KEY (service_id)
        REFERENCES services (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_cs_assigned_by
        FOREIGN KEY (assigned_by)
        REFERENCES users (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
