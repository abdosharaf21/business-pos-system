-- =============================================================================
-- Migration 015: Worker Management Tables
-- =============================================================================
-- Adds the four Worker Management tables (workers, attendance, salaries,
-- advances) used to manage the workforce inside the main pos_system database.
--
-- Safe to run on an existing database. All tables are created only if missing.
-- Nothing existing is altered or dropped.
-- =============================================================================

-- =============================================================================
-- Workers
-- =============================================================================
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

-- =============================================================================
-- Attendance
-- =============================================================================
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

-- =============================================================================
-- Salaries
-- =============================================================================
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

-- =============================================================================
-- Advances
-- =============================================================================
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
