-- =============================================================================
-- Migration 012: Refresh Token Blocklist
-- =============================================================================
-- Adds the refresh_token_blocklist table used by the auth module to revoke
-- access and refresh tokens at logout. Tokens are stored by JWT ID (jti)
-- with their expiry so expired rows can be purged periodically.
--
-- Safe to run on an existing database. The table is created only if missing.
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
