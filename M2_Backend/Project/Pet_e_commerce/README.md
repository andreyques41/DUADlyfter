# Pet E-commerce Backend

A professional Flask-based REST API for a pet products e-commerce platform with clean architecture, JWT authentication, and comprehensive sales workflows.

## 🎯 Overview

Complete e-commerce solution for pet products with 42 validated REST endpoints:
- **Authentication & Users**: JWT-based auth with role-based access control (Admin/Customer)
- **Products**: Public catalog with advanced filtering (category, pet type, price range)
- **Shopping Cart**: Full cart management with item quantity controls (1-100 items)
- **Orders**: Complete order lifecycle (pending → confirmed → processing → shipped → delivered)
- **Invoices**: Automatic invoice generation with payment tracking
- **Returns**: Customer return requests with admin approval workflow

**Architecture**:
- ✅ Layered design: Routes → Controllers → Services → Repositories → Models
- ✅ PostgreSQL + SQLAlchemy ORM with schema-based organization
- ✅ Real-time database role verification on every request
- ✅ Marshmallow validation with business rule enforcement
- ✅ Centralized error handling and logging

## 📁 Project Structure

```text
Pet_e_commerce/
├── run.py                  # Application entry point
├── app/
│   ├── core/               # Database, enums, middleware, utilities
│   ├── auth/               # Authentication (User, Role models + services)
│   ├── products/           # Product catalog (Product, Category models + services)
│   └── sales/              # Sales workflows (Cart, Order, Invoice, Return + services)
├── config/                 # Settings, logging, environment variables
├── scripts/                # Database initialization scripts
├── docs/                   # API documentation (API_ROUTES.md)
└── tests/                  # Test suite
```

**Module Architecture** (auth, products, sales):
```
module/
├── models/         # SQLAlchemy ORM models
├── schemas/        # Marshmallow validation schemas
├── routes/         # Flask Blueprint endpoints
├── controllers/    # HTTP request/response handling
├── repositories/   # Data access layer (CRUD)
└── services/       # Business logic layer
```

---

## 📖 API Documentation

**Complete API Reference**: [docs/API_ROUTES.md](docs/API_ROUTES.md)

**Endpoint Summary** (42 total):
- **Authentication**: Register, Login (2 endpoints)
- **Users**: List, View, Update, Delete, Role Management (8 endpoints)
- **Products**: CRUD operations with public catalog access (5 endpoints)
- **Carts**: Full cart management with item controls (8 endpoints)
- **Orders**: Order lifecycle management (7 endpoints)
- **Invoices**: Invoice CRUD and status tracking (6 endpoints)
- **Returns**: Return request workflow (6 endpoints)

**Status**: All 42 endpoints validated and tested ✅

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+ (for caching)
- pip/virtualenv

### Setup

```sh
# 1. Navigate to project
cd M2_Backend/Project/Pet_e_commerce

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r config/requirements.txt

# 4. Configure environment
# Copy config/.env.example to config/.env and update with your values:
cp config/.env.example config/.env
# Then edit config/.env with your database credentials and secure JWT secret

JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

FLASK_ENV=development
FLASK_DEBUG=True

# 5. Start Redis server
# Windows: redis-server (if installed via Chocolatey/MSI)
# Linux/Mac: redis-server
# Docker: docker run -d -p 6379:6379 redis:6-alpine

# 6. Initialize database
python scripts/init_db.py

# 7. Run application
python run.py
```

Access API at: **http://localhost:8000**

**Note**: Ensure both PostgreSQL and Redis are running before starting the application.

---

## 🏗️ Architecture

**Layered Design** - Clean separation of concerns:

1. **Routes** - Flask Blueprints, endpoint registration, decorators
2. **Controllers** - HTTP request/response handling, input parsing
3. **Services** - Business logic, orchestration, access control
4. **Repositories** - Data access (CRUD), ORM queries, transactions
5. **Models** - SQLAlchemy ORM models, table definitions, relationships
6. **Schemas** - Marshmallow validation, serialization, custom validators

**Key Patterns**:
- Repository pattern for clean data access
- Service layer for business rules
- Controller layer for HTTP concerns
- Real-time role verification from database
- Schema-based validation with business logic enforcement

---

## 🛠️ Features

### Core Modules

#### 🔐 Authentication & Users
- JWT tokens (24-hour expiration, bcrypt hashing)
- Real-time database role verification
- Admin/Customer role-based access control

#### 📦 Products
- Public catalog browsing
- Admin-only CRUD operations
- Advanced filtering (category, pet type, price, stock)

#### 💰 Sales Workflows
- **Carts**: Item management (1-50 per product, 1-100 total)
- **Orders**: Status workflow with automatic invoice generation
- **Invoices**: Auto-created with 30-day due date, payment tracking
- **Returns**: Customer requests with admin approval workflow

---

## 🗄️ Database

**Technology**: PostgreSQL 12+ with SQLAlchemy ORM

**Models**: User, Role, Product, Category, Cart, Order, Invoice, Return (+ associated items/status tables)

**Business Rules**: No duplicate products in orders, validated status transitions, calculated refund amounts

---

## 🔒 Security

- JWT tokens with 24-hour expiration
- Bcrypt password hashing (12 rounds)
- Real-time database role verification (not just JWT payload)
- SQL injection protection via ORM
- User-scoped resource access

---

## 📝 Development

**Adding a New Feature**:
1. Define model in `models/`
2. Create schema in `schemas/`
3. Implement repository in `repositories/`
4. Add business logic in `services/`
5. Create controller in `controllers/`
6. Define routes in `routes/`
7. Write tests in `tests/`

---

## 🧪 Testing

**Status**: 806 passing tests (100% pass rate) | 76.21% code coverage ✅

```sh
pytest tests/                    # Run all tests
pytest tests/ --cov=app         # With coverage report
```

**Coverage**: All 42 API endpoints, business workflows, security, error handling

---

## 📚 Documentation

### Complete Documentation Suite

| Document | Purpose | Audience |
|----------|---------|----------|
| **[📋 Project Overview](docs/PROJECT_OVERVIEW.md)** | Complete project summary & architecture | All team members |
| **[🚀 API Routes](docs/API_ROUTES.md)** | 42 endpoint reference with examples | Frontend developers |
| **[🏗️ Architecture](docs/ARCHITECTURE_OVERVIEW.md)** | System design, patterns & layers | Backend developers |
| **[⚡ Cache Helper](docs/CACHE_HELPER_USAGE.md)** | Caching implementation guide | Backend developers |
| **[🧪 Testing](docs/TESTING.md)** | Test strategy, coverage & best practices | QA & developers |

### Quick Links

- **Database Scripts**: `docs/postgres_sql_queries/` - Table creation and sample data
- **Environment Config**: `config/.env.example` - Configuration template
- **Test Suite**: 806 passing tests, 76.21% coverage ✅

---

**Last Updated**: January 2025  
**Version**: 1.2  
**Status**: Production-ready ✅
