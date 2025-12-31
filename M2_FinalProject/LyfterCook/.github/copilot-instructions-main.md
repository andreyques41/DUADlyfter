# Main Agent Instructions - LyfterCook

## Your Role
You are the **Main Development Agent** for LyfterCook. You handle feature implementation, bug fixes, architecture decisions, and production code changes. You coordinate with specialized agents (Testing, Database, Security, Documentation, Frontend).

## Project Overview

**LyfterCook** is a platform connecting chefs with clients for custom catering services.

**Current Status (Dec 31, 2025):**
- **Backend**: Flask REST API, 10 modules, 60+ endpoints
- **Database**: PostgreSQL with 3 schemas (auth, core, integrations)
- **Tests**: 296 tests (161 unit + 135 integration), 75% coverage
- **Status**: Production-ready backend, all modules validated

---

## Tech Stack

### Backend
- **Framework**: Flask 3.0+ with application factory pattern
- **Database**: PostgreSQL 16 with SQLAlchemy 2.0 (declarative models)
- **Cache**: Redis 7 with custom CacheHelper and cache_route decorator
- **Auth**: JWT (Flask-JWT-Extended) with role-based access control
- **Validation**: Marshmallow schemas with @validate_json decorator
- **Testing**: pytest (unit + real HTTP integration tests)

### Infrastructure
- **Docker**: Postgres (5433) + Redis (6380) for integration tests
- **Local Dev**: Postgres (5432) + Redis (6379)

### Key Libraries
```python
Flask==3.0.0
SQLAlchemy==2.0.23
marshmallow==3.20.1
Flask-JWT-Extended==4.6.0
redis==5.0.1
pytest==7.4.3
requests==2.31.0
beautifulsoup4==4.12.2  # Optional, for scrapers module
```

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py              # Application factory (create_app)
│   ├── blueprints.py            # Blueprint registration
│   ├── core/
│   │   ├── database.py          # db, Base, init_db
│   │   ├── cache_manager.py     # CacheHelper, cache_route decorator
│   │   ├── middleware/          # CORS, error handlers
│   │   └── lib/                 # Utilities (jwt_helpers, validators)
│   ├── auth/                    # User authentication module
│   ├── admin/                   # Admin + audit logging module
│   ├── chefs/                   # Chef profiles module
│   ├── clients/                 # Client profiles module
│   ├── dishes/                  # Dish catalog module
│   ├── menus/                   # Menu management module
│   ├── appointments/            # Appointment scheduling module
│   ├── quotations/              # Quote requests module
│   ├── public/                  # Public API (no auth) module
│   ├── scrapers/                # Price scraping module (optional)
│   └── scraper/                 # ⚠️ LEGACY - removed (was unused)
├── scripts/
│   ├── init_db.py               # Initialize all schemas and tables
│   ├── seed_admin.py            # Create default admin user
│   └── run_tests.py             # Test runner wrapper
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── unit/                    # 161 unit tests (fast, mocked)
│   ├── integration/             # 135 integration tests (real HTTP)
│   └── TESTING_GUIDE.md         # Testing documentation
├── migrations/
│   └── check_all_models.py      # Model registration validator
├── config.py                    # Environment configurations
├── run.py                       # Development server entry point
├── docker-compose.yml           # Docker infrastructure
└── requirements.txt             # Python dependencies
```

---

## Architecture Patterns

### 1. Module Structure (Layered Architecture)

Every module follows this structure:

```
module_name/
├── __init__.py                  # Empty or module-level exports
├── models/
│   ├── __init__.py              # Export all models
│   └── resource_model.py        # SQLAlchemy models
├── schemas/
│   ├── __init__.py              # Export all schemas
│   └── resource_schema.py       # Marshmallow schemas
├── repositories/
│   ├── __init__.py
│   └── resource_repository.py   # Data access layer (DB queries)
├── services/
│   ├── __init__.py
│   └── resource_service.py      # Business logic layer
├── controllers/
│   ├── __init__.py
│   └── resource_controller.py   # Request/response handling
└── routes/
    ├── __init__.py
    └── resource_routes.py       # Blueprint + route definitions
```

### 2. Request Flow

```
Client Request
    ↓
Route (@blueprint.route)
    ↓
Controller (@validate_json, @jwt_required)
    ↓
Service (business logic)
    ↓
Repository (database access)
    ↓
Model (SQLAlchemy ORM)
    ↓
PostgreSQL
```

### 3. Response Pattern

All endpoints return consistent JSON envelopes:

```python
# Success (200, 201)
{
    "data": {...},           # Single object or list
    "message": "Success"     # Optional
}

# Error (400, 404, 500)
{
    "error": "Error message",
    "details": {...}         # Optional validation details
}
```

### 4. Database Schemas

PostgreSQL uses 3 schemas for logical separation:

- **`auth`**: Users, roles, sessions
  - `auth.users` (id, username, email, password_hash, role, created_at)

- **`core`**: Business entities
  - `core.chefs` (user_id, specialties, experience_years, ...)
  - `core.clients` (user_id, preferences, ...)
  - `core.dishes` (chef_id, name, category, price, ...)
  - `core.menus` (chef_id, name, description, ...)
  - `core.menu_dishes` (menu_id, dish_id, quantity)
  - `core.appointments` (client_id, chef_id, date, status, ...)
  - `core.quotations` (client_id, event_date, status, ...)
  - `core.admin_audit_logs` (admin_id, action, resource_type, ...)

- **`integrations`**: External services
  - `integrations.price_sources` (name, base_url, active, ...)
  - `integrations.scraped_prices` (source_id, product_name, price, ...)

### 5. Authentication & Authorization

```python
# Public endpoints (no auth)
@blueprint.route('/public/chefs', methods=['GET'])
def list_chefs():
    pass

# Protected endpoints (JWT required)
from flask_jwt_extended import jwt_required, get_jwt_identity

@blueprint.route('/dishes', methods=['POST'])
@jwt_required()
def create_dish():
    user_id = get_jwt_identity()
    pass

# Role-based access (admin only)
from app.core.lib.jwt_helpers import role_required

@blueprint.route('/admin/users', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_users():
    pass
```

**Roles**: `chef`, `client`, `admin`

### 6. Validation Pattern

```python
from app.core.lib.validators import validate_json
from app.module.schemas import ResourceSchema

@blueprint.route('/resource', methods=['POST'])
@jwt_required()
@validate_json(ResourceSchema())
def create_resource():
    """
    @validate_json automatically:
    - Validates request JSON against schema
    - Returns 400 with validation errors if invalid
    - Makes validated data available in g.validated_data
    """
    data = g.validated_data
    # ... use validated data
```

### 7. Caching Pattern

```python
# Service-level caching
from app.core.cache_manager import CacheHelper

class DishService:
    def __init__(self, repository, cache_helper=None):
        self.repository = repository
        self.cache = cache_helper or CacheHelper()
    
    def get_dish(self, dish_id):
        return self._get_dish_cached(dish_id)
    
    def _get_dish_cached(self, dish_id):
        cache_key = f"dish:{dish_id}"
        
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        dish = self.repository.get_by_id(dish_id)
        if dish:
            self.cache.set(cache_key, dish, ttl=300)
        return dish

# Route-level caching
from app.core.cache_manager import cache_route

@blueprint.route('/dishes', methods=['GET'])
@cache_route(key_prefix='dishes_list', ttl=300)
def list_dishes():
    """Responses are cached by Redis automatically."""
    pass
```

**Cache Keys Standard**: `resource:id` or `resource_list:filter:value`

### 8. Error Handling

```python
# Custom exceptions in services
class ResourceNotFoundError(Exception):
    pass

# Controllers catch and format
from app.core.lib.error_responses import not_found_response, error_response

try:
    result = service.get_resource(id)
    if not result:
        return not_found_response("Resource")
except Exception as e:
    return error_response(str(e), 500)
```

---

## Database Conventions

### Model Pattern

```python
from app.core.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

class StatusEnum(enum.Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'

class Appointment(Base):
    __tablename__ = 'appointments'
    __table_args__ = {'schema': 'core'}
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('auth.users.id'), nullable=False)
    chef_id = Column(Integer, ForeignKey('auth.users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.PENDING)
    
    # Relationships
    client = relationship('User', foreign_keys=[client_id])
    chef = relationship('User', foreign_keys=[chef_id])
    
    def to_dict(self):
        """Serialization method."""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'chef_id': self.chef_id,
            'date': self.date.isoformat(),
            'status': self.status.value
        }
```

**Rules**:
- All tables must specify `__table_args__ = {'schema': 'auth|core|integrations'}`
- Use `to_dict()` for basic serialization, schemas for validation/deserialization
- Foreign keys reference `schema.table.column`
- Enums are Python enums, not raw strings

### Repository Pattern

```python
class ResourceRepository:
    def __init__(self, db_session):
        self.db = db_session
    
    def get_by_id(self, resource_id):
        return self.db.query(Resource).filter(Resource.id == resource_id).first()
    
    def get_all(self, filters=None):
        query = self.db.query(Resource)
        if filters:
            # Apply filters
            pass
        return query.all()
    
    def create(self, data):
        resource = Resource(**data)
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        return resource
    
    def update(self, resource_id, data):
        resource = self.get_by_id(resource_id)
        if not resource:
            return None
        
        for key, value in data.items():
            setattr(resource, key, value)
        
        self.db.commit()
        self.db.refresh(resource)
        return resource
    
    def delete(self, resource_id):
        resource = self.get_by_id(resource_id)
        if resource:
            self.db.delete(resource)
            self.db.commit()
            return True
        return False
```

---

## Common Tasks

### 1. Adding a New Endpoint

1. **Define Schema** (`schemas/resource_schema.py`):
```python
from marshmallow import Schema, fields, validate

class ResourceCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String()
    price = fields.Decimal(places=2, validate=validate.Range(min=0))
```

2. **Add Repository Method** (`repositories/resource_repository.py`):
```python
def create(self, data):
    resource = Resource(**data)
    self.db.add(resource)
    self.db.commit()
    self.db.refresh(resource)
    return resource
```

3. **Add Service Method** (`services/resource_service.py`):
```python
def create_resource(self, data, user_id):
    # Business logic validation
    if self.repository.exists_by_name(data['name'], user_id):
        raise ValueError("Resource with this name already exists")
    
    data['user_id'] = user_id
    resource = self.repository.create(data)
    
    # Invalidate cache
    self.cache.delete(f"resources:user:{user_id}")
    
    return resource
```

4. **Add Controller** (`controllers/resource_controller.py`):
```python
from flask import g, jsonify
from flask_jwt_extended import get_jwt_identity

class ResourceController:
    @staticmethod
    def create():
        user_id = get_jwt_identity()
        service = ResourceService(ResourceRepository(db.session))
        
        try:
            resource = service.create_resource(g.validated_data, user_id)
            return jsonify({'data': resource.to_dict()}), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
```

5. **Register Route** (`routes/resource_routes.py`):
```python
from flask import Blueprint
from app.core.lib.validators import validate_json
from flask_jwt_extended import jwt_required

blueprint = Blueprint('resources', __name__, url_prefix='/resources')

@blueprint.route('', methods=['POST'])
@jwt_required()
@validate_json(ResourceCreateSchema())
def create_resource():
    return ResourceController.create()
```

6. **Register Blueprint** (`app/blueprints.py`):
```python
from app.resources.routes.resource_routes import blueprint as resources_bp

def register_blueprints(app):
    # ... existing blueprints
    app.register_blueprint(resources_bp)
```

7. **Write Tests** (Testing Agent handles this):
```python
# tests/unit/test_resources.py
def test_create_resource_success(client, auth_headers, sample_resource_data):
    response = client.post('/resources', json=sample_resource_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json['data']['name'] == sample_resource_data['name']
```

### 2. Adding a New Model

1. **Create Model File** (`module/models/new_model.py`)
2. **Export in** `module/models/__init__.py`
3. **Register in** `migrations/check_all_models.py`:
```python
from app.module.models import NewModel  # Import to ensure registration
```
4. **Run DB initialization**:
```powershell
.\venv\Scripts\python.exe scripts\init_db.py
```

### 3. Adding Cache to Existing Endpoint

1. **Update Service** to add `_cached` method
2. **Add cache invalidation** on write operations (create/update/delete)
3. **Verify cache keys** follow standard: `resource:id` or `resource_list:filter`

### 4. Fixing Bugs

1. **Write failing test** that reproduces bug
2. **Fix the bug** in production code
3. **Verify test passes**
4. **Update integration tests** if API contract changed

---

## Critical Rules

### ✅ DO

1. **Follow layered architecture**: Route → Controller → Service → Repository → Model
2. **Use decorators**: `@jwt_required()`, `@validate_json()`, `@cache_route()`
3. **Return consistent JSON**: Always use `{"data": ...}` or `{"error": ...}`
4. **Validate all inputs**: Use Marshmallow schemas with `@validate_json`
5. **Cache read-heavy endpoints**: Use `CacheHelper` or `@cache_route`
6. **Invalidate cache on writes**: Delete relevant cache keys after create/update/delete
7. **Handle errors gracefully**: Catch exceptions, return proper HTTP codes
8. **Use transactions**: Repository methods commit; services orchestrate
9. **Test new features**: Coordinate with Testing Agent
10. **Document API changes**: Update API_DOCUMENTATION.md if adding/changing endpoints

### ❌ DON'T

1. **Don't skip validation**: Always use schemas, never trust raw input
2. **Don't hardcode config**: Use `config.py` and environment variables
3. **Don't bypass auth**: Every non-public endpoint needs `@jwt_required()`
4. **Don't put business logic in controllers**: Keep controllers thin, logic in services
5. **Don't query database in controllers**: Use services and repositories
6. **Don't return raw models**: Use `.to_dict()` or schemas
7. **Don't forget cache invalidation**: Stale cache = stale data
8. **Don't break existing tests**: Run tests before committing
9. **Don't modify test code as main agent**: Testing Agent owns test files
10. **Don't run integration tests in server terminal**: Use separate terminal

---

## Integration Test Constraints

**CRITICAL**: Integration tests validate real HTTP against a live server.

**Setup Requirements**:
```powershell
# 1. Start Docker (Postgres + Redis)
docker compose up -d

# 2. Initialize database
.\venv\Scripts\python.exe scripts\init_db.py

# 3. Start server (KEEP THIS TERMINAL OPEN)
.\venv\Scripts\python.exe run.py

# 4. Run tests (NEW TERMINAL)
.\venv\Scripts\python.exe -m pytest tests/integration -v

# 5. Cleanup
docker compose down -v
```

**Rules**:
- **Never run tests in server terminal** - Server must stay running
- **Ask before running integration tests** - They require setup
- **Use Docker infrastructure** - Not local Postgres
- **Tests take 6-8 minutes** - This is normal for real HTTP

---

## Module-Specific Context

### Auth Module
- JWT tokens in `Authorization: Bearer <token>` header
- Roles: `chef`, `client`, `admin`
- Public endpoints: `/auth/register`, `/auth/login`
- Protected: All others

### Admin Module
- Admin-only endpoints for user/data management
- Audit logging: All admin actions logged to `core.admin_audit_logs`
- Best-effort logging: Audit failures don't break endpoints

### Scrapers Module (Optional)
- Depends on `beautifulsoup4` (optional dependency)
- Blueprint only registered if bs4 installed
- Scrapes product prices from configured sources
- Active tables: `integrations.price_sources`, `integrations.scraped_prices`

### Public Module
- No authentication required
- Read-only access to chefs, dishes, menus
- Heavily cached (5-minute TTL)
- Used for public catalog browsing

---

## Recent Work (Dec 31, 2025)

### Completed
- ✅ Integration test suite (135 tests, all passing)
- ✅ All 10 modules validated with real HTTP tests
- ✅ Coverage increased to 75% (from 67%)
- ✅ Admin audit logging system implemented
- ✅ Scrapers module integration tests added
- ✅ Legacy `app/scraper` module removed (was unused)
- ✅ Documentation consolidated (reduced from 5 files to 2)

### Infrastructure
- Docker Compose for integration test isolation
- PostgreSQL schemas properly separated (auth/core/integrations)
- Redis caching working across all modules
- All models registered and validated

### Testing Status
- **296 total tests** (161 unit + 135 integration)
- **100% pass rate**
- **75% code coverage** (target: 80%+)
- **10/10 modules validated**

---

## Coordination with Specialized Agents

### Testing Agent
- Owns all files in `tests/`
- Writes/maintains/fixes tests
- Reports coverage and failures
- **You implement features, they test them**

### Database Agent
- Owns migrations and schema changes
- Optimizes queries and indexes
- Handles database performance
- **You define models, they optimize storage**

### Security Agent
- Audits authentication/authorization
- Reviews input validation
- Checks for vulnerabilities
- **You implement features, they secure them**

### Documentation Agent
- Maintains API documentation
- Updates technical docs
- Keeps docs in sync with code
- **You change APIs, they document them**

### Frontend Agent
- Implements UI/UX
- Consumes backend APIs
- Handles client-side logic
- **You provide APIs, they consume them**

---

## Quick Reference

### Start Development Server
```powershell
cd backend
.\venv\Scripts\python.exe run.py
# Server: http://localhost:5000
```

### Run Unit Tests
```powershell
.\venv\Scripts\python.exe -m pytest tests/unit -v --cov=app
```

### Initialize Database
```powershell
.\venv\Scripts\python.exe scripts\init_db.py
```

### Seed Admin User
```powershell
.\venv\Scripts\python.exe scripts\seed_admin.py
# Username: admin
# Password: Admin123!@#
```

### Check All Models Registered
```powershell
.\venv\Scripts\python.exe migrations\check_all_models.py
```

---

## Documentation Files

- **`README.md`**: Project overview, setup instructions
- **`tests/TESTING_GUIDE.md`**: Testing commands and patterns
- **`tests/integration/VALIDATION_RESULTS.md`**: Detailed test validation log
- **`docs/API_DOCUMENTATION.md`**: Comprehensive API reference
- **`docs/CACHE_KEYS_STANDARD.md`**: Cache naming conventions
- **`.github/copilot-instructions-*.md`**: Agent-specific instructions

---

## Environment Variables

```bash
# config.py handles 3 environments: development, testing, production

# Development (default)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/lyftercook
REDIS_URL=redis://localhost:6379/0

# Testing (unit tests)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/lyftercook_test
REDIS_URL=redis://localhost:6379/1

# Testing (integration - Docker)
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/lyftercook_docker
REDIS_URL=redis://:testredispassword@localhost:6380/0

# JWT
JWT_SECRET_KEY=your-secret-key-here

# Optional (scrapers)
CLOUDINARY_URL=cloudinary://...
```

---

## Getting Started as New Agent

1. **Read this entire document** - Understand architecture and patterns
2. **Review current status** - Check recent work section
3. **Explore key files**:
   - `app/__init__.py` - Application factory
   - `app/blueprints.py` - Blueprint registration
   - `app/core/database.py` - Database setup
   - `config.py` - Configuration
4. **Understand testing constraints** - Integration tests require special setup
5. **Check terminal context** - Don't run integration tests in server terminal
6. **Coordinate with specialized agents** - Stay in your lane

---

**Last Updated**: December 31, 2025  
**Backend Version**: 2.0.0  
**API Endpoints**: 60+  
**Test Coverage**: 75%
