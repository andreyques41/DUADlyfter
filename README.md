# Pet E-commerce Backend

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
- **Modular, scalable Flask backend** for e-commerce
- **PostgreSQL database** with SQLAlchemy ORM
- **JWT authentication** and role-based access control
- **Public product browsing**, admin product management
- **Shopping cart**, order, billing, and returns workflows
- **Centralized logging** and error handling
- **Comprehensive API documentation**

### Module Breakdown

#### 🔐 Authentication (`app/auth/`)
- User registration and login
- JWT token generation and validation
- Role-based access control (admin/customer)
- Password hashing with bcrypt
- User profile management

#### 📦 Products (`app/products/`)
- Product catalog management
- Category and pet type organization
- Stock tracking and availability
- Advanced filtering and search
- Public browsing (no auth required)
- Admin-only product management

#### 💰 Sales (`app/sales/`)
- **Shopping Cart**: Add/remove items, update quantities
- **Orders**: Create orders from cart, track status
- **Invoices**: Payment tracking and billing
- **Returns**: Return requests and refund processing

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

- **JWT tokens** for stateless authentication
- **bcrypt password hashing** for secure password storage
- **Role-based access control** (RBAC)
- **Environment variables** for sensitive configuration
- **SQL injection protection** via SQLAlchemy ORM
- **Input validation** using Marshmallow schemas

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

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

---

## 📄 License

[Specify your license here]
