# Pet E-commerce Backend

A professional Flask-based REST API for a pet products e-commerce platform. Built with clean architecture principles, featuring JWT authentication, role-based access control, and comprehensive sales management workflows.

## 🎯 Overview

This backend system provides a complete e-commerce solution for pet products, including:
- **User Management**: Secure registration, login, and profile management with JWT authentication
- **Product Catalog**: Browse and manage pet products with advanced filtering by category, pet type, and price
- **Shopping Experience**: Full cart-to-checkout workflow with order tracking
- **Sales Operations**: Invoicing, payment tracking, and returns processing
- **Admin Controls**: Complete administrative access for managing products, orders, and user accounts

**Key Features**:
- ✅ Clean layered architecture (Routes → Services → Repositories → Models)
- ✅ JWT-based authentication with database role verification
- ✅ Role-based access control (Admin/Customer)
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Input validation with Marshmallow schemas
- ✅ Centralized error handling and logging
- ✅ RESTful API design with 42 endpoints

## 📁 Project Structure

```text
Pet_e_commerce/
├── run.py                  # App entry point
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── blueprints.py       # Blueprint registration
│   ├── core/               # Core utilities, DB, middleware, enums
│   │   ├── database.py     # SQLAlchemy Base, engine, session
│   │   ├── enums.py        # Shared enums (UserRole, OrderStatus, etc.)
│   │   ├── lib/            # Utility libraries (JWT, auth, users)
│   │   └── middleware/     # Auth decorators and middleware
│   ├── auth/               # Authentication module
│   │   ├── models/         # User, Role, RoleUser models (SQLAlchemy ORM)
│   │   ├── schemas/        # User validation schemas (Marshmallow)
│   │   ├── routes/         # Auth endpoints (Flask Blueprint)
│   │   ├── repositories/   # User CRUD operations (data access layer)
│   │   └── services/       # Auth business logic (AuthService, SecurityService)
│   ├── products/           # Products module
│   │   ├── models/         # Product, ProductCategory, PetType models (SQLAlchemy ORM)
│   │   ├── schemas/        # Product validation schemas (Marshmallow)
│   │   ├── routes/         # Product endpoints (Flask Blueprint)
│   │   ├── repositories/   # Product CRUD operations (data access layer)
│   │   └── services/       # Product business logic (ProductService)
│   └── sales/              # Sales module (carts, orders, invoices, returns)
│       ├── models/         # Cart, Order, Invoice, Return models (SQLAlchemy ORM)
│       ├── schemas/        # Sales validation schemas (Marshmallow)
│       ├── routes/         # Sales endpoints (Flask Blueprint)
│       ├── repositories/   # Sales CRUD operations (data access layer)
│       └── services/       # Sales business logic (CartService, OrderService, etc.)
├── config/                 # App config, logging, requirements
│   ├── settings.py         # Database and JWT configuration
│   ├── logging.py          # Centralized logging setup
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables (DB credentials, JWT secret)
├── scripts/                # Utility scripts
│   └── init_db.py          # Database initialization script
├── docs/                   # API usage/reference docs
│   └── USAGE_API_REFERENCE.md
└── tests/                  # Test suite
```

---

## 📖 API Usage

For detailed API endpoints, authentication, and usage examples, see:

**[docs/USAGE_API_REFERENCE.md](docs/USAGE_API_REFERENCE.md)**

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip and virtualenv

### Installation

1. **Clone the repo and navigate to the project folder:**
   ```sh
   git clone <repository-url>
   cd M2_Backend/Project/Pet_e_commerce
   ```

2. **Create and activate a Python virtual environment:**
   ```sh
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r config/requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `config/.env.example` to `config/.env` (if available)
   - Update database credentials and JWT secret in `config/.env`:
     ```env
     DB_USER=postgres
     DB_PASSWORD=your_password
     DB_HOST=localhost
     DB_PORT=5432
     DB_NAME=lyfter
     DB_SCHEMA=lyfter_backend_project
     JWT_SECRET_KEY=your-secret-key
     ```

5. **Initialize the database:**
   ```sh
   python scripts/init_db.py
   ```

6. **Run the app:**
   ```sh
   python run.py
   ```

7. **Access the API at [http://localhost:8000](http://localhost:8000)**

---

## 🏗️ Architecture

### Layered Architecture

The project follows a clean, modular architecture with clear separation of concerns:

#### 1. **Routes Layer** (`routes/`)
- Flask Blueprints for each module
- HTTP endpoint definitions
- Request/response handling
- Input validation using schemas
- Authentication and authorization decorators

#### 2. **Services Layer** (`services/`)
- Business logic and validation
- Orchestrates repository operations
- Complex calculations and transformations
- Access control and permissions

#### 3. **Repositories Layer** (`repositories/`)
- Data access layer (CRUD operations)
- SQLAlchemy ORM queries
- Database transaction management
- Error handling for database operations

#### 4. **Models Layer** (`models/`)
- SQLAlchemy ORM models
- Database table definitions
- Relationships between entities
- Field definitions and constraints

#### 5. **Schemas Layer** (`schemas/`)
- Marshmallow schemas for validation
- Input/output data serialization
- Field-level validation rules
- Custom validators

---

## 🛠️ Features

### Core Functionality
- **Modular, scalable Flask backend** with clean separation of concerns
- **PostgreSQL database** with SQLAlchemy ORM and schema-based organization
- **JWT authentication** with real-time database role verification
- **Role-based access control** - Admin and customer roles with granular permissions
- **Public product browsing** - No authentication required for catalog browsing
- **Admin product management** - Full CRUD operations for authorized admins
- **Complete shopping workflow** - Cart → Order → Invoice → Returns
- **Centralized logging** with configurable log levels
- **Comprehensive error handling** with detailed error responses
- **API documentation** with usage examples and endpoint reference

### Technical Highlights
- **Optimized authentication decorators** - Database role verification on every request
- **Repository pattern** - Clean data access layer with transaction management
- **Service layer** - Business logic separated from routes and data access
- **Schema validation** - Marshmallow schemas for input/output validation
- **Flexible filtering** - Advanced product search by category, type, price, and availability

### Module Breakdown

#### 🔐 Authentication (`app/auth/`)
- **User Management**: Registration, login, profile updates, and account deletion
- **JWT Authentication**: Token generation with configurable expiration (default: 24 hours)
- **Role-Based Access**: Admin and customer roles with database verification
- **Password Security**: Bcrypt hashing with 12-round salt
- **Profile Operations**: Users can view/update their own profiles, admins can manage all users
- **Access Control**: Repository-based decorators verify roles in real-time from database

#### 📦 Products (`app/products/`)
- **Product Catalog**: Complete CRUD operations for pet products
- **Advanced Filtering**: Filter by category (food, toys, accessories), pet type (dog, cat, bird, fish), price range, and stock availability
- **Public Access**: Product browsing requires no authentication
- **Admin Management**: Only admins can create, update, or delete products
- **Stock Tracking**: Real-time inventory management with stock quantity tracking
- **Category Organization**: Normalized categories and pet types for data consistency

#### 💰 Sales (`app/sales/`)
- **Shopping Cart**: 
  - Add/remove items with quantity management
  - Update cart contents
  - Clear entire cart or remove individual items
  - Users can only access their own carts, admins can view all

- **Orders**: 
  - Create orders from cart with automatic inventory checks
  - Track order status: pending → confirmed → processing → shipped → delivered
  - Cancel orders (user access with status validation)
  - Users can view their own orders, admins can manage all orders
  - Order history and detail tracking

- **Invoices**: 
  - Automatic invoice generation linked to orders
  - Payment tracking with status: pending → paid → overdue → refunded
  - Admin-only creation and management
  - Users can view their own invoices

- **Returns**: 
  - Customer return request submission with reason tracking
  - Return status workflow: requested → approved/rejected → processed
  - Refund amount calculation and tracking
  - Admin approval and processing
  - Link returns to original orders and invoices

---

## 🗄️ Database

### Technology
- **PostgreSQL** 12+
- **SQLAlchemy ORM** for database operations
- **Schema-based organization** for multi-tenancy support

### Key Models

#### Authentication
- `User`: User accounts with authentication
- `Role`: User roles (admin, customer)
- `RoleUser`: Many-to-many user-role relationship

#### Products
- `Product`: Product catalog items
- `ProductCategory`: Normalized category reference table
- `PetType`: Normalized pet type reference table

#### Sales
- `Cart`: Shopping cart with items
- `CartItem`: Individual cart items
- `Order`: Customer orders
- `OrderItem`: Order line items
- `Invoice`: Payment and billing records
- `Return`: Return requests and refunds

---

## 🔒 Security

### Authentication & Authorization
- **JWT tokens** for stateless authentication with automatic token verification
- **Database role verification** - User roles are validated against the database on each request (not just from JWT payload)
- **Repository-based decorators** - New `@token_required_with_repo` and `@admin_required_with_repo` decorators provide real-time role checking
- **bcrypt password hashing** for secure password storage (12 rounds)
- **Role-based access control** (RBAC) - Separate admin and customer roles with granular permissions

### Security Features
- **Environment variables** for sensitive configuration (database credentials, JWT secrets)
- **SQL injection protection** via SQLAlchemy ORM parameterized queries
- **Input validation** using Marshmallow schemas with custom validators
- **Request-scoped user context** - Current user and role stored in Flask's `g` object
- **Secure password requirements** - Minimum length, complexity validation

### Decorator Optimization
The project uses optimized authentication decorators that verify user roles from the database in real-time:
- `@token_required_with_repo` - Validates JWT + verifies role in DB, sets `g.current_user` and `g.is_admin`
- `@admin_required_with_repo` - Enforces admin-only access with DB verification

This ensures that role changes (e.g., user promoted to admin) take effect immediately without waiting for token expiration.

---

## 📝 Development

### Code Organization
Each module follows the same structure:
```
module/
├── models/         # SQLAlchemy ORM models
├── schemas/        # Marshmallow validation schemas
├── routes/         # Flask Blueprint routes
├── repositories/   # Data access layer
├── services/       # Business logic layer
└── __init__.py     # Module exports
```

### Adding a New Feature
1. **Define the model** in `models/`
2. **Create validation schemas** in `schemas/`
3. **Implement repository** for data access in `repositories/`
4. **Add business logic** in `services/`
5. **Create routes** in `routes/`
6. **Register blueprint** in module's `__init__.py`

---

## 🧪 Testing

Run tests with pytest:
```sh
pytest tests/
```

---

## 📚 Additional Documentation

- **API Reference**: See `docs/USAGE_API_REFERENCE.md` for endpoint details
- **Database Schema**: See database diagram (if available)
- **Environment Setup**: See `.env.example` for configuration options

---
