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
- ✅ Layered design: Routes → Services → Repositories → Models
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
- Python 3.8+, PostgreSQL 12+, pip/virtualenv

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

# 4. Configure environment (.env)
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lyfter
DB_SCHEMA=lyfter_backend_project
JWT_SECRET_KEY=your-secret-key

# 5. Initialize database
python scripts/init_db.py

# 6. Run application
python run.py
```

Access API at: **http://localhost:8000**

---

## 🏗️ Architecture

**Layered Design** - Clean separation of concerns:

1. **Routes** - HTTP endpoints, request/response handling, input validation
2. **Services** - Business logic, orchestration, access control
3. **Repositories** - Data access (CRUD), ORM queries, transactions
4. **Models** - SQLAlchemy ORM models, table definitions, relationships
5. **Schemas** - Marshmallow validation, serialization, custom validators

**Key Patterns**:
- Repository pattern for clean data access
- Service layer for business rules
- Real-time role verification from database
- Schema-based validation with business logic enforcement

---

## 🛠️ Features

### Core Modules

#### 🔐 Authentication & Users
- JWT tokens (24-hour expiration, bcrypt password hashing)
- Real-time database role verification on every request
- Admin/Customer role-based access control
- User CRUD with profile management and role assignment

#### 📦 Products
- Public catalog browsing (no authentication required)
- Admin-only CRUD operations
- Advanced filtering: category, pet type, price range, stock availability
- Normalized categories and pet types (food, toys, accessories | dog, cat, bird, fish)

#### 💰 Sales Workflows

**Carts**:
- Item management (1-50 per product, 1-100 total items)
- User-scoped access (users see own cart, admins see all)

**Orders**:
- Status workflow: pending → confirmed → processing → shipped → delivered (or cancelled)
- Automatic inventory validation
- No duplicate products (schema-enforced)
- Automatic invoice generation on order creation

**Invoices**:
- Auto-created with 30-day due date
- Status tracking: pending → paid → overdue → refunded
- Amount validation against associated order

**Returns**:
- Customer-initiated requests with required reason
- Admin approval workflow: requested → approved/rejected → processed
- Per-item refund calculation (default: price × quantity)
- Validation ensures returned products belong to the order

---

## 🗄️ Database

**Technology**: PostgreSQL 12+ with SQLAlchemy ORM, schema-based organization

**Models**:
- **Auth**: User, Role, RoleUser (many-to-many)
- **Products**: Product, ProductCategory, PetType (normalized references)
- **Sales**: Cart, CartItem, Order, OrderItem, Invoice, Return, ReturnItem

**Business Rules**:
- Status fields validated against reference tables (orders, invoices, returns)
- No duplicate products in orders (schema-enforced)
- Refund amounts calculated and validated per item
- All state transitions enforced by Marshmallow schemas

---

## 🔒 Security

**Authentication**:
- JWT tokens with 24-hour expiration
- Bcrypt password hashing (12 rounds)
- Database role verification on every request (not just JWT payload)
- Optimized decorators: `@token_required_with_repo`, `@admin_required_with_repo`

**Data Protection**:
- Environment variables for sensitive config
- SQL injection protection via ORM parameterized queries
- Marshmallow schema validation with business rules
- Request-scoped user context (Flask `g` object)

**Access Control**:
- Role-based permissions (Admin/Customer)
- User-scoped resource access (users see own data, admins see all)
- Real-time role changes (effective immediately without token re-issue)

---

## 📝 Development

**Adding a New Feature**:
1. Define model in `models/`
2. Create schema in `schemas/`
3. Implement repository in `repositories/`
4. Add business logic in `services/`
5. Create routes in `routes/`
6. Register blueprint in module's `__init__.py`

---

## 🧪 Testing

**Status**: All 42 endpoints validated and tested ✅

Run tests:
```sh
pytest tests/
python test_sales_endpoints.py  # Comprehensive sales module tests
```

Test coverage includes:
- All CRUD operations for carts, orders, invoices, returns
- Business rule validation and status transitions
- Role-based access control
- Error handling and edge cases

---

## 📚 Additional Resources

- **API Reference**: [docs/API_ROUTES.md](docs/API_ROUTES.md) - Complete endpoint documentation
- **Database Scripts**: `docs/postgres_sql_queries/` - Table creation and sample data
- **Environment Config**: `config/.env.example` - Configuration template

---

**Last Updated**: October 19, 2025  
**Version**: 1.1  
**Status**: Production-ready ✅
