# LyfterCook Backend - AI Agent Instructions

## Architecture Overview

**Stack**: Flask + SQLAlchemy + PostgreSQL + Redis (caching)  
**Pattern**: Three-layer architecture (Controller → Service → Repository)  
**Auth**: JWT tokens with role-based access (CHEF, ADMIN)

### Module Structure
Each feature module (`dishes/`, `menus/`, `clients/`, etc.) follows:
```
module/
├── controllers/    # HTTP layer - request/response handling
├── services/       # Business logic layer
├── repositories/   # Data access layer (SQLAlchemy)
├── models/         # SQLAlchemy ORM models
└── schemas/        # Marshmallow validation schemas
```

**Critical**: Controllers instantiate services per-request using `get_db()` from Flask's `g` context. Never store database sessions as class attributes.

## Database Schema Convention

PostgreSQL with **three schemas**:
- `auth` - Users and authentication
- `core` - Main business entities (chefs, dishes, menus, clients, quotations)
- `integrations` - External services (appointments, scrapers)

All models must specify `__table_args__ = {'schema': 'schemaname'}`. Foreign keys use full schema paths: `ForeignKey('core.chefs.id')`.

## Key Patterns

### 1. Service Instantiation (CRITICAL)
```python
# ✅ CORRECT - Per-request instantiation
def _get_service(self):
    db = get_db()
    dish_repo = DishRepository(db)
    chef_repo = ChefRepository(db)
    return DishService(dish_repo, chef_repo)

# ❌ WRONG - Never store in __init__
def __init__(self):
    self.service = DishService()  # BAD: Reuses sessions
```

### 2. Authentication Decorators
```python
from app.core.middleware.auth_middleware import jwt_required, role_required

@jwt_required  # Requires valid JWT, stores user in g.current_user
def protected_route():
    user = g.current_user  # Dict with id, username, email, role

@role_required('admin')  # Restricts to specific role
def admin_only_route():
    pass
```

### 3. Enum Handling
PostgreSQL custom enums require Python enum classes:
```python
import enum
from sqlalchemy import Enum

class MenuStatus(enum.Enum):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    
status = Column(Enum(MenuStatus, name='menustatus', create_type=False))
```
`create_type=False` means enum exists in DB. Serialize with `.value` in `to_dict()`.

### 4. Cache Invalidation
Services use `CacheHelper` for caching:
```python
# In service method
self.cache_helper = CacheHelper(resource_name="dish", version="v1")

# GET with cache
dish = self.cache_helper.get_or_set(
    cache_key=f"detail:{dish_id}:user:{user_id}",
    fetch_func=lambda: self.repository.get_by_id(dish_id),
    schema_class=DishResponseSchema,
    ttl=600
)

# Invalidate on UPDATE/DELETE
self.cache_helper.invalidate(
    f"detail:{dish_id}:user:{user_id}",
    f"list:chef:{chef.id}:active:True"
)
```

**Pattern**: Cache keys must match format used in GET methods: `detail:{id}:user:{user_id}` or `list:chef:{chef_id}:active:{bool}`.

### 5. Duplication Prevention
Use two-layer approach:
1. **DB constraints**: `UNIQUE(chef_id, name)` in migrations
2. **Service validation**: Check before insert for friendly errors
```python
# In service create method
existing = self.repository.get_by_chef_and_name(chef_id, name)
if existing:
    raise ValueError(f"You already have a dish named '{name}'")
```

### 6. Ownership Verification
All chef endpoints verify ownership:
```python
def get_dish_by_id(self, dish_id, user_id):
    chef = self.chef_repository.get_by_user_id(user_id)
    dish = self.dish_repository.get_by_id(dish_id)
    if not dish or dish.chef_id != chef.id:
        return None  # or raise ValueError
```

## Testing

**Location**: `tests/unit/test_{module}.py`  
**Run**: `pytest tests/unit -v`  
**Coverage**: `pytest --cov=app tests/unit`

### Test Database Setup

**Critical**: Uses PostgreSQL test database (`lyftercook_test`), NOT SQLite:
```bash
# Create test database
psql -U postgres
CREATE DATABASE lyftercook_test;
\q
```

Test DB schema matches production with three schemas (auth, core, integrations). Created/torn down automatically by `conftest.py`.

### Test Structure Pattern

**Organize by HTTP verb + resource**:
```python
class TestDishCreate:
    """Tests for creating dishes."""
    
    def test_create_dish_success(self, client, chef_headers, test_chef, sample_dish_data):
        """Test successful dish creation with ingredients."""
        response = client.post('/dishes', json=sample_dish_data, headers=chef_headers)
        result = assert_success_response(response, 201)
        assert result['data']['name'] == sample_dish_data['name']
        ResponseValidator.validate_dish_response(result['data'])

class TestDishList:
    """Tests for listing dishes."""
    # ...

class TestDishUpdate:
    """Tests for updating dishes."""
    # ...
```

**Naming convention**: `test_{verb}_{resource}_{scenario}` (e.g., `test_create_dish_success`, `test_update_dish_not_found`)

### Essential Fixtures (conftest.py)

**Core fixtures**:
- `app` - Flask application (session scope)
- `database` - PostgreSQL test DB with schemas (session scope)
- `db_session` - Fresh DB session per test with auto-rollback (function scope)
- `client` - Flask test client

**Auth fixtures**:
- `test_user` - Admin user object
- `test_chef_user` - Chef user object (separate from test_user)
- `auth_headers` - Headers with admin JWT token: `{'Authorization': 'Bearer ...', 'Content-Type': 'application/json'}`
- `chef_headers` - Headers with chef JWT token

**Data fixtures**:
- `test_chef` - Chef profile linked to `test_chef_user`
- `test_client_data` - Client object for testing
- `test_dish` - Dish with ingredients
- `test_menu` - Menu with dishes
- `sample_dish_data` - Dict for POST requests
- `sample_client_data` - Dict for POST requests

**Token generation**:
```python
def generate_token(user_id, email, role):
    """Generate JWT token for testing."""
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
```

### Test Helpers (test_helpers.py)

**Use these instead of raw assertions**:
```python
from tests.unit.test_helpers import (
    assert_success_response,     # Validates 2xx + JSON structure
    assert_not_found_error,      # Validates 404
    assert_validation_error,     # Validates 400 with validation details
    assert_unauthorized_error,   # Validates 401
    ResponseValidator           # Schema validators
)

# Example usage
result = assert_success_response(response, 201)  # Auto-checks status + parses JSON
assert result['data']['name'] == 'Expected Name'

# Validate complex responses
ResponseValidator.validate_dish_response(result['data'])  # Checks all dish fields
ResponseValidator.validate_menu_response(result['data'])  # Checks menu + nested dishes
```

**Available validators**:
- `validate_dish_response(data)` - Dish with ingredients
- `validate_menu_response(data)` - Menu with dishes array
- `validate_chef_response(data)` - Chef with user data
- `validate_quotation_response(data)` - Quotation with items
- `validate_appointment_response(data)` - Appointment with client

### Testing Authentication

**Public endpoint** (no auth):
```python
def test_public_endpoint(client):
    response = client.get('/public/chefs')
    assert_success_response(response, 200)
```

**Protected endpoint** (requires JWT):
```python
def test_protected_endpoint(client, chef_headers):
    response = client.get('/dishes', headers=chef_headers)
    assert_success_response(response, 200)
```

**Test unauthorized access**:
```python
def test_endpoint_without_auth(client):
    response = client.get('/dishes')  # No headers
    assert_unauthorized_error(response)
```

**Test wrong role**:
```python
def test_admin_endpoint_as_chef(client, chef_headers):
    response = client.get('/admin/dashboard', headers=chef_headers)
    assert response.status_code == 403  # Forbidden
```

### Testing Ownership Verification

**Critical pattern**: Test that users can't access other users' resources:
```python
def test_get_other_chef_dish(client, chef_headers, other_chef_dish):
    """Test that chef cannot access another chef's dish."""
    response = client.get(f'/dishes/{other_chef_dish.id}', headers=chef_headers)
    assert_not_found_error(response)  # Should return 404, not 403
```

Create separate fixture for "other chef" data:
```python
@pytest.fixture
def other_chef(db_session):
    user = User(username='otherchef', email='other@test.com', ...)
    db_session.add(user)
    chef = Chef(user_id=user.id, ...)
    db_session.add(chef)
    db_session.commit()
    return chef
```

### Testing Validation

**Schema validation errors**:
```python
def test_create_with_invalid_email(client, chef_headers):
    data = {'name': 'Test', 'email': 'not-an-email'}
    response = client.post('/clients', json=data, headers=chef_headers)
    
    error = assert_validation_error(response)
    assert 'email' in error['details']  # Field-specific error
```

**Business rule validation**:
```python
def test_create_duplicate_dish(client, chef_headers, test_dish):
    """Test that duplicate dish names are rejected."""
    data = {'name': test_dish.name, 'category': 'Main'}  # Same name
    response = client.post('/dishes', json=data, headers=chef_headers)
    
    assert response.status_code == 400
    result = response.get_json()
    assert 'already have a dish named' in result['error']
```

### Testing Cascades and Relationships

**Test cascade deletes**:
```python
def test_delete_dish_deletes_ingredients(client, chef_headers, test_dish, db_session):
    """Test that deleting dish also deletes ingredients."""
    from app.dishes.models import Ingredient
    
    # Verify ingredients exist
    ingredients = db_session.query(Ingredient).filter_by(dish_id=test_dish.id).all()
    assert len(ingredients) > 0
    
    # Delete dish
    response = client.delete(f'/dishes/{test_dish.id}', headers=chef_headers)
    assert_success_response(response, 200)
    
    # Verify ingredients deleted
    db_session.expire_all()  # Clear session cache
    ingredients = db_session.query(Ingredient).filter_by(dish_id=test_dish.id).all()
    assert len(ingredients) == 0
```

**Test nested creates**:
```python
def test_create_dish_with_ingredients(client, chef_headers):
    data = {
        'name': 'Pasta',
        'ingredients': [
            {'name': 'Pasta', 'quantity': 200, 'unit': 'g'},
            {'name': 'Sauce', 'quantity': 100, 'unit': 'ml'}
        ]
    }
    response = client.post('/dishes', json=data, headers=chef_headers)
    result = assert_success_response(response, 201)
    assert len(result['data']['ingredients']) == 2
```

### Testing Cache Invalidation

**Pattern**: Create → Read (cached) → Update → Read (fresh):
```python
def test_cache_invalidation_on_update(client, chef_headers, test_dish):
    # First read - populates cache
    response1 = client.get(f'/dishes/{test_dish.id}', headers=chef_headers)
    result1 = assert_success_response(response1, 200)
    
    # Update
    client.put(f'/dishes/{test_dish.id}', 
               json={'name': 'Updated'}, 
               headers=chef_headers)
    
    # Second read - should get fresh data
    response2 = client.get(f'/dishes/{test_dish.id}', headers=chef_headers)
    result2 = assert_success_response(response2, 200)
    assert result2['data']['name'] == 'Updated'
    assert result2['data']['name'] != result1['data']['name']
```

### Running Specific Tests

```bash
# Single test file
pytest tests/unit/test_dishes.py -v

# Single test class
pytest tests/unit/test_dishes.py::TestDishCreate -v

# Single test function
pytest tests/unit/test_dishes.py::TestDishCreate::test_create_dish_success -v

# Tests matching pattern
pytest -k "test_create" -v  # All create tests

# Failed tests only
pytest --lf  # Last failed
pytest --ff  # Failed first

# With print statements
pytest -v -s

# Stop on first failure
pytest -x

# Parallel execution
pytest -n auto  # Requires pytest-xdist
```

### Debugging Test Failures

**Common issues**:

1. **"relation does not exist"**: Test DB not initialized
   ```bash
   psql -U postgres
   CREATE DATABASE lyftercook_test;
   ```

2. **"could not serialize access"**: DB session conflict
   - Ensure using `db_session` fixture, not global `SessionLocal`
   - Call `db_session.expire_all()` before re-querying

3. **"Invalid or expired token"**: JWT secret mismatch
   - Check `JWT_SECRET_KEY` in `conftest.py` matches token generation

4. **"Chef profile not found"**: Missing fixture dependency
   - Add `test_chef` fixture to test signature
   - Ensure `test_chef_user` created before `test_chef`

5. **"404 when expecting data"**: Ownership check failing
   - Verify test uses correct headers (`chef_headers` vs `auth_headers`)
   - Check that test data belongs to the authenticated user

**Debug with print statements**:
```python
def test_something(client, chef_headers, test_dish):
    print(f"Test dish ID: {test_dish.id}")
    print(f"Token: {chef_headers['Authorization']}")
    response = client.get(f'/dishes/{test_dish.id}', headers=chef_headers)
    print(f"Response: {response.get_json()}")
```
Run with: `pytest -v -s tests/unit/test_dishes.py::test_something`

### Coverage Requirements

**Target**: 80%+ coverage for services and repositories

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html tests/unit/

# View report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac

# Coverage by module
pytest --cov=app.dishes --cov-report=term-missing tests/unit/test_dishes.py
```

**Focus areas**: Services (business logic) and repositories (data access). Controllers are thin wrappers, 60%+ OK.

### Writing New Tests

**Checklist for new endpoint tests**:
1. ✅ Happy path (success scenario)
2. ✅ Missing required fields (validation)
3. ✅ Invalid data types (validation)
4. ✅ Not found (404)
5. ✅ Unauthorized (401 - no token)
6. ✅ Forbidden (403 - wrong role)
7. ✅ Ownership check (can't access other user's data)
8. ✅ Duplicate prevention (if applicable)

**Template**:
```python
class TestResourceCreate:
    def test_create_success(self, client, chef_headers):
        """Test successful creation."""
        pass
    
    def test_create_validation_error(self, client, chef_headers):
        """Test validation catches invalid data."""
        pass
    
    def test_create_unauthorized(self, client):
        """Test requires authentication."""
        pass
    
    def test_create_duplicate(self, client, chef_headers, existing_resource):
        """Test duplicate prevention."""
        pass
```

### Integration Tests (Future)

**Location**: `tests/integration/` (not yet implemented)

**Planned coverage**:
- Multi-module workflows (create chef → create dish → create menu)
- External service integration (Cloudinary, SendGrid)
- Database transaction rollbacks
- Concurrent request handling
- Rate limiting

**Pattern** (when implemented):
```python
@pytest.mark.integration
def test_full_menu_creation_workflow(client, chef_headers):
    # Create chef profile
    # Create multiple dishes
    # Create menu with dishes
    # Verify all relationships intact
```

## Migrations

**Location**: `migrations/` (SQL files)  
**Pattern**: `00X_description.sql` with Python runner `run_X.py`

Example migration structure:
```sql
BEGIN;
-- Migration logic with IF NOT EXISTS checks
ALTER TABLE core.table ADD CONSTRAINT IF NOT EXISTS...;
COMMIT;
```

Always include rollback validation and use `DROP CONSTRAINT IF EXISTS` before `ADD CONSTRAINT`.

## Common Tasks

### Adding New Endpoint
1. Create schema in `schemas/` (Marshmallow)
2. Add repository method in `repositories/`
3. Add service method with business logic
4. Add controller method with `@validate_json` decorator
5. Register route in `app/blueprints.py`
6. Add test in `tests/unit/test_{module}.py`

### Adding Cache to Endpoint
1. Add `CacheHelper` to service `__init__`
2. Create `_cached` version of method
3. Use `get_or_set` with proper cache key format
4. Add invalidation in UPDATE/DELETE methods

### Handling Enums
1. Check if enum exists: Query `pg_type` table
2. Create migration if needed: `ALTER TYPE enumname ADD VALUE`
3. Define Python enum class matching DB values
4. Use `Enum(ClassName, name='dbname', create_type=False)`

## Security Notes

- Public registration only creates CHEF role (hardcoded in `auth_service.py`)
- Admin creation via `scripts/seed_admin.py` only
- JWT tokens expire in 24 hours
- Password hashing uses bcrypt
- All admin actions logged in `admin_audit_logs`

## Documentation

- **📚 Documentation Hub**: `docs/INDEX.md`
- **API endpoints**: `docs/api/API_DOCUMENTATION.md`
- **Architecture & Design**: `docs/architecture/`
  - `PROJECT_PLAN.md` - Complete architecture
  - `SCHEMA_MIGRATION.md` - Database migrations
  - `CACHE_IMPLEMENTATION.md` - Redis caching
  - `ADMIN_ENDPOINTS_DESIGN.md` - Admin system
- **Decisions (ADRs)**: `docs/decisions/`
- **Testing guide**: `backend/tests/TESTING_GUIDE.md`
- **Archived docs**: `docs/archive/` - Historical phase completions
