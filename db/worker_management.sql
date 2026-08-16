-- =============================================================================
-- Worker Management + Expenses Standalone - Database Schema
-- MySQL 8.0
-- -----------------------------------------------------------------------------
-- Independent, standalone database for the Worker Management + Expenses application.
--
-- Contains:
--   * Authentication: users, refresh_token_blocklist
--   * Application: store_settings
--   * Worker Management: workers, attendance, salaries, advances
--   * Expenses: expense_categories, expenses
-- =============================================================================

CREATE DATABASE IF NOT EXISTS worker_management
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE worker_management;

-- =============================================================================
-- Users (shared auth foundation)
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
-- Store Settings (single shared shell branding row)
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
-- Seed Data: Admin User
-- admin@pos.com / 123456
-- =============================================================================
INSERT INTO users (full_name, email, password_hash, phone, role, status) VALUES
    ('Admin User', 'admin@pos.com', '$2b$12$rowv6gy8.CmyHXxQmdGZiOoMA2JxHJML88kLXghUb78tr/LSLlcwm', '+10000000000', 'admin', 'active');

-- =============================================================================
-- Worker Management Tables
-- =============================================================================

-- Workers
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

-- Attendance
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

-- Salaries
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

-- Advances
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
-- Expenses Tables
-- =============================================================================

-- Expense Categories
CREATE TABLE IF NOT EXISTS expense_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_expense_category_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Expenses
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    expense_date DATE NOT NULL,
    payment_method ENUM('cash', 'card', 'transfer', 'mixed', 'vodafone_cash') NOT NULL DEFAULT 'cash',
    notes VARCHAR(255) DEFAULT NULL,
    created_by INT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_expenses_category (category_id),
    INDEX idx_expenses_date (expense_date),
    INDEX idx_expenses_created_by (created_by),
    CONSTRAINT fk_expenses_category
        FOREIGN KEY (category_id)
        REFERENCES expense_categories (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_expenses_created_by
        FOREIGN KEY (created_by)
        REFERENCES users (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- Seed Data: Admin User
-- admin@pos.com / 123456
-- =============================================================================
INSERT INTO users (full_name, email, password_hash, phone, role, status) VALUES
    ('Admin User', 'admin@pos.com', '$2b$12$rowv6gy8.CmyHXxQmdGZiOoMA2JxHJML88kLXghUb78tr/LSLlcwm', '+10000000000', 'admin', 'active')
ON DUPLICATE KEY UPDATE id = id;

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
    ('Other', 'Other business expenses')
ON DUPLICATE KEY UPDATE id = id;