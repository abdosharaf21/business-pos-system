# POS System — Project Overview

A complete Point of Sale (POS) System built from scratch using a modular, enterprise-grade architecture. This project is an independent copy derived from the Business Development Management System codebase, preserving the original architecture while building toward POS-specific functionality.

---

## Project Overview

The POS System is designed to manage:

- Products and inventory
- Sales transactions
- Customer relationships
- Supplier orders
- Expenses and reporting
- User roles and permissions

It provides a modern web interface with a RESTful API backend, JWT authentication, and role-based access control.

---

## Architecture

The system follows a strict layered architecture:

```
HTTP Request
    ↓
Routes
    ↓
Services
    ↓
Repositories
    ↓
Models
    ↓
Database
```

Each layer has a single responsibility:

| Layer        | Responsibility                              |
|-------------|---------------------------------------------|
| Routes      | Receive HTTP requests, return JSON responses |
| Services    | Business logic, validation, authorization   |
| Repositories| SQL execution, parameterized queries        |
| Models      | Data objects, to_dict/from_dict             |
| Database    | MySQL connection pool management            |

---

## Technologies

### Backend

| Technology             | Purpose                   |
|------------------------|---------------------------|
| Python 3.12            | Runtime                   |
| Flask                  | Web framework             |
| MySQL 8                | Database                  |
| mysql-connector-python | Database driver           |
| Flask-JWT-Extended     | JWT authentication        |
| bcrypt                 | Password hashing          |
| pytest                 | Testing                   |

### Frontend

| Technology             | Purpose                   |
|------------------------|---------------------------|
| React 19               | UI framework              |
| Vite 8                 | Build tool                |
| React Router 7         | Client-side routing       |
| Axios                  | HTTP client               |
| React Hook Form        | Form management           |
| Zod                    | Validation                |
| TanStack React Query   | Server state management   |
| Tailwind CSS 4         | Styling                   |
| Vitest                 | Unit testing              |

---

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 20+
- MySQL 8+
- npm

### Backend Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials
```

### Database Setup

```bash
# Create the database
mysql -u root -p -e "CREATE DATABASE pos_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Import schema
mysql -u root -p pos_system < db/pos_system.sql
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Running

```bash
# Terminal 1 — Backend
cd backend
python3 app.py

# Terminal 2 — Frontend
cd frontend
npm run dev -- --host
```

---

## Current Inherited Modules

These modules were inherited from the original Business Development Management System. They provide the foundation for user management, authentication, and basic CRUD patterns.

| Module              | Purpose                              |
|---------------------|--------------------------------------|
| Users               | User management, roles, passwords    |
| Auth                | JWT authentication, login, logout    |
| Clients             | Customer/client management           |
| Services            | Service/Product definitions          |
| Service Categories  | Category management                  |
| Client Services     | Assignment management                |
| Dashboard           | Statistics and reporting             |

---

## Future POS Modules

| Module               | Purpose                                   |
|----------------------|-------------------------------------------|
| Products             | Product catalog with barcode support      |
| Customers            | Customer profiles and history             |
| Suppliers            | Supplier management and purchase orders   |
| Sales                | Point of sale transactions and invoices   |
| Sale Items           | Line items for each sale                  |
| Purchases            | Purchase orders from suppliers            |
| Purchase Items       | Line items for each purchase              |
| Expenses             | Operational expense tracking              |
| Inventory            | Stock management and adjustments          |
| Inventory Transactions| Movement history for each product        |
| Reports              | Sales, profit, and inventory reports      |
| Barcode              | Barcode scanning and label generation     |
| Receipts             | Receipt printing and templates            |

---

## Development Roadmap

1. **Phase 1** — Database design, product CRUD, customer management
2. **Phase 2** — Sales transactions, purchase orders
3. **Phase 3** — Inventory tracking, expense management
4. **Phase 4** — Reports, barcode scanning, receipt printing
5. **Phase 5** — Deployment, CI/CD, Docker support
