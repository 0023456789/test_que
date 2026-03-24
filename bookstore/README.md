# 📚 Bookstore Microservices System

A production-ready, industry-level Bookstore management system built with **Django REST Framework**, **Microservices Architecture**, **Docker Compose**, and **RabbitMQ** event bus.

---

## 🏗️ Architecture Overview

```
                          ┌─────────────────────────────────────────────────────────────┐
                          │                    CLIENT (Browser / Mobile)                  │
                          └───────────────────────────┬─────────────────────────────────┘
                                                       │ HTTP
                          ┌────────────────────────────▼────────────────────────────────┐
                          │                     API GATEWAY :8000                        │
                          │  • JWT Validation   • Rate Limiting (Redis)                  │
                          │  • Request Logging  • Route → Service mapping                │
                          └──┬──────┬──────┬──────┬──────┬──────┬──────┬───────────────┘
                             │      │      │      │      │      │      │
              ┌──────────────┘      │      │      │      │      │      └──────────────┐
              │                     │      │      │      │      │                     │
     ┌────────▼──────┐   ┌──────────▼┐  ┌─▼──────▼──┐  │  ┌───▼──────┐   ┌─────────▼──────┐
     │  auth-service  │   │  customer  │  │   book    │  │  │  catalog  │   │  recommender   │
     │  :8001         │   │  :8002     │  │   :8006   │  │  │  :8005    │   │  :8012         │
     └────────────────┘   └───────────┘  └───────────┘  │  └───────────┘   └────────────────┘
              │                │               │         │        │
       ┌──────▼──┐     ┌───────▼──┐    ┌───────▼──┐     │  ┌─────▼──────┐  ┌──────────────┐
       │   JWT   │     │   cart   │    │  staff   │     │  │  comment   │  │   manager    │
       │  issuer │     │  :8007   │    │  :8003   │     │  │  :8011     │  │  :8004       │
       └─────────┘     └──────────┘    └──────────┘     │  └────────────┘  └──────────────┘
                              │                          │
                       ┌──────▼───────────────────────┐ │
                       │          order-service :8008  │◄┘
                       │   ┌──────────────────────┐    │
                       │   │  SAGA ORCHESTRATOR   │    │
                       │   │  1. Create Order     │    │
                       │   │  2. Reserve Payment  │────┼──► pay-service :8010
                       │   │  3. Reserve Shipping │────┼──► ship-service :8009
                       │   │  4. Confirm Order    │    │
                       │   │  ↕ Compensations     │    │
                       │   └──────────────────────┘    │
                       └───────────────────────────────┘
                                      │
                         ┌────────────▼──────────────┐
                         │       RabbitMQ Event Bus   │
                         │  bookstore.events exchange │
                         └────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Docker ≥ 24.0
- Docker Compose ≥ 2.20

### Start Everything
```bash
# Clone and enter the project
cd bookstore/

# Build and start all 12 services + infrastructure
docker compose up --build

# In a second terminal, verify all services are healthy
curl http://localhost:8000/gateway/health/
```

The API Gateway is your single entry point on **http://localhost:8000**.

---

## 🔌 Services & Ports

| Service              | Port  | Description                          |
|----------------------|-------|--------------------------------------|
| **api-gateway**      | 8000  | Reverse proxy, JWT auth, rate limit  |
| auth-service         | 8001  | JWT issuance, RBAC, user management  |
| customer-service     | 8002  | Customer profiles & addresses        |
| staff-service        | 8003  | Staff CRUD, inventory management     |
| manager-service      | 8004  | Manager dashboard, analytics         |
| catalog-service      | 8005  | Browse, search, filter books         |
| book-service         | 8006  | Book/Author/Category CRUD, inventory |
| cart-service         | 8007  | Shopping cart management             |
| order-service        | 8008  | Order placement + Saga orchestration |
| ship-service         | 8009  | Shipment lifecycle management        |
| pay-service          | 8010  | Payment reservation & confirmation   |
| comment-rate-service | 8011  | Ratings & comments                   |
| recommender-ai       | 8012  | AI-driven recommendations            |
| **RabbitMQ UI**      | 15672 | Management console (guest/guest)     |

---

## 📡 API Reference

### Authentication

```bash
# Register a new customer
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","username":"alice","first_name":"Alice",
       "last_name":"Smith","password":"Secret123","password_confirm":"Secret123","role":"customer"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Secret123"}'
# → returns { "access": "<JWT>", "refresh": "<JWT>" }

# Use the token
export TOKEN="<access token from login>"
```

### Customer Flow

```bash
# Create customer profile (auto-creates cart)
curl -X POST http://localhost:8000/api/customers/create/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":"<uuid>","email":"alice@example.com","first_name":"Alice","last_name":"Smith"}'

# Browse catalog
curl "http://localhost:8000/api/catalog/?sort=rating&page=1"

# Search books
curl "http://localhost:8000/api/catalog/?q=python&category=programming"

# Add to cart
curl -X POST "http://localhost:8000/api/cart/<customer_id>/add/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"book_id":"<uuid>","quantity":2}'

# Checkout → triggers Saga
curl -X POST http://localhost:8000/api/orders/create/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cart_id": "<uuid>",
    "shipping_address": {
      "street": "123 Main St", "city": "Springfield",
      "state": "IL", "postal_code": "62701", "country": "US"
    }
  }'

# Poll order status
curl "http://localhost:8000/api/orders/<order_id>/status/" \
  -H "Authorization: Bearer $TOKEN"
```

### Staff Flow

```bash
# Register staff user (role: staff)
curl -X POST http://localhost:8000/api/auth/register/ \
  -d '{"email":"bob@store.com","role":"staff",...}'

# Create a book
curl -X POST http://localhost:8000/api/books/ \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Clean Code","isbn":"9780132350884",
    "price":"39.99","stock_quantity":100,
    "author_ids":["<uuid>"],"category":"<uuid>"
  }'

# Adjust inventory
curl -X POST http://localhost:8000/api/staff/books/<book_id>/inventory/ \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{"operation":"add","quantity":50,"note":"Restock delivery"}'
```

### Reviews & Recommendations

```bash
# Rate a book (1–5)
curl -X POST "http://localhost:8000/api/reviews/books/<book_id>/ratings/" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"score":5}'

# Comment on a book
curl -X POST "http://localhost:8000/api/reviews/books/<book_id>/comments/" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"body":"Excellent book! Highly recommended."}'

# Get personalised recommendations
curl http://localhost:8000/api/recommendations/for-me/ \
  -H "Authorization: Bearer $TOKEN"

# Trending books
curl http://localhost:8000/api/recommendations/trending/

# Similar books
curl http://localhost:8000/api/recommendations/similar/<book_id>/
```

---

## ⚙️ Saga Orchestration Pattern

The order checkout uses the **Saga Orchestration** pattern for distributed transactions:

```
order-service (Orchestrator)
        │
        ├─ Step 1: Create Order  (status: PENDING)
        │
        ├─ Step 2: POST /api/payments/reserve/
        │          ↳ success → status: PAYMENT_RESERVED
        │          ↳ failure → FAIL (no compensation needed)
        │
        ├─ Step 3: POST /api/shipping/reserve/
        │          ↳ success → status: SHIPPING_RESERVED
        │          ↳ failure → compensate: cancel payment → FAIL
        │
        └─ Step 4: Confirm both services
                   ↳ success → status: COMPLETED
                   ↳ failure → compensate: cancel shipping + cancel payment → FAIL
```

Each step is logged in the `SagaLog` table for full audit trail.
Poll `GET /api/orders/<id>/status/` to track progress asynchronously.

---

## 📨 Event Bus (RabbitMQ)

Exchange: `bookstore.events` (topic)

| Routing Key                  | Producer            | Consumers                        |
|------------------------------|---------------------|----------------------------------|
| `customer.registered`        | customer-service    | cart-service                     |
| `order.created`              | order-service       | recommender, catalog             |
| `order.completed`            | order-service       | recommender, comment-rate        |
| `book.created`               | book-service        | catalog-service                  |
| `book.inventory.updated`     | book-service        | catalog-service                  |
| `payment.confirmed`          | pay-service         | order-service                    |
| `shipping.confirmed`         | ship-service        | order-service                    |

Access RabbitMQ Management UI: http://localhost:15672 (guest/guest)

---

## 🔐 RBAC Roles

| Role       | Access                                                  |
|------------|---------------------------------------------------------|
| `customer` | Browse, cart, orders, reviews, recommendations         |
| `staff`    | All customer access + book CRUD + inventory management  |
| `manager`  | All staff access + staff management + analytics         |
| `admin`    | Full access to all services                             |

---

## 🏥 Health Checks

```bash
# Gateway aggregated health (all 12 services)
curl http://localhost:8000/gateway/health/

# Individual service
curl http://localhost:8001/health/   # auth
curl http://localhost:8006/health/   # books
# etc.
```

---

## 🗄️ Database Architecture

Each service owns its **independent PostgreSQL database** — no shared schemas:

| Service     | Database         | Key Tables                         |
|-------------|------------------|------------------------------------|
| auth        | auth_db          | auth_users                         |
| customer    | customer_db      | customers, customer_addresses      |
| book        | book_db          | books, authors, categories         |
| cart        | cart_db          | carts, cart_items                  |
| order       | order_db         | orders, order_items, saga_logs     |
| pay         | pay_db           | payments                           |
| ship        | ship_db          | shipments, shipment_items          |
| comment     | comment_db       | comments, ratings                  |
| recommender | recommender_db   | recommendations, book_similarities |

---

## 🛠️ Development

```bash
# Rebuild a single service
docker compose up --build book-service

# View logs
docker compose logs -f order-service

# Access a service shell
docker compose exec book-service bash

# Run migrations manually
docker compose exec order-service python manage.py migrate

# Scale a service
docker compose up --scale book-service=3
```

---

## 📁 Project Structure

```
bookstore/
├── docker-compose.yml          # Full orchestration (12 services + infra)
├── shared/
│   ├── event_bus.py            # RabbitMQ publish/consume helpers
│   ├── jwt_auth.py             # Shared JWT validation middleware
│   └── entrypoint.sh           # Common service entrypoint
├── api-gateway/                # Routing, JWT, rate limiting
├── auth-service/               # JWT issuance + user management
├── customer-service/           # Customer profiles
├── staff-service/              # Staff + inventory
├── manager-service/            # Manager dashboard
├── catalog-service/            # Browse + search proxy
├── book-service/               # Book/Author/Category CRUD
├── cart-service/               # Shopping cart
├── order-service/              # Orders + Saga orchestrator
├── pay-service/                # Payment lifecycle
├── ship-service/               # Shipment lifecycle
├── comment-rate-service/       # Ratings & comments
└── recommender-ai-service/     # AI recommendations
```
