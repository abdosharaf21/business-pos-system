# Business POS System

A full-stack Point of Sale (POS) and Inventory Management System built with Flask, React, MySQL, and a modular feature-based architecture. Supports bilingual English/Arabic UI with RTL layout and Egyptian Currency (EGP).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, Flask, Flask-CORS, Flask-JWT-Extended, bcrypt, mysql-connector-python |
| **Frontend** | React 19, Vite, React Router, Axios, Tailwind CSS, Recharts, Zod, react-hook-form, react-i18next, react-hot-toast |
| **Database** | MySQL 8 |
| **Auth** | JWT (access + refresh tokens), bcrypt password hashing, Role-Based Access Control (admin / manager / employee) |

---

## Features

### Modules
- **Authentication** — JWT login/logout/refresh, role-based access, password change
- **Dashboard** — KPIs, stats cards, today's activity, inventory health
- **POS (Sales)** — Product search, barcode lookup, category filter, cart management, checkout, invoice generation
- **Products** — Full CRUD with SKU, barcode, category, pricing, stock tracking
- **Categories** — Product categorization
- **Inventory** — Stock overview, low-stock alerts, adjustment history, expiration tracking
- **Inventory Audits** — Full stock-count audits with variance tracking
- **Purchases** — Purchase orders, supplier management, cost tracking
- **Customers** — Customer management with search for POS
- **Suppliers** — Supplier management for purchases
- **Expenses** — Expense tracking with categories
- **Users** — User management with role assignment
- **Notifications** — In-app alerts (low stock, expiration, etc.)
- **Store Settings** — Store profile, receipt footer, logo/branding upload
- **Reports** — Sales analytics, profit analysis, product/supplier performance, charts

### Localization
- **English** — Full English UI
- **Arabic** — Full Arabic UI with RTL layout
- **Egyptian Currency (EGP)** — All monetary values displayed in ج.م

### Additional
- Invoice printing
- Barcode scanning support
- SKU support
- Responsive design
- Feature-based architecture (model / repository / service / routes)

---

## Project Structure

```
business-pos-system/
├── backend/
│   ├── app.py                  # Flask application factory
│   ├── wsgi.py                 # WSGI entry point (web deployments)
│   ├── config.py               # Environment configuration
│   ├── database/               # Connection pool, bootstrap, schema reconcile
│   ├── middleware/             # Error handlers, security, CORS, logging, RBAC
│   ├── modules/
│   │   ├── auth/               # JWT authentication
│   │   ├── users/              # User management
│   │   ├── dashboard/          # Dashboard stats
│   │   ├── categories/         # Product categories
│   │   ├── products/           # Product catalog
│   │   ├── inventory/          # Stock management
│   │   ├── inventory_audits/   # Stock-count audits
│   │   ├── purchases/          # Purchase orders
│   │   ├── customers/          # Customer management
│   │   ├── suppliers/          # Supplier management
│   │   ├── expenses/           # Expense tracking
│   │   ├── pos/                # Point of Sale
│   │   ├── reports/            # Analytics and reports
│   │   ├── notifications/      # In-app alerts
│   │   └── store_settings/     # Store profile and branding
│   ├── tests/                  # Unit tests
│   └── utils/                  # Utility functions
├── frontend/
│   ├── src/
│   │   ├── modules/            # Feature pages
│   │   ├── shared/             # Shared components, context, layouts
│   │   ├── router/             # App routes
│   │   ├── locales/            # i18n translation files
│   │   ├── utils/              # Utility functions
│   │   └── tests/              # Unit tests
│   ├── index.html
│   └── package.json
├── db/
│   └── pos_system.sql          # Database schema
├── requirements.txt
└── .env.example
```

---

## Installation

### Prerequisites

- Python 3.12+
- Node.js 20+
- MySQL 8
- npm

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/business-pos-system.git
cd business-pos-system
```

### Backend Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Linux / macOS
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### Database Setup

Create a MySQL database and import the schema:

```sql
CREATE DATABASE pos_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

```bash
mysql -u root -p pos_system < db/pos_system.sql
```

Alternatively, run `python backend/app.py` once — the built-in idempotent
bootstrap creates the database, imports the schema, and seeds the admin
account automatically.

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your database credentials and secrets:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=pos_system
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

Set `FLASK_ENV=production` when deploying; the app then refuses to start
without explicit `SECRET_KEY` / `JWT_SECRET_KEY`.

### Frontend Setup

```bash
cd frontend
npm install
```

---

## Running the Project

### Backend (Development)

```bash
python backend/app.py
```

The API server starts at `http://localhost:5001`.

### Frontend (Development)

```bash
cd frontend
npm run dev
```

The development server starts at `http://localhost:5174` and proxies
`/api` to the backend.

### Production Deployment (WSGI)

Build the frontend:

```bash
cd frontend
npm run build
```

Serve the Flask app with gunicorn (or your WSGI server of choice) from the
repository root:

```bash
backend/.venv/bin/gunicorn --bind 0.0.0.0:5001 backend.wsgi:application
```

`backend/wsgi.py` runs the idempotent database bootstrap (schema reconcile
+ admin seeding) and the Flask app serves the built SPA from
`frontend/dist/` as static files. Put it behind a reverse proxy (nginx /
Caddy) with HTTPS in production.

---

## Default Login

The database bootstrap seeds one admin account:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@pos.com | 123456 |

---

## API Endpoints

The backend exposes a RESTful API under `/api/`:

| Module | Endpoints |
|--------|-----------|
| Auth | `POST /api/auth/login`, `POST /api/auth/logout`, `POST /api/auth/refresh`, `GET /api/auth/me`, `PUT /api/auth/change-password` |
| Users | `GET/POST /api/users`, `GET/PUT/DELETE /api/users/<id>` |
| Dashboard | `GET /api/dashboard/stats` |
| Products | `GET/POST /api/products`, `GET/PUT/DELETE /api/products/<id>` |
| Categories | `GET/POST /api/categories`, `GET/PUT/DELETE /api/categories/<id>` |
| Customers | `GET/POST /api/customers`, `GET/PUT/DELETE /api/customers/<id>` |
| Suppliers | `GET/POST /api/suppliers`, `GET/PUT/DELETE /api/suppliers/<id>` |
| Purchases | `GET/POST /api/purchases`, `GET /api/purchases/<id>`, `GET /api/purchases/<id>/invoice` |
| Inventory | `GET /api/inventory`, `GET /api/inventory/summary`, `POST /api/inventory/adjust`, expiration endpoints |
| Inventory Audits | `GET/POST /api/inventory-audits`, `POST /api/inventory-audits/<id>/complete` |
| Expenses | `GET/POST /api/expenses`, expense categories |
| POS | `GET /api/pos/products`, `GET /api/pos/customers`, `POST /api/pos/checkout`, `GET /api/pos/invoice/<id>` |
| Notifications | `GET /api/notifications`, `POST /api/notifications/read` |
| Store Settings | `GET/PUT /api/store-settings`, logo/branding upload |
| Reports | `GET /api/reports/dashboard`, `GET /api/reports/sales-trend`, `GET /api/reports/profit`, `GET /api/reports/products-performance`, `GET /api/reports/suppliers-performance` |

Every endpoint returns JSON:

```json
{ "success": true, "message": "Success", "data": {} }
```

---

## Testing

### Backend

```bash
backend/.venv/bin/python -m pytest backend/tests -q
```

### Frontend

```bash
cd frontend
npm test
npm run lint
npm run build
```

---

## Security

- Passwords are hashed with bcrypt; never stored in plaintext.
- JWT access + refresh tokens with a server-side refresh blocklist.
- Role-based authorization (admin / manager / employee).
- Every input is validated (Zod on the frontend, validators on the backend).
- All SQL uses parameterized queries.
- Config-driven CORS (explicit origin allow-list) and security headers (CSP, HSTS).
- No stack traces are ever exposed to clients.

---

## Future Improvements

- Sales return / refund
- Purchase return
- Multi-warehouse inventory
- Barcode printing
- Receipt customization
- Offline mode
- Mobile app
- Email notifications
- Data export (PDF, Excel)

---

## License

This project is for educational and portfolio purposes.

---

## Author

**Abdelrahman Sharaf**

GitHub: [https://github.com/YOUR_USERNAME](https://github.com/YOUR_USERNAME)
