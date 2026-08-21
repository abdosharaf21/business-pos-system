-- Migration 017: Make services.category_id nullable
-- Services no longer require a category to be created.

ALTER TABLE services
  MODIFY COLUMN category_id INT NULL;
