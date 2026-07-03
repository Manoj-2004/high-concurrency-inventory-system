# 🚀 High Concurrency Inventory System

> A production-inspired backend for an e-commerce inventory management system built with **FastAPI**, **PostgreSQL**, **Redis**, and **Apache Kafka**.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Kafka](https://img.shields.io/badge/Apache-Kafka-black)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

---

## 📖 Overview

This project demonstrates how modern e-commerce platforms handle authentication, shopping carts, inventory synchronization, payments, asynchronous order processing, and role-based administration.

Unlike a traditional CRUD application, this backend incorporates:

- Event-driven architecture using Kafka
- Redis-backed inventory caching
- JWT authentication with refresh tokens
- Redis token blacklisting (logout)
- Role-based access control (RBAC)
- Shopping cart & checkout flow
- Payment lifecycle
- Multi-item order processing
- Dead Letter Queue (DLQ)
- Shipping address snapshotting

The project is designed with scalability and production-style backend practices in mind.

---

# 🏗 Architecture

```
                Client
                   │
                   ▼
             FastAPI Backend
                   │
     ┌─────────────┴──────────────┐
     │                            │
 PostgreSQL                  Redis Cache
     │                            │
     │                            │
     └─────────────┬──────────────┘
                   │
              Kafka Producer
                   │
            purchase-events
                   │
            Kafka Consumer
                   │
        Order Processing Service
```

---

# ✨ Features

## 🔐 Authentication

- User Registration
- User Login
- JWT Access Token
- Refresh Token
- Secure Logout
- Redis Token Blacklisting

---

## 👥 Authorization

Role Based Access Control

### Customer

- Browse Products
- Manage Cart
- Manage Addresses
- Checkout
- View Orders

### Admin

- Product Management
- Inventory Sync
- View All Orders
- Update Order Status

---

## 📦 Product Management

- Create Product
- View Products
- Update Product
- Delete Product

---

## 🛒 Shopping Cart

- Add Product
- Update Quantity
- Remove Product
- Multi-item Checkout

---

## 🏠 Address Management

- Add Address
- Update Address
- Delete Address
- Multiple Addresses
- Default Address Support
- Shipping Address Snapshot

---

## 💳 Payment Workflow

```
Checkout
      │
      ▼
Payment (PENDING)
      │
      ▼
Payment Success
      │
      ▼
Kafka Event
      │
      ▼
Order Creation
```

---

## 📬 Event Driven Order Processing

After successful payment:

- Kafka Producer publishes event
- Kafka Consumer processes order
- Inventory updated
- Cart cleared
- Order created
- Order Items created

---

## 📦 Inventory

### PostgreSQL

Permanent inventory storage

### Redis

High-speed inventory cache

Admin endpoint available to synchronize Redis with PostgreSQL.

---

## ☠ Dead Letter Queue (DLQ)

Invalid purchase events are automatically redirected to a DLQ.

Examples:

- Product not found
- Insufficient stock
- Invalid payload

---

## 📜 Order Management

Customers can

- View Order History
- View Order Details

Admins can

- View All Orders
- Update Order Status

---

# 🛠 Tech Stack

| Category | Technology |
|-----------|------------|
| Backend | FastAPI |
| Language | Python 3.12 |
| Database | PostgreSQL |
| Cache | Redis |
| Messaging | Apache Kafka |
| ORM | SQLAlchemy |
| Migration | Alembic |
| Validation | Pydantic |
| Authentication | JWT |
| Containerization | Docker |

---

# 📂 Project Structure

```
app
│
├── routers
├── services
├── kafka
├── dependencies
├── models
├── schemas
├── database
├── config
├── logging
│
alembic
docker-compose.yml
requirements.txt
```

---

# 🔄 Checkout Flow

```
Login

↓

Add Products

↓

Add Address

↓

Checkout

↓

Payment Created

↓

Payment Success

↓

Kafka Producer

↓

Kafka Consumer

↓

Create Order

↓

Reduce Stock

↓

Clear Cart
```

---

# 🔑 Authentication Flow

```
Register

↓

Login

↓

Access Token

↓

Refresh Token

↓

Logout

↓

Redis Blacklist
```

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/<your-username>/high-concurrency-inventory-system.git

cd high-concurrency-inventory-system
```

---

## Start with Docker

```bash
docker compose up --build
```

---

## Run Alembic

```bash
alembic upgrade head
```

---

## API Documentation

Swagger UI

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

# 📌 Main APIs

Authentication

```
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
```

Products

```
GET /products
POST /products
PUT /products/{id}
DELETE /products/{id}
```

Cart

```
POST /cart
GET /cart
POST /cart/checkout
```

Addresses

```
GET /addresses
POST /addresses
PUT /addresses/{id}
DELETE /addresses/{id}
```

Payments

```
POST /payments/{id}/success
POST /payments/{id}/failed
```

Orders

```
GET /orders
GET /orders/{id}
```

Admin

```
GET /admin/orders
PATCH /admin/orders/{id}/status
```

---

# 📈 Future Improvements

- Stripe / Razorpay Integration
- WebSocket Notifications
- Prometheus Monitoring
- Grafana Dashboards
- GitHub Actions CI/CD
- Kubernetes Deployment
- Distributed Rate Limiting
- Email Notifications

---

# 👨‍💻 Author

**Vajrapu Manoj Kalyan**

B.Tech Computer Science & Engineering

Python Backend Developer

GitHub: https://github.com/<your-github>

LinkedIn: https://linkedin.com/in/<your-linkedin>

---

## ⭐ If you found this project useful, consider giving it a star.