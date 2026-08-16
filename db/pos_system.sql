-- =============================================================================
-- POS System - Database Schema
-- MySQL 8.0
-- =============================================================================

CREATE DATABASE IF NOT EXISTS pos_system
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE pos_system;

-- =============================================================================
-- Users
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    role ENUM('admin', 'manager', 'employee') NOT NULL DEFAULT 'employee',
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Categories
-- =============================================================================
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT DEFAULT NULL,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_categories_name (name),
    INDEX idx_categories_parent_id (parent_id),
    CONSTRAINT fk_categories_parent
        FOREIGN KEY (parent_id)
        REFERENCES categories (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Products
-- =============================================================================
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    sku VARCHAR(50) DEFAULT NULL,
    barcode VARCHAR(50) DEFAULT NULL UNIQUE,
    description TEXT DEFAULT NULL,
    purchase_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    selling_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    quantity INT NOT NULL DEFAULT 0,
    minimum_stock INT NOT NULL DEFAULT 0,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_products_category (category_id),
    INDEX idx_products_sku (sku),
    INDEX idx_products_barcode (barcode),
    INDEX idx_products_status (status),
    INDEX idx_products_name (name),
    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id)
        REFERENCES categories (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Customers
-- =============================================================================
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    email VARCHAR(150) DEFAULT NULL UNIQUE,
    address TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customers_name (name),
    INDEX idx_customers_phone (phone),
    INDEX idx_customers_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Suppliers
-- =============================================================================
CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    email VARCHAR(150) DEFAULT NULL UNIQUE,
    address TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_suppliers_name (name),
    INDEX idx_suppliers_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Sales
-- =============================================================================
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT DEFAULT NULL,
    user_id INT NOT NULL,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    discount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    paid_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    payment_method ENUM('cash', 'card', 'transfer', 'mixed', 'vodafone_cash') NOT NULL DEFAULT 'cash',
    status ENUM('pending', 'completed', 'cancelled', 'refunded') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sales_customer (customer_id),
    INDEX idx_sales_user (user_id),
    INDEX idx_sales_invoice (invoice_number),
    INDEX idx_sales_status (status),
    INDEX idx_sales_created (created_at),
    CONSTRAINT fk_sales_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_sales_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Sale Items
-- =============================================================================
CREATE TABLE IF NOT EXISTS sale_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    subtotal DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    INDEX idx_sale_items_sale (sale_id),
    INDEX idx_sale_items_product (product_id),
    CONSTRAINT fk_sale_items_sale
        FOREIGN KEY (sale_id)
        REFERENCES sales (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_sale_items_product
        FOREIGN KEY (product_id)
        REFERENCES products (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Purchases
-- =============================================================================
CREATE TABLE IF NOT EXISTS purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT DEFAULT NULL,
    user_id INT NOT NULL,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    status ENUM('pending', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
    payment_method VARCHAR(20) NOT NULL DEFAULT 'cash',
    notes TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_purchases_supplier (supplier_id),
    INDEX idx_purchases_user (user_id),
    INDEX idx_purchases_invoice (invoice_number),
    INDEX idx_purchases_status (status),
    CONSTRAINT fk_purchases_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES suppliers (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_purchases_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Purchase Items
-- =============================================================================
CREATE TABLE IF NOT EXISTS purchase_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    cost_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    subtotal DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    expiration_date DATE NULL,
    INDEX idx_purchase_items_purchase (purchase_id),
    INDEX idx_purchase_items_product (product_id),
    CONSTRAINT fk_purchase_items_purchase
        FOREIGN KEY (purchase_id)
        REFERENCES purchases (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_purchase_items_product
        FOREIGN KEY (product_id)
        REFERENCES products (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Expense Categories
-- =============================================================================
CREATE TABLE IF NOT EXISTS expense_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_expense_categories_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Expenses
-- =============================================================================
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    payment_method ENUM('Cash', 'Bank', 'Visa', 'Other') NOT NULL DEFAULT 'Cash',
    notes TEXT DEFAULT NULL,
    expense_date DATE NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_expenses_date (expense_date),
    INDEX idx_expenses_category_id (category_id),
    INDEX idx_expenses_created_by (created_by),
    CONSTRAINT fk_expenses_category
        FOREIGN KEY (category_id)
        REFERENCES expense_categories (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_expenses_created_by
        FOREIGN KEY (created_by)
        REFERENCES users (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Inventory Transactions
-- =============================================================================
CREATE TABLE IF NOT EXISTS inventory_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    transaction_type ENUM('purchase', 'sale', 'adjustment', 'return') NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    reference_id INT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_inv_product (product_id),
    INDEX idx_inv_type (transaction_type),
    INDEX idx_inv_created (created_at),
    CONSTRAINT fk_inv_product
        FOREIGN KEY (product_id)
        REFERENCES products (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Warehouses (storage locations including the default store)
-- =============================================================================
CREATE TABLE IF NOT EXISTS warehouses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50) NOT NULL,
    address VARCHAR(255) DEFAULT NULL,
    manager_name VARCHAR(150) DEFAULT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_warehouses_code (code),
    INDEX idx_warehouses_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed the two built-in warehouses. WH-MAIN receives warehouse-location
-- stock; STORE receives store-location stock and is the source for POS sales.
INSERT INTO warehouses (name, code, address, manager_name, phone, status)
VALUES
    ('Main Warehouse', 'WH-MAIN', '', '', '', 'active'),
    ('Store', 'STORE', '', '', '', 'active')
ON DUPLICATE KEY UPDATE id = id;

-- =============================================================================
-- Inventory (multi-location stock)
--
-- Every stock row belongs to exactly one warehouse. The built-in rows are
-- WH-MAIN (location = 'warehouse') and STORE (location = 'store'); custom
-- warehouses created by the user use location = 'warehouse' with their own
-- warehouse_id.
-- =============================================================================
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    location ENUM('warehouse', 'store') NOT NULL,
    warehouse_id INT DEFAULT NULL,
    quantity INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_inventory_product_warehouse (product_id, warehouse_id),
    INDEX idx_inventory_location (location),
    INDEX idx_inventory_warehouse (warehouse_id),
    CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_id)
        REFERENCES products (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_inventory_warehouse
        FOREIGN KEY (warehouse_id)
        REFERENCES warehouses (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Stock Movements (history log)
-- =============================================================================
CREATE TABLE IF NOT EXISTS stock_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    from_location ENUM('warehouse', 'store') DEFAULT NULL,
    to_location ENUM('warehouse', 'store') DEFAULT NULL,
    warehouse_id INT DEFAULT NULL,
    quantity INT NOT NULL DEFAULT 0,
    movement_type ENUM('transfer', 'sale', 'purchase', 'return', 'damage', 'adjustment') NOT NULL,
    reference VARCHAR(50) DEFAULT NULL,
    notes VARCHAR(255) DEFAULT NULL,
    user_id INT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_movements_product (product_id),
    INDEX idx_movements_type (movement_type),
    INDEX idx_movements_created (created_at),
    INDEX idx_movements_from (from_location),
    INDEX idx_movements_to (to_location),
    INDEX idx_movements_warehouse (warehouse_id),
    CONSTRAINT fk_movements_product
        FOREIGN KEY (product_id)
        REFERENCES products (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_movements_warehouse
        FOREIGN KEY (warehouse_id)
        REFERENCES warehouses (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_movements_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Inventory Audits (physical stock counts)
-- =============================================================================
CREATE TABLE IF NOT EXISTS inventory_audits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location ENUM('warehouse', 'store') NOT NULL,
    warehouse_id INT DEFAULT NULL,
    status ENUM('open', 'completed', 'cancelled') NOT NULL DEFAULT 'open',
    created_by INT NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audits_name (name),
    INDEX idx_audits_location (location),
    INDEX idx_audits_status (status),
    INDEX idx_audits_warehouse (warehouse_id),
    INDEX idx_audits_created_by (created_by),
    INDEX idx_audits_created_at (created_at),
    CONSTRAINT fk_audits_warehouse
        FOREIGN KEY (warehouse_id)
        REFERENCES warehouses (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_audits_user
        FOREIGN KEY (created_by)
        REFERENCES users (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Inventory Audit Items (counted quantities per product)
-- =============================================================================
CREATE TABLE IF NOT EXISTS inventory_audit_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    audit_id INT NOT NULL,
    product_id INT NOT NULL,
    system_quantity INT NOT NULL DEFAULT 0,
    counted_quantity INT NULL DEFAULT NULL,
    difference INT NOT NULL DEFAULT 0,
    notes VARCHAR(255) DEFAULT NULL,
    UNIQUE KEY uq_audit_items_audit_product (audit_id, product_id),
    INDEX idx_audit_items_product (product_id),
    CONSTRAINT fk_audit_items_audit
        FOREIGN KEY (audit_id)
        REFERENCES inventory_audits (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_audit_items_product
        FOREIGN KEY (product_id)
        REFERENCES products (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Stock Transfers (warehouse-to-warehouse / warehouse-to-store movements)
-- =============================================================================
CREATE TABLE IF NOT EXISTS transfers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transfer_number VARCHAR(50) NOT NULL,
    source_warehouse_id INT NOT NULL,
    destination_warehouse_id INT NOT NULL,
    status ENUM('pending', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
    created_by INT NOT NULL,
    completed_by INT DEFAULT NULL,
    completed_at TIMESTAMP NULL DEFAULT NULL,
    notes VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_transfers_number (transfer_number),
    INDEX idx_transfers_source (source_warehouse_id),
    INDEX idx_transfers_destination (destination_warehouse_id),
    INDEX idx_transfers_status (status),
    CONSTRAINT fk_transfers_source
        FOREIGN KEY (source_warehouse_id)
        REFERENCES warehouses (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_transfers_destination
        FOREIGN KEY (destination_warehouse_id)
        REFERENCES warehouses (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_transfers_created_by
        FOREIGN KEY (created_by)
        REFERENCES users (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_transfers_completed_by
        FOREIGN KEY (completed_by)
        REFERENCES users (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS transfer_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transfer_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    UNIQUE KEY uq_transfer_items_transfer_product (transfer_id, product_id),
    INDEX idx_transfer_items_product (product_id),
    CONSTRAINT fk_transfer_items_transfer
        FOREIGN KEY (transfer_id)
        REFERENCES transfers (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_transfer_items_product
        FOREIGN KEY (product_id)
        REFERENCES products (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Notifications (in-app Notification Center)
-- =============================================================================
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    notification_type ENUM('low_stock', 'out_of_stock', 'expired', 'expiring_soon') NOT NULL,
    priority ENUM('critical', 'warning') NOT NULL,
    is_read TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_notifications_product_type (product_id, notification_type),
    INDEX idx_notifications_type (notification_type),
    INDEX idx_notifications_priority (priority),
    INDEX idx_notifications_read (is_read),
    CONSTRAINT fk_notifications_product
        FOREIGN KEY (product_id)
        REFERENCES products (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Store Settings (single business configuration row)
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
    login_background_path VARCHAR(255) NOT NULL DEFAULT '',
    login_logo_path VARCHAR(255) NOT NULL DEFAULT '',
    login_title VARCHAR(150) NOT NULL DEFAULT '',
    login_subtitle VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO store_settings (id, store_name, owner_name, phone, email, address, website, tax_number, currency, receipt_footer, logo_path)
VALUES (1, '', '', '', '', '', '', '', 'EGP', '', '')
ON DUPLICATE KEY UPDATE id = id;

-- =============================================================================
-- Refresh Token Blocklist (revoked JWT ids at logout)
-- =============================================================================
CREATE TABLE IF NOT EXISTS refresh_token_blocklist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jti VARCHAR(36) NOT NULL,
    token_type ENUM('access', 'refresh') NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_token_blocklist_jti (jti),
    INDEX idx_token_blocklist_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Business Development: Clients
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
-- Business Development: Service Categories
-- =============================================================================
CREATE TABLE IF NOT EXISTS service_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Business Development: Services
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
-- Business Development: Client Services (Assignments)
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

-- =============================================================================
-- Worker Management
-- -----------------------------------------------------------------------------
-- Integrated into the main pos_system database as one business system with
-- four internal entities: workers, attendance, salaries, advances. All tables
-- are idempotent (CREATE TABLE IF NOT EXISTS) and non-destructive.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Workers
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS workers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL DEFAULT '',
    email VARCHAR(150) DEFAULT NULL,
    job_title VARCHAR(100) DEFAULT NULL,
    department VARCHAR(100) DEFAULT NULL,
    hire_date DATE DEFAULT NULL,
    base_salary DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_workers_name (full_name),
    INDEX idx_workers_status (status),
    INDEX idx_workers_department (department),
    INDEX idx_workers_hire_date (hire_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Attendance
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    worker_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('present', 'absent', 'late', 'half_day', 'leave') NOT NULL DEFAULT 'present',
    check_in TIME DEFAULT NULL,
    check_out TIME DEFAULT NULL,
    notes VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_attendance_worker_date (worker_id, attendance_date),
    INDEX idx_attendance_worker (worker_id),
    INDEX idx_attendance_date (attendance_date),
    INDEX idx_attendance_status (status),
    CONSTRAINT fk_attendance_worker
        FOREIGN KEY (worker_id)
        REFERENCES workers (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Salaries
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS salaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    worker_id INT NOT NULL,
    salary_period VARCHAR(7) NOT NULL,
    base_salary DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    bonuses DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    deductions DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    advances_deduction DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    net_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    payment_status ENUM('paid', 'pending', 'partial') NOT NULL DEFAULT 'pending',
    payment_date DATE DEFAULT NULL,
    notes VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_salaries_worker_period (worker_id, salary_period),
    INDEX idx_salaries_worker (worker_id),
    INDEX idx_salaries_period (salary_period),
    INDEX idx_salaries_status (payment_status),
    CONSTRAINT fk_salaries_worker
        FOREIGN KEY (worker_id)
        REFERENCES workers (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Advances
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS advances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    worker_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    advance_date DATE NOT NULL,
    status ENUM('pending', 'paid', 'settled') NOT NULL DEFAULT 'pending',
    notes VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_advances_worker (worker_id),
    INDEX idx_advances_date (advance_date),
    INDEX idx_advances_status (status),
    CONSTRAINT fk_advances_worker
        FOREIGN KEY (worker_id)
        REFERENCES workers (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Seed Data: Expense Categories
-- =============================================================================
INSERT INTO expense_categories (name, description) VALUES
    ('Rent', 'Payments for business premises'),
    ('Electricity', 'Electricity and utility bills'),
    ('Water', 'Water supply bills'),
    ('Internet', 'Internet and telecommunication bills'),
    ('Transportation', 'Shipping, delivery and travel costs'),
    ('Maintenance', 'Equipment and building maintenance'),
    ('Marketing', 'Advertising and promotional costs'),
    ('Taxes', 'Tax payments and government fees'),
    ('Purchases', 'Operational purchases'),
    ('Salaries', 'Employee wages and salaries'),
    ('Other', 'Other business expenses');

-- =============================================================================
-- Seed Data: Admin User
-- admin@pos.com / 123456
-- =============================================================================
INSERT INTO users (full_name, email, password_hash, phone, role, status) VALUES
    ('Admin User', 'admin@pos.com', '$2b$12$rowv6gy8.CmyHXxQmdGZiOoMA2JxHJML88kLXghUb78tr/LSLlcwm', '+10000000000', 'admin', 'active');
