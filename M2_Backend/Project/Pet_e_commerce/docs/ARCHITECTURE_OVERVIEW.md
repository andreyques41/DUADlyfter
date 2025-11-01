# Pet E-commerce Backend Architecture Overview

## 🏛️ System Architecture

### Centralized Infrastructure Pattern

Our backend follows a **centralized infrastructure pattern** similar to enterprise frameworks like Spring Boot (Java) or Django (Python). All core services use singleton or request-scoped instances accessed through factory functions.

```
┌─────────────────────────────────────────────────────────────┐
│                     Flask Application                        │
│                      (app/__init__.py)                       │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Logging    │    │   Database   │    │    Cache     │
│   (Global)   │    │  (Request)   │    │ (Singleton)  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
   setup_logging()      get_db()            get_cache()
   get_logger()         close_db()          close_cache()
```

---

## 📦 Module Structure

### Core Infrastructure (`app/core/`)

#### 1. **Logging** (`config/logging.py`)
```python
# Scope: Global (application-wide)
# Pattern: Configuration + Factory

from config.logging import get_logger

logger = get_logger(__name__)
logger.info("Message")
```

**Features:**
- Centralized configuration (level, format, destination)
- Module-specific loggers via `get_logger(__name__)`
- Global `EXC_INFO_LOG_ERRORS` flag for stack traces
- Consistent across all modules

#### 2. **Database** (`app/core/database.py`)
```python
# Scope: Request (new session per request)
# Pattern: Request-scoped via Flask's g object

from app.core.database import get_db

db = get_db()  # Returns session for current request
product = db.query(Product).filter_by(id=1).first()
```

**Features:**
- SQLAlchemy ORM integration
- Request-scoped sessions (automatic cleanup)
- Connection pooling
- Schema management
- Automatic teardown via `close_db()`

#### 3. **Cache** (`app/core/cache_manager.py`)
```python
# Scope: Application (singleton shared across requests)
# Pattern: Singleton via global instance

from app.core.cache_manager import get_cache

cache = get_cache()  # Returns global singleton
cache.store_data("key", "value", ttl=300)
```

**Features:**
- Redis connection pooling
- Singleton pattern (one instance per app)
- Type-safe methods with return types
- Error handling and logging
- Pattern matching for bulk operations

---

## 🎯 Domain Modules

### Module Template Structure

Each domain module (products, auth, sales) follows this structure:

```
module_name/
├── __init__.py
├── controllers/          # HTTP layer (NEW)
│   └── module_controller.py
├── models/              # ORM models
│   └── module_model.py
├── repositories/        # Data access layer
│   └── module_repository.py
├── routes/             # Route definitions
│   └── module_routes.py
├── schemas/            # Validation/serialization
│   └── module_schema.py
└── services/           # Business logic
    └── module_service.py
```

### Layer Responsibilities

#### 1. **Routes Layer** (`routes/`)
```python
# Responsibility: Route registration and decorators only
# NO business logic, NO database access

from flask import Blueprint
from flask.views import MethodView

class ProductAPI(MethodView):
    @admin_required_with_repo
    def post(self):
        from app.products.controllers.product_controller import ProductController
        controller = ProductController()
        return controller.post()
```

**Allowed:**
- Route definitions
- Method-level decorators (@admin_required, etc.)
- Controller instantiation and delegation

**NOT Allowed:**
- Business logic
- Database queries
- Validation logic
- Response formatting (beyond delegation)

#### 2. **Controller Layer** (`controllers/`) 🆕
```python
# Responsibility: HTTP handling and response formatting
# Delegates to service layer for business logic

from flask import jsonify, request, g

class ProductController:
    def __init__(self):
        self.product_service = ProductService()
        self.logger = get_logger(__name__)
        
    def post(self):
        try:
            data = request.get_json()
            validated = self.product_schema.load(data)
            
            # Add request context (g.current_user)
            if hasattr(g, 'current_user'):
                validated['created_by'] = g.current_user.username
            
            # Delegate to service
            product = self.product_service.create_product(**validated)
            
            # Format response
            schema = ProductResponseSchema(...)
            return jsonify(schema.dump(product)), 201
            
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
```

**Allowed:**
- Request parsing (`request.get_json()`)
- Authentication context (`g.current_user`)
- Schema serialization (response formatting)
- HTTP status codes
- Error handling and logging
- Service delegation

**NOT Allowed:**
- Database queries
- Complex business logic
- Direct repository access

#### 3. **Service Layer** (`services/`)
```python
# Responsibility: Business logic and orchestration
# Uses repository for data access

from app.core.cache_manager import get_cache

class ProductService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.cache = get_cache()
        self.logger = get_logger(__name__)
        
    @cache_invalidate([...])
    def create_product(self, **product_data):
        # Business logic: validation, conversions
        category_id = ReferenceData.get_product_category_id(
            product_data.pop('category')
        )
        
        # SKU generation
        if 'sku' not in product_data:
            product_data['sku'] = self._generate_sku()
        
        # Delegate to repository
        product = Product(**product_data)
        return self.product_repo.create(product)
```

**Allowed:**
- Business logic and validation
- Reference data conversions
- Cache management
- Repository delegation
- Transaction orchestration

**NOT Allowed:**
- HTTP request/response handling
- Direct SQL queries (use repository)
- Route definitions

#### 4. **Repository Layer** (`repositories/`)
```python
# Responsibility: Database operations ONLY
# No business logic

from app.core.database import get_db

class ProductRepository:
    def get_by_id(self, product_id: int) -> Optional[Product]:
        try:
            db = get_db()
            return db.query(Product).filter_by(id=product_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            return None
            
    def create(self, product: Product) -> Optional[Product]:
        try:
            db = get_db()
            db.add(product)
            db.flush()  # Don't commit here - let service/controller handle it
            return product
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            return None
```

**Allowed:**
- Database queries (SELECT, INSERT, UPDATE, DELETE)
- SQLAlchemy ORM operations
- Query optimization
- Error handling for DB operations

**NOT Allowed:**
- Business logic
- Validation beyond database constraints
- Cache operations
- HTTP handling

#### 5. **Schema Layer** (`schemas/`)
```python
# Responsibility: Data validation and serialization
# Marshmallow schemas for API contracts

from marshmallow import Schema, fields, validates

class ProductRegistrationSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True)
    
    @validates('category')
    def validate_category(self, value):
        if not ReferenceData.is_valid_product_category(value):
            raise ValidationError(f"Invalid category: {value}")

class ProductResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    category = fields.Method("get_category_name")
    
    def __init__(self, include_admin_data=False, **kwargs):
        super().__init__(**kwargs)
        self.include_admin_data = include_admin_data
    
    @post_dump
    def add_conditional_fields(self, data, original_obj):
        if self.include_admin_data:
            data['admin_data'] = {...}
        return data
```

**Allowed:**
- Field definitions and validation rules
- Custom validators
- Serialization methods
- Pre/post processing hooks
- Role-based field inclusion

**NOT Allowed:**
- Database access
- Business logic beyond validation
- HTTP handling

#### 6. **Model Layer** (`models/`)
```python
# Responsibility: ORM models and database schema
# SQLAlchemy declarative models

from app.core.database import Base, get_schema

class Product(Base):
    __tablename__ = "products"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relationships
    category: Mapped["ProductCategory"] = relationship(back_populates="products")
```

**Allowed:**
- Table/column definitions
- Relationships
- Database constraints
- Schema configuration

**NOT Allowed:**
- Business logic
- Validation beyond DB constraints
- HTTP handling

---

## 🔄 Request Flow

### Example: GET /products/1

```
1. Client Request
   │
   ▼
2. Flask Router
   │
   ▼
3. Route (product_routes.py)
   │  - @admin_required decorator (optional auth)
   ▼
4. Controller (product_controller.py)
   │  - Parse request
   │  - Check authentication (g.current_user)
   ▼
5. Service (product_service.py)
   │  - Check cache (get_cache())
   │  - If miss, call repository
   ▼
6. Repository (product_repository.py)
   │  - Query database (get_db())
   ▼
7. Model (product.py)
   │  - SQLAlchemy ORM object
   ▼
8. Back to Service
   │  - Store in cache
   ▼
9. Back to Controller
   │  - Serialize with schema
   │  - Determine role-based fields
   ▼
10. Response to Client
    - JSON with appropriate fields
```

### Example: POST /products

```
1. Client Request (JSON body)
   │
   ▼
2. Flask Router
   │
   ▼
3. Route (product_routes.py)
   │  - @admin_required decorator (enforces admin)
   ▼
4. Controller (product_controller.py)
   │  - Parse JSON: request.get_json()
   │  - Validate: schema.load(data)
   │  - Add context: validated['created_by'] = g.current_user.username
   ▼
5. Service (product_service.py)
   │  - Business logic: category name → ID conversion
   │  - SKU generation if not provided
   │  - Validate SKU uniqueness
   ▼
6. Repository (product_repository.py)
   │  - Create: db.add(product)
   ▼
7. Database
   │  - INSERT query via SQLAlchemy
   ▼
8. Back to Service
   │  - @cache_invalidate: clear products:all cache
   ▼
9. Back to Controller
   │  - Serialize response with admin data
   ▼
10. Response to Client
    - 201 Created with product JSON
```

---

## 🛡️ Security & Best Practices

### Authentication Flow
```python
# 1. Optional authentication (public endpoints)
def _try_authenticate_user(self):
    token = request.headers.get('Authorization')
    if token:
        user = verify_and_get_user(token)
        if user:
            g.current_user = user

# 2. Required authentication (decorator)
@admin_required_with_repo
def post(self):
    # g.current_user guaranteed to exist here
    # and guaranteed to be admin
```

### Error Handling Hierarchy
```
1. Schema Validation → 400 Bad Request
   ├─ Marshmallow ValidationError
   └─ Custom validators

2. Business Logic → 400 Bad Request
   ├─ Duplicate SKU
   └─ Invalid reference data

3. Not Found → 404 Not Found
   ├─ Product doesn't exist
   └─ User doesn't exist

4. Authorization → 403 Forbidden
   ├─ Non-admin accessing admin endpoint
   └─ User accessing other user's data

5. Server Errors → 500 Internal Server Error
   ├─ Database connection failure
   ├─ Cache connection failure
   └─ Unexpected exceptions
```

---

## 📊 Comparison with Other Frameworks

### Spring Boot (Java) Equivalent
```
Flask Routes         ↔ @RestController
Controllers (NEW)    ↔ Controller methods
Services            ↔ @Service classes
Repositories        ↔ @Repository / JpaRepository
Models              ↔ @Entity classes
Schemas             ↔ DTO classes
get_db()            ↔ @Autowired EntityManager
get_cache()         ↔ @Autowired RedisTemplate
```

### Django (Python) Equivalent
```
Flask Routes        ↔ urls.py
Controllers (NEW)   ↔ ViewSets/APIView
Services           ↔ Service layer (custom)
Repositories       ↔ Models.objects
Models             ↔ Django Models
Schemas            ↔ Serializers
get_db()           ↔ Django ORM (automatic)
get_cache()        ↔ django.core.cache
```

---

## 🎯 Key Architectural Decisions

### Why Controller Layer?
**Before:** Routes had business logic mixed with HTTP handling
**After:** Clean separation between HTTP and business concerns
**Benefit:** Easier testing, better maintainability, clearer responsibilities

### Why Singleton Cache?
**Reason:** Redis connections are stateless and thread-safe
**Benefit:** Reduced connection overhead, shared across requests
**Trade-off:** Less flexible than request-scoped, but more efficient

### Why Request-Scoped Database?
**Reason:** Database sessions are stateful and transaction-bound
**Benefit:** Automatic cleanup, proper transaction boundaries
**Trade-off:** More overhead, but necessary for correctness

### Why Bypass Object Caching?
**Reason:** SQLAlchemy objects have session dependencies and lazy loading
**Alternative:** Cache serialized data (dicts/JSON) instead of objects
**Future:** Implement at controller layer where data is already serialized

---

## 📈 Performance Characteristics

### Database (per request)
- Connection: From pool (fast)
- Session: Created on first `get_db()` call
- Queries: Lazy-loaded via ORM
- Cleanup: Automatic via `close_db()`

### Cache (singleton)
- Connection: Single persistent connection
- Operations: Sub-millisecond for simple gets
- Invalidation: Synchronous (blocking)
- Failure: Graceful degradation

### Logging (global)
- Overhead: Minimal (async I/O in production)
- Format: Centralized configuration
- Levels: Dynamically adjustable
- Destination: Console + optional file

---

## 🚀 Scaling Considerations

### Horizontal Scaling
- ✅ Stateless application (sessions via JWT)
- ✅ Shared cache (Redis)
- ✅ Shared database (PostgreSQL)
- ⚠️ Need load balancer
- ⚠️ Need session affinity for uploads

### Caching Strategy
- **Current:** Simple key-value (Redis)
- **Future:** Distributed cache cluster
- **Monitoring:** Cache hit rate tracking
- **Eviction:** TTL-based policies

### Database Optimization
- **Current:** Connection pooling (10 + 20 overflow)
- **Future:** Read replicas for queries
- **Indexes:** On foreign keys and search fields
- **Partitioning:** By date for orders/invoices

---

This architecture provides a solid foundation for scaling while maintaining code quality and maintainability. Each layer has clear responsibilities, and the centralized infrastructure pattern ensures consistency across all modules.
