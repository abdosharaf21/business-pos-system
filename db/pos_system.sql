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
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_categories_name (name)
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
    payment_method ENUM('cash', 'card', 'transfer', 'mixed') NOT NULL DEFAULT 'cash',
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
-- Expenses
-- =============================================================================
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    description TEXT DEFAULT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_expenses_user (user_id),
    INDEX idx_expenses_created (created_at),
    CONSTRAINT fk_expenses_user
        FOREIGN KEY (user_id)
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
-- Seed Data: Admin User
-- admin@pos.com / 123456
-- =============================================================================
INSERT INTO users (full_name, email, password_hash, phone, role, status) VALUES
    ('Admin User', 'admin@pos.com', '$2b$12$rowv6gy8.CmyHXxQmdGZiOoMA2JxHJML88kLXghUb78tr/LSLlcwm', '+10000000000', 'admin', 'active');
