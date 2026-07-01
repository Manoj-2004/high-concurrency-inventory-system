# 🚀 High-Concurrency Inventory Management System (V1)

A production-inspired backend system built with **FastAPI**, **PostgreSQL**, and **Redis** to simulate high-concurrency inventory management for e-commerce platforms.

The project demonstrates how Redis atomic operations prevent overselling during flash-sale scenarios while maintaining consistency with PostgreSQL.

---

# 📌 Project Overview

Modern e-commerce platforms such as Amazon, Flipkart, and Shopify face thousands of simultaneous purchase requests during flash sales.

This project implements a scalable backend architecture capable of handling concurrent purchase requests by using:

- Redis for atomic inventory reservation
- PostgreSQL as the source of truth
- JWT Authentication
- Dockerized services
- Configurable synchronous and asynchronous order processing

---

# 🏗 Architecture

```
                    Client
                       │
                       ▼
                 FastAPI API
                       │
        ┌──────────────┴──────────────┐
        │                             │
 Authentication                  Product APIs
        │                             │
        ▼                             ▼
      JWT                    Purchase Service
                                      │
                                      ▼
                          Redis Atomic DECRBY
                                      │
                          Stock Available?
                             │            │
                            Yes          No
                             │            │
                             ▼            ▼
                 Sync / Background Task   400
                             │
                             ▼
                        PostgreSQL
```

---

# ✨ Features

## Authentication

- User Registration
- JWT Authentication
- OAuth2 Password Flow
- Swagger Authorize Integration
- Protected Routes

---

## Product Management

- Create Products
- View Products
- View Individual Product

---

## Purchase System

- Redis Atomic Stock Reservation
- Order Creation
- Order Items
- Automatic Rollback on Failure
- Configurable Purchase Mode

```env
USE_BACKGROUND_TASKS=true
```

or

```env
USE_BACKGROUND_TASKS=false
```

---

## Stress Testing

A custom asyncio + httpx based stress testing script simulates concurrent users purchasing the same product.

Example:

```
Stock = 25

Concurrent Requests = 100

Result

25 Successful Orders
75 Out of Stock
0 Overselling
```

---

# 🛠 Tech Stack

Backend

- FastAPI
- SQLAlchemy
- Pydantic
- Alembic

Database

- PostgreSQL

Caching

- Redis

Authentication

- JWT
- OAuth2

Testing

- httpx
- asyncio

Containerization

- Docker
- Docker Compose

---

# 📂 Project Structure

```
app
│
├── routers
│   ├── auth.py
│   ├── product.py
│   └── purchase.py
│
├── services
│   ├── auth_service.py
│   ├── product_service.py
│   └── purchase_service.py
│
├── models.py
├── schemas.py
├── database.py
├── redis_client.py
├── config.py
└── main.py

tests
└── stress_test.py
```

---

# 🔄 Purchase Flow

```
User

↓

Login

↓

JWT Token

↓

Purchase API

↓

Redis Atomic DECRBY

↓

Stock Available?

↓

Yes

↓

Create Order

↓

Update PostgreSQL

↓

Return Response
```

---

# 🚦 Stress Test Results

Example run:

```
Stock = 25

Concurrent Requests = 100

Successful Orders : 25

Out of Stock : 75

Overselling : 0
```

Redis successfully prevented overselling under concurrent purchase requests.

---

# ⚠ Current Limitation (V1)

The project supports an optional **Background Task** mode.

```
Redis

↓

Response

↓

Background Task

↓

PostgreSQL
```

This improves API response time but **is not durable**.

If the application stops before all background tasks complete, PostgreSQL may become temporarily inconsistent with Redis.

This limitation motivates the V2 architecture.

---

# 🚀 Planned V2

Version 2 replaces FastAPI BackgroundTasks with a durable event-driven architecture.

```
Redis

↓

Kafka

↓

Consumer Workers

↓

PostgreSQL
```

Planned additions:

- Apache Kafka
- Retry Mechanism
- Dead Letter Queue
- Worker Consumers
- Event-driven Processing
- Inventory Recovery
- Inventory API
- Role-Based Authorization (RBAC)
- Refresh Tokens
- WebSockets

---

# 🧠 Concepts Demonstrated

- High-Concurrency Inventory Management
- Redis Atomic Operations
- PostgreSQL Transactions
- JWT Authentication
- OAuth2 Password Flow
- Dependency Injection
- SQLAlchemy ORM
- Service Layer Architecture
- Background Processing
- Dockerized Development
- Stress Testing
- Flash Sale System Design

---

# ▶ Running the Project

Clone

```bash
git clone https://github.com/<your-username>/high-concurrency-inventory-system.git
cd high-concurrency-inventory-system
```

Start services

```bash
docker compose up -d
```

Run FastAPI

```bash
uvicorn app.main:app --reload
```

Swagger

```
http://127.0.0.1:8000/docs
```

Run Stress Test

```bash
python tests/stress_test.py
```

---

# 📈 Future Improvements

- Kafka Event Streaming
- RabbitMQ Alternative
- Kubernetes Deployment
- Prometheus Metrics
- Grafana Dashboard
- Distributed Locking
- Inventory Reconciliation Jobs
- CI/CD Pipeline
- Unit & Integration Tests

---

# 👨‍💻 Author

**Vajrapu Manoj Kalyan**

Built as a backend systems engineering project to explore high-concurrency architecture using FastAPI, Redis, and PostgreSQL.