# Business POS System

A full-stack Point of Sale (POS) and Inventory Management System built with Flask, React, MySQL, and a modular feature-based architecture. Supports bilingual English/Arabic UI with RTL layout and Egyptian Currency (EGP).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, Flask, Flask-CORS, Flask-JWT-Extended, bcrypt, mysql-connector-python |
| **Frontend** | React 19, Vite 8, React Router, Axios, Tailwind CSS, Recharts, Zod, react-hook-form, react-i18next, react-hot-toast |
| **Database** | MySQL 8 |
| **Auth** | JWT (access tokens), bcrypt password hashing, Role-Based Access Control (admin / manager / employee) |

---

## Features

### Modules
- **Authentication** — JWT login/logout with role-based access
- **Dashboard** — KPIs, stats cards, today's activity, inventory health
- **POS (Sales)** — Product search, barcode lookup, category filter, cart management, checkout, invoice generation
- **Products** — Full CRUD with SKU, barcode, category, pricing, stock tracking
- **Categories** — Product categorization
- **Inventory** — Stock overview, low-stock alerts, adjustment history
- **Purchases** — Purchase orders, supplier management, cost tracking
- **Customers** — Customer management with search for POS
- **Suppliers** — Supplier management for purchases
- **Users** — User management with role assignment
- **Reports** — Sales analytics, profit analysis, product/supplier performance, charts

### Localization
- **English** — Full English UI
- **Arabic** — Full Arabic UI with RTL layout
- **Egyptian Currency (EGP)** — All monetary values displayed in ج.م

### Additional
- Invoice printing
- Barcode support
- SKU support
- Responsive design
- Feature-based architecture (model / repository / service / routes)

---

## Project Structure

```
business-pos-system/
├── backend/
│   ├── app.py                  # Flask entry point
│   ├── config.py               # Environment configuration
│   ├── config/                 # Configuration modules
│   ├── database/               # Database connection and config
│   ├── middleware/              # Error handlers, security, CORS, logging
│   ├── modules/
│   │   ├── auth/               # JWT authentication
│   │   ├── users/              # User management
│   │   ├── dashboard/          # Dashboard stats
│   │   ├── categories/         # Product categories
│   │   ├── products/           # Product catalog
│   │   ├── inventory/          # Stock management
│   │   ├── purchases/          # Purchase orders
│   │   ├── customers/          # Customer management
│   │   ├── suppliers/          # Supplier management
│   │   ├── pos/                # Point of Sale
│   │   └── reports/            # Analytics and reports
│   ├── utils/                  # Utility functions
│   ├── tests/                  # Unit tests
│   └── requirements.txt
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

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=pos_system
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### Frontend Setup

```bash
cd frontend
npm install
```

---

## Running the Project

### Backend

```bash
cd backend
python app.py
```

The API server starts at `http://localhost:5001`.

### Frontend

```bash
cd frontend
npm run dev
```

The development server starts at `http://localhost:5174`.

### Production Build

```bash
cd frontend
npm run build
```

Output is written to `frontend/dist/`.

---

## Default Login

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@pos.com | admin123 |

---

## API Endpoints

The backend exposes a RESTful API at `http://localhost:5001/api/`:

| Module | Endpoints |
|--------|-----------|
| Auth | `POST /api/users/login`, `POST /api/users/logout` |
| Users | `GET/POST /api/users`, `GET/PUT/DELETE /api/users/<id>` |
| Dashboard | `GET /api/dashboard/stats` |
| Products | `GET/POST /api/products`, `GET/PUT/DELETE /api/products/<id>` |
| Categories | `GET/POST /api/categories`, `GET/PUT/DELETE /api/categories/<id>` |
| Customers | `GET/POST /api/customers`, `GET/PUT/DELETE /api/customers/<id>` |
| Suppliers | `GET/POST /api/suppliers`, `GET/PUT/DELETE /api/suppliers/<id>` |
| Purchases | `GET/POST /api/purchases`, `GET /api/purchases/<id>`, `GET /api/purchases/<id>/invoice` |
| Inventory | `GET /api/inventory`, `GET /api/inventory/summary`, `POST /api/inventory/adjust` |
| POS | `GET /api/pos/products`, `GET /api/pos/customers`, `POST /api/pos/checkout`, `GET /api/pos/invoice/<id>` |
| Reports | `GET /api/reports/dashboard`, `GET /api/reports/sales-trend`, `GET /api/reports/profit`, `GET /api/reports/products-performance`, `GET /api/reports/suppliers-performance` |

---

## Screenshots

| Module | Preview |
|--------|---------|
| Login | *Screenshot coming soon* |
| Dashboard | *Screenshot coming soon* |
| POS | *Screenshot coming soon* |
| Products | *Screenshot coming soon* |
| Inventory | *Screenshot coming soon* |
| Purchases | *Screenshot coming soon* |
| Reports | *Screenshot coming soon* |

---

## Future Improvements

- Expense tracking
- Sales return / refund
- Purchase return
- Multi-warehouse inventory
- Barcode printing
- Receipt customization
- Offline mode
- Mobile app
- Email notifications
- Audit logs
- Data export (PDF, Excel)

---

## License

This project is for educational and portfolio purposes.

---

## Author

**Abdelrahman Sharaf**

GitHub: [https://github.com/YOUR_USERNAME](https://github.com/YOUR_USERNAME)
