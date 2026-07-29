# AGENTS.md

# Business POS System

This document defines the architecture, coding standards, folder structure, and development rules for the entire backend project.

Every generated file must follow these rules.

---

# Tech Stack

Backend
- Python 3.12
- Flask
- MySQL 8
- mysql-connector-python
- JWT Authentication
- bcrypt
- REST API

Frontend
- React
- Vite

Version Control
- Git
- GitHub

---

# Architecture

Always use this architecture:

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

Never skip layers.

Routes never access Database.

Services never execute SQL.

Models never contain business logic.

Repositories never contain business logic.

---

# Folder Structure

backend/

    app.py

    config/

    database/

    modules/

        auth/

            model.py
            repository.py
            service.py
            routes.py

        users/

            model.py
            repository.py
            service.py
            routes.py

        dashboard/

            repository.py
            service.py
            routes.py

        categories/

            model.py
            repository.py
            service.py
            routes.py

        products/

            model.py
            repository.py
            service.py
            routes.py

        customers/

            model.py
            repository.py
            service.py
            routes.py

        suppliers/

            model.py
            repository.py
            service.py
            routes.py

        purchases/

            model.py
            repository.py
            service.py
            routes.py

        inventory/

            model.py
            repository.py
            service.py
            routes.py

        pos/

            model.py
            repository.py
            service.py
            routes.py

        reports/

            repository.py
            service.py
            routes.py

    utils/

    middleware/

---

# Naming Rules

Classes

PascalCase

Example

User

Client

Service

Variables

snake_case

Functions

snake_case

Files

snake_case

Database

snake_case

---

# Models

Models only represent database tables.

Allowed:

constructor

properties

to_dict()

from_dict()

__str__()

__repr__()

type hints

docstrings

Not Allowed

SQL

Flask

Authentication

JWT

Validation

Business Logic

Password hashing

API calls

---

# Repository Rules

Repository is the only layer allowed to access MySQL.

Allowed

SELECT

INSERT

UPDATE

DELETE

Transactions

Cursor execution

Connection handling

Parameterized queries

Not Allowed

Authentication

JWT

Business Logic

Password hashing

Validation

HTTP responses

Routes

---

# Service Rules

Service contains all business logic.

Examples

Login

Register

Validation

Authorization

Permissions

Password hashing

JWT generation

JWT verification

Business rules

Workflow

Calling repositories

Not Allowed

Raw SQL

Flask request

Flask response

Cursor execution

---

# Route Rules

Routes only receive requests.

Allowed

Read request

Call service

Return JSON

HTTP Status Codes

Blueprint

Not Allowed

Business logic

SQL

Hash passwords

JWT logic

Complex calculations

---

# Database Rules

Always use parameterized queries.

Never concatenate SQL strings.

Use transactions when needed.

Commit only after successful execution.

Rollback on errors.

Always close cursor.

Always close connection.

---

# Security Rules

Hash passwords using bcrypt.

Never store plaintext passwords.

Use JWT Authentication.

Validate every input.

Use parameterized SQL.

Never expose stack traces to clients.

Never trust frontend data.

---

# API Rules

Every endpoint returns JSON.

Success Example

{
    "success": true,
    "message": "Success",
    "data": {}
}

Error Example

{
    "success": false,
    "message": "Invalid credentials"
}

---

# Error Handling

Never ignore exceptions.

Catch expected exceptions.

Return meaningful messages.

Log internal errors.

---

# Code Style

PEP8

Type hints

Docstrings

Small functions

Single Responsibility Principle

Readable names

No duplicated code

Maximum readability

---

# Documentation

Every class must have a docstring.

Every method must have a docstring.

Explain parameters.

Explain return value.

---

# Comments

Only comment when necessary.

Avoid obvious comments.

Prefer readable code.

---

# Authentication

JWT

Access Token

Refresh Token later

bcrypt password hashing

Role Based Authorization

Admin

Manager

Employee

---

# Completed Modules

- Auth (JWT login/logout)
- Dashboard (KPIs and stats)
- Products (CRUD with SKU/barcode)
- Categories (product categorization)
- Customers (management with search)
- Suppliers (management for purchases)
- Purchases (orders with cost tracking)
- Inventory (stock + adjustments + history)
- POS (sales with cart/checkout/invoice)
- Users (role-based management)
- Reports (sales, profit, performance)

# Future Modules

- Projects
- Invoices
- Payments
- Notifications
- Analytics
- Settings

---

# AI Instructions

Whenever creating code:

Follow the architecture.

Generate production-ready code.

Use OOP.

Use clean architecture.

Do not mix responsibilities.

Keep every class focused on one responsibility.

Never generate placeholder code.

Never generate TODO comments.

Always generate complete implementations.

When unsure, choose the cleanest architecture.

Code quality should be similar to enterprise software.
