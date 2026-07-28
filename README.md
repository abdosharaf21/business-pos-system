# Business Development Management System

A full-stack Business Development Management System built with **Flask**, **React**, **MySQL**, and a modular feature-based architecture.

This project is designed to manage clients, services, service categories, assignments, and business operations through a modern web interface and a RESTful API.

---

# Features

* User Management
* Client Management
* Service Management
* Service Categories
* Client Service Assignments
* Dashboard
* JWT Authentication (In Progress)
* REST API
* OpenAPI / Swagger Documentation
* Modular Feature-Based Backend
* React + Vite Frontend

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

frontend/
    src/
        api/
        components/
        layouts/
        pages/
        routes/
        context/

db/
    maindb.sql
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/my-web-app.git
cd my-web-app
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
CREATE DATABASE business_development;
```

Import the schema:

```bash
mysql -u root -p business_development < db/maindb.sql
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
http://localhost:5000
```

Swagger (if enabled):

```
http://localhost:5000/docs
```

---

## Frontend

```bash
cd frontend
npm run dev -- --host
```

Frontend:

```
http://localhost:5173
```

---

# API Modules

* Users
* Clients
* Services
* Service Categories
* Client Services
* Dashboard

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

**v1.0 (Development MVP)**

Completed:

* Backend Architecture
* Frontend Architecture
* Database Design
* REST API
* CRUD Structure
* OpenAPI
* Swagger
* LAN Development Support

Planned:

* Complete JWT Authentication
* Dashboard Analytics
* Production Deployment
* Docker Support
* CI/CD Pipeline

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
