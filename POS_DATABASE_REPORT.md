# POS Database Report

## Database Name

**pos_system**

A MySQL 8.0 database designed for a full-featured Point of Sale system.

---

## Tables Created

| # | Table                    | Description                              |
|---|--------------------------|------------------------------------------|
| 1 | `users`                  | System users with roles and authentication |
| 2 | `categories`             | Product categories                       |
| 3 | `products`               | Product catalog with pricing and stock   |
| 4 | `customers`              | Customer profiles                        |
| 5 | `suppliers`              | Supplier information                     |
| 6 | `sales`                  | Sales transactions and invoices          |
| 7 | `sale_items`             | Line items for each sale                 |
| 8 | `purchases`              | Purchase orders from suppliers           |
| 9 | `purchase_items`         | Line items for each purchase             |
| 10 | `expenses`               | Operational expense tracking             |
| 11 | `inventory_transactions` | Inventory movement history               |

### Table Details

#### users
| Column        | Type              | Constraints          |
|---------------|-------------------|----------------------|
| id            | INT               | PK, AUTO_INCREMENT   |
| full_name     | VARCHAR(100)      | NOT NULL             |
| email         | VARCHAR(150)      | NOT NULL, UNIQUE     |
| password_hash | VARCHAR(255)      | NOT NULL             |
| phone         | VARCHAR(20)       | DEFAULT NULL         |
| role          | ENUM              | admin/manager/employee |
| status        | ENUM              | active/inactive      |
| created_at    | TIMESTAMP         | DEFAULT NOW()        |
| updated_at    | TIMESTAMP         | ON UPDATE NOW()      |

#### categories
| Column      | Type              | Constraints          |
|-------------|-------------------|----------------------|
| id          | INT               | PK, AUTO_INCREMENT   |
| name        | VARCHAR(100)      | NOT NULL, UNIQUE     |
| description | TEXT              | DEFAULT NULL         |
| created_at  | TIMESTAMP         | DEFAULT NOW()        |
| updated_at  | TIMESTAMP         | ON UPDATE NOW()      |

#### products
| Column         | Type              | Constraints          |
|----------------|-------------------|----------------------|
| id             | INT               | PK, AUTO_INCREMENT   |
| category_id    | INT               | FK → categories.id   |
| name           | VARCHAR(150)      | NOT NULL             |
| barcode        | VARCHAR(50)       | UNIQUE, DEFAULT NULL |
| description    | TEXT              | DEFAULT NULL         |
| purchase_price | DECIMAL(10,2)     | DEFAULT 0.00         |
| selling_price  | DECIMAL(10,2)     | DEFAULT 0.00         |
| quantity       | INT               | DEFAULT 0            |
| minimum_stock  | INT               | DEFAULT 0            |
| status         | ENUM              | active/inactive      |
| created_at     | TIMESTAMP         | DEFAULT NOW()        |
| updated_at     | TIMESTAMP         | ON UPDATE NOW()      |

#### customers
| Column     | Type              | Constraints          |
|------------|-------------------|----------------------|
| id         | INT               | PK, AUTO_INCREMENT   |
| name       | VARCHAR(100)      | NOT NULL             |
| phone      | VARCHAR(20)       | DEFAULT NULL         |
| email      | VARCHAR(150)      | UNIQUE, DEFAULT NULL |
| address    | TEXT              | DEFAULT NULL         |
| created_at | TIMESTAMP         | DEFAULT NOW()        |
| updated_at | TIMESTAMP         | ON UPDATE NOW()      |

#### suppliers
| Column     | Type              | Constraints          |
|------------|-------------------|----------------------|
| id         | INT               | PK, AUTO_INCREMENT   |
| name       | VARCHAR(150)      | NOT NULL             |
| phone      | VARCHAR(20)       | DEFAULT NULL         |
| email      | VARCHAR(150)      | UNIQUE, DEFAULT NULL |
| address    | TEXT              | DEFAULT NULL         |
| created_at | TIMESTAMP         | DEFAULT NOW()        |
| updated_at | TIMESTAMP         | ON UPDATE NOW()      |

#### sales
| Column         | Type              | Constraints          |
|----------------|-------------------|----------------------|
| id             | INT               | PK, AUTO_INCREMENT   |
| customer_id    | INT               | FK → customers.id    |
| user_id        | INT               | FK → users.id        |
| invoice_number | VARCHAR(50)       | NOT NULL, UNIQUE     |
| total_amount   | DECIMAL(12,2)     | DEFAULT 0.00         |
| discount       | DECIMAL(12,2)     | DEFAULT 0.00         |
| paid_amount    | DECIMAL(12,2)     | DEFAULT 0.00         |
| payment_method | ENUM              | cash/card/transfer/mixed |
| status         | ENUM              | pending/completed/cancelled/refunded |
| created_at     | TIMESTAMP         | DEFAULT NOW()        |

#### sale_items
| Column     | Type              | Constraints          |
|------------|-------------------|----------------------|
| id         | INT               | PK, AUTO_INCREMENT   |
| sale_id    | INT               | FK → sales.id        |
| product_id | INT               | FK → products.id     |
| quantity   | INT               | DEFAULT 1            |
| unit_price | DECIMAL(10,2)     | DEFAULT 0.00         |
| subtotal   | DECIMAL(12,2)     | DEFAULT 0.00         |

#### purchases
| Column         | Type              | Constraints          |
|----------------|-------------------|----------------------|
| id             | INT               | PK, AUTO_INCREMENT   |
| supplier_id    | INT               | FK → suppliers.id    |
| user_id        | INT               | FK → users.id        |
| invoice_number | VARCHAR(50)       | NOT NULL, UNIQUE     |
| total_amount   | DECIMAL(12,2)     | DEFAULT 0.00         |
| status         | ENUM              | pending/completed/cancelled |
| created_at     | TIMESTAMP         | DEFAULT NOW()        |

#### purchase_items
| Column      | Type              | Constraints          |
|-------------|-------------------|----------------------|
| id          | INT               | PK, AUTO_INCREMENT   |
| purchase_id | INT               | FK → purchases.id    |
| product_id  | INT               | FK → products.id     |
| quantity    | INT               | DEFAULT 1            |
| cost_price  | DECIMAL(10,2)     | DEFAULT 0.00         |
| subtotal    | DECIMAL(12,2)     | DEFAULT 0.00         |

#### expenses
| Column      | Type              | Constraints          |
|-------------|-------------------|----------------------|
| id          | INT               | PK, AUTO_INCREMENT   |
| title       | VARCHAR(200)      | NOT NULL             |
| amount      | DECIMAL(10,2)     | DEFAULT 0.00         |
| description | TEXT              | DEFAULT NULL         |
| user_id     | INT               | FK → users.id        |
| created_at  | TIMESTAMP         | DEFAULT NOW()        |

#### inventory_transactions
| Column           | Type              | Constraints          |
|------------------|-------------------|----------------------|
| id               | INT               | PK, AUTO_INCREMENT   |
| product_id       | INT               | FK → products.id     |
| transaction_type | ENUM              | purchase/sale/adjustment/return |
| quantity         | INT               | DEFAULT 0            |
| reference_id     | INT               | DEFAULT NULL         |
| created_at       | TIMESTAMP         | DEFAULT NOW()        |

---

## Relationships

```
categories
    └── products (1:N) — RESTRICT on delete, CASCADE on update

products
    └── sale_items (1:N) — RESTRICT on delete, CASCADE on update
    └── purchase_items (1:N) — RESTRICT on delete, CASCADE on update
    └── inventory_transactions (1:N) — CASCADE on delete, CASCADE on update

customers
    └── sales (1:N) — SET NULL on delete, CASCADE on update

suppliers
    └── purchases (1:N) — SET NULL on delete, CASCADE on update

users
    └── sales (1:N) — RESTRICT on delete, CASCADE on update
    └── purchases (1:N) — RESTRICT on delete, CASCADE on update
    └── expenses (1:N) — RESTRICT on delete, CASCADE on update

sales
    └── sale_items (1:N) — CASCADE on delete, CASCADE on update

purchases
    └── purchase_items (1:N) — CASCADE on delete, CASCADE on update
```

---

## Indexes

| Table                    | Indexes                                                  |
|--------------------------|----------------------------------------------------------|
| users                    | email (unique), role, status                             |
| categories               | name (unique)                                             |
| products                 | category_id, barcode (unique), status, name              |
| customers                | name, phone, email (unique)                              |
| suppliers                | name, phone                                              |
| sales                    | customer_id, user_id, invoice_number (unique), status, created_at |
| sale_items               | sale_id, product_id                                      |
| purchases                | supplier_id, user_id, invoice_number (unique), status    |
| purchase_items           | purchase_id, product_id                                  |
| expenses                 | user_id, created_at                                      |
| inventory_transactions   | product_id, transaction_type, created_at                 |

---

## Security Considerations

1. **Password Hashing** — Passwords are stored as bcrypt hashes (`$2b$12$`). Never plaintext.
2. **Parameterized Queries** — All SQL uses parameterized queries (enforced by repository layer). No SQL concatenation.
3. **JWT Authentication** — API access is secured via JWT tokens with access + refresh token pattern.
4. **RBAC** — Three roles (admin, manager, employee) with different permission levels.
5. **Input Validation** — All inputs validated at the service layer before reaching the database.
6. **Connection Pooling** — Database connections are pooled and recycled, preventing connection leaks.
7. **Foreign Keys** — Referential integrity is enforced at the database level.
8. **ON DELETE RESTRICT** — Critical data (products, users) cannot be deleted while referenced.
9. **ON DELETE SET NULL** — Optional relations (customer on sale, supplier on purchase) nullify on delete.
10. **ON DELETE CASCADE** — Child records (sale_items, purchase_items) are removed with parent.

---

## Setup Instructions

### Prerequisites

- MySQL 8.0+
- Access to a MySQL client (mysql CLI, MySQL Workbench, etc.)

### Installation

```bash
# Create and import the database
mysql -u root -p < db/pos_system.sql
```

This single command creates the `pos_system` database and all 11 tables with their relationships, indexes, and seed data.

### Verify Installation

```bash
mysql -u root -p -e "USE pos_system; SHOW TABLES;"
```

Expected output:

```
+----------------------+
| Tables_in_pos_system |
+----------------------+
| categories           |
| customers            |
| expenses             |
| inventory_transactions |
| products             |
| purchase_items       |
| purchases            |
| sale_items           |
| sales                |
| suppliers            |
| users                |
+----------------------+
```

### Backend Configuration

Update `.env` with:

```env
DB_NAME=pos_system
DB_POOL_NAME=pos_pool
```

### Default Admin Credentials

| Field    | Value          |
|----------|----------------|
| Email    | admin@pos.com  |
| Password | 123456         |

⚠ Change the default password immediately after first login.

---

## Verification

| Question                           | Answer |
|------------------------------------|--------|
| Database can be created            | **YES** |
| All tables exist                   | **YES** (11 tables) |
| Foreign keys work                  | **YES** (11 foreign keys across 7 tables) |
| Backend connection config ready    | **YES** (DB_NAME and DB_POOL_NAME updated in .env.example) |
| Old database affected              | **NO** |
| Architecture changed               | **NO** |
| Ready for POS development          | **YES** |
