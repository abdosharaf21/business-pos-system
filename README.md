# POS System

A full-stack Point of Sale System built with **Flask**, **React**, **MySQL**, and a modular feature-based architecture.

This project was initialized from the Business Development Management System codebase and is being developed as an independent POS application.

---

# Tech Stack

## Backend

* Python 3
* Flask
* MySQL
* Flask-CORS
* bcrypt
* JWT
* OpenAPI

## Frontend

* React
* Vite
* React Router
* Axios

## Database

* MySQL

---

# Project Structure

```
backend/
    modules/
        users/
        clients/
        services/
        service_categories/
        client_services/
        dashboard/
        auth/

frontend/
    src/
        modules/
        shared/
        router/
        tests/

db/
    pos_system.sql
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/business-pos-system.git
cd business-pos-system
```

---

## Backend

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

Linux / macOS

```bash
source .venv/bin/activate
```

Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Database

Create a MySQL database:

```sql
CREATE DATABASE pos_system;
```

Import the schema:

```bash
mysql -u root -p pos_system < db/pos_system.sql
```

---

## Environment Variables

Copy:

```bash
cp .env.example .env
```

Configure the database credentials inside `.env`.

---

## Frontend

```bash
cd frontend
npm install
```

---

# Running the Project

## Backend

```bash
cd backend
python3 app.py
```

Backend:

```
http://localhost:5001
```

Swagger (if enabled):

```
http://localhost:5001/docs
```

---

## Frontend

```bash
cd frontend
npm run dev -- --host
```

Frontend:

```
http://localhost:5174
```

---

# Architecture

Backend follows a **Feature-Based Architecture**.

Each module contains:

```
model.py
repository.py
service.py
routes.py
validator.py
```

This keeps every feature isolated and easy to maintain.

---

# Development Status

Current Version:

**v1.0 (Initial POS Base)**

Completed:

* Backend Architecture (inherited)
* Frontend Architecture (inherited)
* Database Design
* REST API
* CRUD Structure
* JWT Authentication
* RBAC
* OpenAPI / Swagger

Planned POS Modules:

* Product Management
* Customer Management
* Supplier Management
* Sales Management
* Purchase Management
* Expense Tracking
* Inventory Management
* Reports & Analytics
* Barcode Scanning
* Receipt Printing

---

# License

This project is for educational and portfolio purposes.

---

# Author

**Abdelrahman Sharaf**

GitHub:

```
https://github.com/YOUR_USERNAME
```
