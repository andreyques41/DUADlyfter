# 🧪 Unit Testing Strategy - Pet E-commerce API

**Project:** Pet E-commerce Backend  
**Date:** October 24, 2025  
**Status:** Proposal for Review

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Testing Philosophy](#testing-philosophy)
3. [Project Architecture Analysis](#project-architecture-analysis)
4. [Testing Layers Strategy](#testing-layers-strategy)
5. [Directory Structure](#directory-structure)
6. [Testing Tools & Dependencies](#testing-tools--dependencies)
7. [Test Coverage Goals](#test-coverage-goals)
8. [Implementation Phases](#implementation-phases)
9. [Test Categories](#test-categories)
10. [Fixtures & Test Data](#fixtures--test-data)
11. [CI/CD Integration](#cicd-integration)
12. [Examples](#examples)

---

## 📊 Executive Summary

### Current State
- **42 REST endpoints** across 3 main modules (auth, products, sales)
- **Layered architecture**: Routes → Services → Repositories → Models
- **Manual testing only** - no automated test suite
- README mentions testing but no tests/ directory exists

### Proposed Solution
- **Comprehensive pytest-based test suite** with 200+ tests
- **4 testing layers**: Unit, Integration, API, End-to-End
- **80%+ code coverage** target
- **CI/CD ready** with automated test runs
- **Test database** isolation with fixtures

### Benefits
1. ✅ **Confidence** - Catch bugs before production
2. ✅ **Refactoring Safety** - Change code without breaking functionality
3. ✅ **Documentation** - Tests serve as usage examples
4. ✅ **Quality Assurance** - Enforce business rules
5. ✅ **Faster Development** - Quick feedback on changes

---

## 🎯 Testing Philosophy

### The Testing Pyramid

```
           /\
          /  \  E2E Tests (5%)
         /____\  
        /      \  Integration Tests (15%)
       /________\
      /          \  Unit Tests (80%)
     /____________\
```

**Distribution:**
- **80% Unit Tests** - Fast, isolated, specific
- **15% Integration Tests** - Component interactions
- **5% E2E Tests** - Full workflow validation

### Key Principles

1. **F.I.R.S.T Principles**
   - **F**ast - Tests run in milliseconds
   - **I**solated - No dependencies between tests
   - **R**epeatable - Same result every time
   - **S**elf-validating - Clear pass/fail
   - **T**imely - Written alongside code

2. **AAA Pattern** (Arrange, Act, Assert)
   ```python
   def test_example():
       # Arrange - Set up test data
       user = User(username="test", email="test@test.com")
       
       # Act - Execute the code under test
       result = user_service.create_user(user)
       
       # Assert - Verify expectations
       assert result is not None
       assert result.username == "test"
   ```

3. **Test Isolation**
   - Use **mocks** for external dependencies
   - Use **fixtures** for test data setup
   - Use **test database** for integration tests
   - **Rollback** after each test

---

## 🏗️ Project Architecture Analysis

### Current Layer Structure

```
┌─────────────────────────────────────────┐
│            ROUTES LAYER                  │  Flask blueprints, HTTP handling
│  auth_routes.py, product_routes.py...   │  Input validation, response formatting
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           SERVICES LAYER                 │  Business logic orchestration
│  auth_service.py, product_service.py... │  Access control, workflow management
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         REPOSITORIES LAYER               │  Data access, CRUD operations
│  user_repository.py, product_repo...    │  ORM queries, transactions
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            MODELS LAYER                  │  SQLAlchemy ORM models
│  user.py, product.py, order.py...       │  Table definitions, relationships
└──────────────────────────────────────────┘
```

### Cross-Cutting Concerns

```
┌─────────────────────────────────────────┐
│          SCHEMAS LAYER                   │  Marshmallow validation
│  user_schema.py, product_schema.py...   │  Data serialization/deserialization
└──────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         MIDDLEWARE LAYER                 │  Authentication, authorization
│  auth_decorators.py, JWT handling       │  Role-based access control
└──────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         UTILITIES LAYER                  │  Shared functionality
│  reference_data.py, cache_manager.py    │  Configuration, helpers
└──────────────────────────────────────────┘
```

### Testing Targets by Layer

| Layer | Test Type | Mock Dependencies | Coverage Goal |
|-------|-----------|-------------------|---------------|
| **Routes** | Integration | Services, Auth | 85% |
| **Services** | Unit | Repositories | 90% |
| **Repositories** | Integration | Database | 85% |
| **Models** | Unit | None | 95% |
| **Schemas** | Unit | None | 95% |
| **Middleware** | Integration | Database, JWT | 90% |

---

## 🧪 Testing Layers Strategy

### Layer 1: Unit Tests (80% of tests)

**Purpose:** Test individual components in isolation

**Characteristics:**
- Very fast (< 10ms per test)
- No database, no network, no file system
- Use mocks for all dependencies
- Focus on logic, not integration

**What to Test:**

#### A. **Models** (Validation, Business Logic)
```python
# Test model validation
def test_user_model_validates_email_format()
def test_product_price_must_be_positive()
def test_order_cannot_have_negative_quantity()

# Test model methods
def test_user_password_hashing()
def test_cart_total_calculation()
def test_order_status_transitions()
```

#### B. **Schemas** (Marshmallow Validation)
```python
# Test schema validation
def test_user_registration_schema_requires_email()
def test_product_schema_validates_price_range()
def test_order_schema_prevents_duplicate_products()

# Test schema transformations
def test_user_response_schema_excludes_password()
def test_product_schema_converts_role_id_to_name()
```

#### C. **Services** (Business Logic - MOCKED)
```python
# Test business rules with mocked repositories
def test_create_user_checks_duplicate_email()
def test_create_order_validates_stock_availability()
def test_cancel_order_only_allowed_for_pending_status()
def test_admin_can_view_all_orders()
def test_user_can_only_view_own_orders()
```

#### D. **Utilities** (Helper Functions)
```python
# Test utility functions
def test_reference_data_caching()
def test_jwt_token_generation()
def test_jwt_token_expiration()
def test_password_hashing_bcrypt()
```

### Layer 2: Integration Tests (15% of tests)

**Purpose:** Test component interactions with real dependencies

**Characteristics:**
- Medium speed (50-200ms per test)
- Use test database (with rollback)
- Real ORM queries
- Test actual integrations

**What to Test:**

#### A. **Repository + Database**
```python
# Test actual database operations
def test_user_repository_creates_user_in_database()
def test_product_repository_filters_by_category()
def test_order_repository_with_items_cascade_delete()
def test_cart_repository_updates_quantities()
```

#### B. **Service + Repository**
```python
# Test service with real repository
def test_create_user_service_with_real_database()
def test_create_order_service_decrements_stock()
def test_return_service_creates_invoice_refund()
```

#### C. **Middleware + Database**
```python
# Test auth decorators with real database
def test_token_required_decorator_verifies_user_exists()
def test_admin_required_decorator_checks_role_in_db()
def test_role_verification_from_database()
```

### Layer 3: API Tests (4% of tests)

**Purpose:** Test HTTP endpoints end-to-end

**Characteristics:**
- Slower (100-500ms per test)
- Use Flask test client
- Test actual HTTP requests/responses
- Full request/response cycle

**What to Test:**

#### A. **Authentication Endpoints**
```python
def test_register_endpoint_creates_user()
def test_login_endpoint_returns_jwt_token()
def test_protected_endpoint_requires_authentication()
def test_admin_endpoint_requires_admin_role()
```

#### B. **CRUD Endpoints**
```python
def test_create_product_endpoint()
def test_get_products_with_filters()
def test_update_product_requires_admin()
def test_delete_product_cascade()
```

#### C. **Workflow Endpoints**
```python
def test_add_to_cart_workflow()
def test_create_order_from_cart()
def test_order_status_update_workflow()
def test_return_request_approval_workflow()
```

### Layer 4: End-to-End Tests (1% of tests)

**Purpose:** Test complete user journeys

**Characteristics:**
- Slowest (1-5 seconds per test)
- Test complete workflows
- Multiple endpoints in sequence
- Validate business scenarios

**What to Test:**

```python
def test_complete_shopping_journey():
    """
    1. Register user
    2. Browse products
    3. Add products to cart
    4. Create order
    5. Verify invoice created
    6. Request return
    7. Admin approves return
    8. Verify refund
    """

def test_admin_product_management_workflow():
    """
    1. Admin login
    2. Create product
    3. Update product details
    4. Monitor orders for product
    5. Update stock
    6. Archive product
    """
```

---

## 📁 Directory Structure

```
Pet_e_commerce/
├── tests/                              # Root test directory
│   ├── __init__.py
│   ├── conftest.py                     # Pytest configuration & global fixtures
│   ├── pytest.ini                      # Pytest settings
│   │
│   ├── unit/                           # Unit tests (80%)
│   │   ├── __init__.py
│   │   ├── test_models/                # Model tests
│   │   │   ├── __init__.py
│   │   │   ├── test_user_model.py
│   │   │   ├── test_product_model.py
│   │   │   ├── test_cart_model.py
│   │   │   ├── test_order_model.py
│   │   │   ├── test_invoice_model.py
│   │   │   └── test_return_model.py
│   │   │
│   │   ├── test_schemas/               # Schema validation tests
│   │   │   ├── __init__.py
│   │   │   ├── test_user_schema.py
│   │   │   ├── test_product_schema.py
│   │   │   ├── test_cart_schema.py
│   │   │   ├── test_order_schema.py
│   │   │   ├── test_invoice_schema.py
│   │   │   └── test_return_schema.py
│   │   │
│   │   ├── test_services/              # Service layer tests (mocked)
│   │   │   ├── __init__.py
│   │   │   ├── test_auth_service.py
│   │   │   ├── test_product_service.py
│   │   │   ├── test_cart_service.py
│   │   │   ├── test_order_service.py
│   │   │   ├── test_invoice_service.py
│   │   │   └── test_return_service.py
│   │   │
│   │   └── test_utils/                 # Utility function tests
│   │       ├── __init__.py
│   │       ├── test_reference_data.py
│   │       ├── test_jwt_utils.py
│   │       ├── test_security_service.py
│   │       └── test_cache_manager.py
│   │
│   ├── integration/                    # Integration tests (15%)
│   │   ├── __init__.py
│   │   ├── test_repositories/          # Repository + DB tests
│   │   │   ├── __init__.py
│   │   │   ├── test_user_repository.py
│   │   │   ├── test_product_repository.py
│   │   │   ├── test_cart_repository.py
│   │   │   ├── test_order_repository.py
│   │   │   ├── test_invoice_repository.py
│   │   │   └── test_return_repository.py
│   │   │
│   │   ├── test_services_integration/  # Service + Repository tests
│   │   │   ├── __init__.py
│   │   │   ├── test_auth_service_integration.py
│   │   │   ├── test_product_service_integration.py
│   │   │   ├── test_cart_service_integration.py
│   │   │   └── test_order_service_integration.py
│   │   │
│   │   └── test_middleware/            # Auth decorators + DB tests
│   │       ├── __init__.py
│   │       └── test_auth_decorators.py
│   │
│   ├── api/                            # API endpoint tests (4%)
│   │   ├── __init__.py
│   │   ├── test_auth_routes.py         # Auth endpoints
│   │   ├── test_user_routes.py         # User CRUD endpoints
│   │   ├── test_product_routes.py      # Product CRUD endpoints
│   │   ├── test_cart_routes.py         # Cart management endpoints
│   │   ├── test_order_routes.py        # Order lifecycle endpoints
│   │   ├── test_invoice_routes.py      # Invoice management endpoints
│   │   └── test_return_routes.py       # Return workflow endpoints
│   │
│   ├── e2e/                            # End-to-end tests (1%)
│   │   ├── __init__.py
│   │   ├── test_shopping_journey.py    # Complete customer workflow
│   │   ├── test_admin_workflow.py      # Admin operations workflow
│   │   └── test_return_workflow.py     # Return request to refund
│   │
│   ├── fixtures/                       # Test data & fixtures
│   │   ├── __init__.py
│   │   ├── user_fixtures.py            # User test data
│   │   ├── product_fixtures.py         # Product test data
│   │   ├── cart_fixtures.py            # Cart test data
│   │   ├── order_fixtures.py           # Order test data
│   │   └── database_fixtures.py        # DB setup/teardown
│   │
│   └── helpers/                        # Test utilities
│       ├── __init__.py
│       ├── api_helpers.py              # HTTP request helpers
│       ├── auth_helpers.py             # JWT token helpers
│       └── database_helpers.py         # DB testing utilities
│
└── pytest.ini                          # Pytest configuration (root level)
```

**File Count Estimate:**
- Unit tests: ~30 files (160+ tests)
- Integration tests: ~10 files (30+ tests)
- API tests: ~7 files (28+ tests)
- E2E tests: ~3 files (6+ tests)
- **Total: ~50 test files, 220+ tests**

---

## 🛠️ Testing Tools & Dependencies

### Core Testing Framework

```txt
# Testing Framework
pytest==8.3.3                    # Main testing framework
pytest-cov==5.0.0                # Coverage reports
pytest-mock==3.14.0              # Mocking utilities
pytest-flask==1.3.0              # Flask testing utilities

# Assertions & Mocking
pytest-factoryboy==2.7.0         # Test data factories
faker==30.8.2                    # Fake data generation
freezegun==1.5.1                 # Mock datetime
responses==0.25.3                # Mock HTTP requests

# Database Testing
pytest-postgresql==6.1.1         # Temporary PostgreSQL instances
sqlalchemy-utils==0.41.2         # Test database utilities

# Code Quality
coverage==7.6.4                  # Coverage analysis
pytest-html==4.1.1               # HTML test reports
pytest-xdist==3.6.1              # Parallel test execution
```

### Updated requirements.txt

```txt
# Production Dependencies
bcrypt==4.3.0
Flask==3.1.1
marshmallow==4.0.0
PyJWT==2.10.1
SQLAlchemy==2.0.44
psycopg2-binary==2.9.10
python-dotenv==1.0.1

# Testing Dependencies (dev only)
pytest==8.3.3
pytest-cov==5.0.0
pytest-mock==3.14.0
pytest-flask==1.3.0
pytest-factoryboy==2.7.0
faker==30.8.2
freezegun==1.5.1
responses==0.25.3
pytest-postgresql==6.1.1
sqlalchemy-utils==0.41.2
coverage==7.6.4
pytest-html==4.1.1
pytest-xdist==3.6.1
```

### Pytest Configuration (pytest.ini)

```ini
[pytest]
# Test discovery patterns
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Directories to search for tests
testpaths = tests

# Markers for test categorization
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (database)
    api: API endpoint tests
    e2e: End-to-end workflow tests
    slow: Tests that take > 1 second
    auth: Authentication related tests
    products: Product module tests
    sales: Sales module tests
    smoke: Critical functionality tests

# Coverage settings
addopts =
    --verbose
    --strict-markers
    --tb=short
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --maxfail=5

# Logging
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S

# Ignore warnings
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

---

## 📊 Test Coverage Goals

### Module-Level Coverage Targets (Industry Standard Aligned)

| Module | Minimum | Target | Ideal | Justification |
|--------|---------|--------|-------|---------------|
| **auth/** | 90% | 95% | 98% | **CRÍTICO** - Seguridad y acceso al sistema |
| **sales/** | 85% | 90% | 95% | **CRÍTICO** - Dinero, órdenes, pagos, devoluciones |
| **products/** | 80% | 85% | 90% | **IMPORTANTE** - CRUD principal pero menos crítico |
| **core/** | 75% | 80% | 85% | **INFRAESTRUCTURA** - Middleware, database, utils |
| **Overall** | **80%** | **85%** | **90%** | **E-commerce production standard** |

### Coverage Philosophy: Differentiated by Risk

```
┌──────────────────────────────────────────────────┐
│ CRITICAL PATHS (100% coverage MANDATORY)         │
├──────────────────────────────────────────────────┤
│ ✓ User registration & email validation          │
│ ✓ Login & JWT generation                        │
│ ✓ Token validation & expiration                 │
│ ✓ Role-based access control                     │
│ ✓ Order creation → Invoice generation           │
│ ✓ Payment status updates                        │
│ ✓ Stock validation & updates                    │
│ ✓ Stock restoration on cancellation             │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ HIGH PRIORITY (90-95% coverage)                  │
├──────────────────────────────────────────────────┤
│ ✓ Business logic in Services layer              │
│ ✓ Access control enforcement                    │
│ ✓ Cart management & calculations                │
│ ✓ Return request workflows                      │
│ ✓ Data integrity constraints                    │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ STANDARD (80-85% coverage)                       │
├──────────────────────────────────────────────────┤
│ ✓ CRUD operations (Repositories)                │
│ ✓ API Routes & HTTP handling                    │
│ ✓ Schema validation (Marshmallow)               │
│ ✓ Model relationships                           │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ INFRASTRUCTURE (70-80% coverage acceptable)      │
├──────────────────────────────────────────────────┤
│ ✓ Configuration & setup                         │
│ ✓ Logging & debugging utilities                 │
│ ✓ Cache management                              │
│ ✓ Reference data initialization                 │
└──────────────────────────────────────────────────┘
```

### CI/CD Enforcement Rules

```python
# pytest.ini configuration
[pytest]
addopts = --cov-fail-under=80  # Minimum gate for CI/CD

# Per-module enforcement (future implementation)
--cov=app.auth --cov-fail-under=90
--cov=app.sales --cov-fail-under=85
--cov=app.products --cov-fail-under=80
--cov=app.core --cov-fail-under=75
```

---

## 🚀 Implementation Phases (ACCELERATED - 3-4 Days)

### Phase 1: Foundation + Core Unit Tests (Day 1 - 6-8 hours)
**Goal:** Infrastructure setup + Models & Schemas tested

**Morning (3-4 hours):**
- [ ] Create tests/ directory structure
- [ ] Install testing dependencies (`pip install pytest pytest-cov pytest-flask faker pytest-mock`)
- [ ] Configure pytest.ini
- [ ] Create conftest.py with PostgreSQL fixtures
- [ ] Set up test database (PostgreSQL)
- [ ] Verify setup with sample test

**Afternoon (3-4 hours):**
- [ ] **Models** (6 files, ~30 tests)
  - test_user_model.py
  - test_product_model.py
  - test_cart_model.py
  - test_order_model.py
  - test_invoice_model.py
  - test_return_model.py

- [ ] **Schemas** (6 files, ~40 tests)
  - test_user_schema.py
  - test_product_schema.py
  - test_cart_schema.py
  - test_order_schema.py
  - test_invoice_schema.py
  - test_return_schema.py

**Deliverables:**
- ✅ Working test infrastructure with PostgreSQL
- ✅ 70 unit tests for models & schemas
- ✅ 95%+ coverage for models and schemas
- ✅ Can run `pytest` and see passing tests

---

### Phase 2: Services + Repositories (Day 2 - 6-8 hours)
**Goal:** Business logic and data access tested

**Morning (3-4 hours) - Services (mocked):**
- [ ] **Services** (6 files, ~50 tests)
  - test_auth_service.py (critical - 100% coverage)
  - test_product_service.py
  - test_cart_service.py
  - test_order_service.py (critical - 100% coverage)
  - test_invoice_service.py
  - test_return_service.py

**Afternoon (3-4 hours) - Repositories + Integration:**
- [ ] **Repositories** (6 files, ~30 tests)
  - test_user_repository.py
  - test_product_repository.py
  - test_cart_repository.py
  - test_order_repository.py
  - test_invoice_repository.py
  - test_return_repository.py

- [ ] **Middleware** (1 file, ~10 tests)
  - test_auth_decorators.py (critical - 100% coverage)

**Deliverables:**
- ✅ 90 tests for services & repositories
- ✅ 90%+ coverage for auth & sales services
- ✅ 85%+ coverage for repositories
- ✅ All critical paths tested (auth, orders)

---

### Phase 3: API Tests + Utilities (Day 3 - 6-8 hours)
**Goal:** HTTP endpoints and utilities tested

**Morning (3-4 hours) - API Tests:**
- [ ] **Auth Routes** (critical)
  - test_auth_routes.py (login, register, JWT validation)
  
- [ ] **Product Routes**
  - test_product_routes.py (CRUD operations)
  
- [ ] **Sales Routes** (critical)
  - test_cart_routes.py
  - test_order_routes.py
  - test_invoice_routes.py
  - test_return_routes.py

**Afternoon (3-4 hours) - Utilities + User Routes:**
- [ ] **Utilities** (4 files, ~20 tests)
  - test_reference_data.py
  - test_security_service.py (password hashing, JWT)
  - test_cache_manager.py

- [ ] **User Routes**
  - test_user_routes.py

**Deliverables:**
- ✅ 35 API tests covering all 42 endpoints
- ✅ 20 utility tests
- ✅ 85%+ coverage for routes
- ✅ 90%+ coverage for security utilities

---

### Phase 4: E2E Tests + Polish + CI/CD (Day 4 - 4-6 hours)
**Goal:** Complete workflows, documentation, and automation

**Morning (2-3 hours) - E2E Tests:**
- [ ] **E2E Tests** (3 files, ~6 tests)
  - test_shopping_journey.py (register → browse → cart → order → invoice)
  - test_admin_workflow.py (product management → order monitoring)
  - test_return_workflow.py (return request → approval → refund)

**Afternoon (2-3 hours) - Polish & CI/CD:**
- [ ] Review coverage report - fill gaps to reach 85%
- [ ] Create test documentation (README for tests/)
- [ ] GitHub Actions workflow (.github/workflows/tests.yml)
- [ ] Pre-commit hooks setup
- [ ] Coverage badge in main README
- [ ] Final test run on clean database

**Deliverables:**
- ✅ Complete test suite (220+ tests)
- ✅ **85%+ overall coverage** achieved
- ✅ CI/CD pipeline configured and tested
- ✅ Documentation complete
- ✅ Production-ready test infrastructure

---

### Timeline Summary

```
Day 1 (6-8h): Infrastructure + Models + Schemas          → 70 tests
Day 2 (6-8h): Services + Repositories + Middleware       → 90 tests  
Day 3 (6-8h): API Tests + Utilities                      → 55 tests
Day 4 (4-6h): E2E Tests + Polish + CI/CD                 → 6 tests + coverage gaps
─────────────────────────────────────────────────────────────────────
TOTAL:       3-4 days intensive work                     → 220+ tests, 85%+ coverage
```

### Daily Checkpoints

**End of Day 1:**
- [ ] Can run `pytest` successfully
- [ ] PostgreSQL test database working
- [ ] Models & Schemas at 95%+ coverage
- [ ] ~70 passing tests

**End of Day 2:**
- [ ] Services at 90%+ coverage (auth, sales)
- [ ] Repositories at 85%+ coverage
- [ ] Auth decorators at 100% coverage
- [ ] ~160 passing tests

**End of Day 3:**
- [ ] All 42 API endpoints tested
- [ ] Routes at 85%+ coverage
- [ ] Security utilities at 90%+ coverage
- [ ] ~215 passing tests

**End of Day 4:**
- [ ] E2E workflows passing
- [ ] Overall coverage ≥ 85%
- [ ] CI/CD pipeline working
- [ ] Documentation complete
- [ ] **220+ passing tests, ready for production**

---

## 🎭 Test Categories

### Test Markers for Organization

```python
# Unit tests - fast, isolated
@pytest.mark.unit
def test_user_model_validation():
    pass

# Integration tests - database required
@pytest.mark.integration
def test_user_repository_creates_user():
    pass

# API tests - full HTTP cycle
@pytest.mark.api
def test_login_endpoint_returns_token():
    pass

# E2E tests - complete workflows
@pytest.mark.e2e
def test_complete_shopping_journey():
    pass

# Slow tests - mark for selective running
@pytest.mark.slow
def test_bulk_data_processing():
    pass

# Module-specific markers
@pytest.mark.auth
@pytest.mark.products
@pytest.mark.sales
```

### Running Tests Selectively

```bash
# Run all tests
pytest

# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run auth-related tests only
pytest -m auth

# Run everything except slow tests
pytest -m "not slow"

# Run with coverage
pytest --cov=app --cov-report=html

# Run in parallel (faster)
pytest -n auto

# Run specific file
pytest tests/unit/test_models/test_user_model.py

# Run specific test
pytest tests/unit/test_models/test_user_model.py::test_user_email_validation
```

---

## 🎪 Fixtures & Test Data

### Global Fixtures (conftest.py)

```python
import pytest
from app import create_app
from app.core.database import Base, get_engine, session_scope
from sqlalchemy_utils import database_exists, create_database, drop_database

@pytest.fixture(scope="session")
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/test_pet_ecommerce'
    return app

@pytest.fixture(scope="session")
def test_db():
    """Create PostgreSQL test database."""
    # Test database configuration
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'database': 'test_pet_ecommerce'
    }
    
    db_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    
    # Create test database if not exists
    if not database_exists(db_url):
        create_database(db_url)
    
    # Create tables
    engine = get_engine(db_url)
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup after all tests
    Base.metadata.drop_all(engine)
    drop_database(db_url)

@pytest.fixture(scope="function")
def db_session(test_db):
    """Provide database session with rollback."""
    connection = test_db.connect()
    transaction = connection.begin()
    
    with session_scope() as session:
        yield session
    
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers with JWT token."""
    response = client.post('/auth/login', json={
        'username': test_user.username,
        'password': 'password123'
    })
    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}
```

### Data Factories (fixtures/user_fixtures.py)

```python
import pytest
from faker import Faker
from app.auth.models import User, Role
from app.auth.services.security_service import hash_password

fake = Faker()

@pytest.fixture
def sample_user_data():
    """Generate sample user data."""
    return {
        'username': fake.user_name(),
        'email': fake.email(),
        'password': 'Test123!@#',
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'phone': fake.phone_number()
    }

@pytest.fixture
def test_user(db_session):
    """Create test user in database."""
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=hash_password('password123'),
        role_id=1  # Regular user
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_admin(db_session):
    """Create test admin user."""
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=hash_password('admin123'),
        role_id=2  # Admin
    )
    db_session.add(admin)
    db_session.commit()
    return admin

@pytest.fixture
def multiple_users(db_session):
    """Create multiple test users."""
    users = []
    for i in range(5):
        user = User(
            username=f'user{i}',
            email=f'user{i}@example.com',
            password_hash=hash_password('password123'),
            role_id=1
        )
        db_session.add(user)
        users.append(user)
    db_session.commit()
    return users
```

---

## 🔄 CI/CD Integration

### GitHub Actions Workflow (.github/workflows/tests.yml)

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_pet_ecommerce
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r config/requirements.txt
    
    - name: Run tests
      env:
        DB_HOST: localhost
        DB_PORT: 5432
        DB_USER: postgres
        DB_PASSWORD: postgres
        DB_NAME: test_pet_ecommerce
        JWT_SECRET_KEY: test-secret-key
      run: |
        pytest -v --cov=app --cov-report=xml --cov-report=term
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Pre-commit Hooks (.pre-commit-config.yaml)

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest -m unit
        language: system
        pass_filenames: false
        always_run: true
```

---

## 📝 Examples

### Example 1: Unit Test (Model)

```python
# tests/unit/test_models/test_user_model.py
import pytest
from app.auth.models import User

class TestUserModel:
    """Test User model validation and methods."""
    
    def test_user_creation_with_valid_data(self):
        """Test creating user with valid data."""
        # Arrange
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password_hash': 'hashed_password',
            'role_id': 1
        }
        
        # Act
        user = User(**user_data)
        
        # Assert
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.role_id == 1
    
    def test_user_repr_returns_formatted_string(self):
        """Test __repr__ method."""
        # Arrange
        user = User(
            id=1,
            username='testuser',
            email='test@example.com',
            password_hash='hashed',
            role_id=1
        )
        
        # Act
        result = repr(user)
        
        # Assert
        assert 'User' in result
        assert 'testuser' in result
        assert 'test@example.com' in result
```

### Example 2: Unit Test (Service with Mocks)

```python
# tests/unit/test_services/test_auth_service.py
import pytest
from unittest.mock import Mock, MagicMock
from app.auth.services.auth_service import AuthService
from app.auth.models import User

class TestAuthService:
    """Test AuthService business logic."""
    
    @pytest.fixture
    def mock_user_repo(self):
        """Mock UserRepository."""
        return Mock()
    
    @pytest.fixture
    def auth_service(self, mock_user_repo):
        """Create AuthService with mocked repository."""
        service = AuthService()
        service.user_repo = mock_user_repo
        return service
    
    def test_create_user_checks_duplicate_email(self, auth_service, mock_user_repo):
        """Test that create_user checks for duplicate emails."""
        # Arrange
        mock_user_repo.exists_by_email.return_value = True
        
        # Act
        user, error = auth_service.create_user(
            username='newuser',
            email='existing@example.com',
            password_hash='hashed',
            role_id=1
        )
        
        # Assert
        assert user is None
        assert error == "Email already exists"
        mock_user_repo.exists_by_email.assert_called_once_with('existing@example.com')
        mock_user_repo.create.assert_not_called()
    
    def test_create_user_success(self, auth_service, mock_user_repo):
        """Test successful user creation."""
        # Arrange
        mock_user_repo.exists_by_email.return_value = False
        mock_user_repo.exists_by_username.return_value = False
        
        created_user = User(
            id=1,
            username='newuser',
            email='new@example.com',
            password_hash='hashed',
            role_id=1
        )
        mock_user_repo.create.return_value = created_user
        
        # Act
        user, error = auth_service.create_user(
            username='newuser',
            email='new@example.com',
            password_hash='hashed',
            role_id=1
        )
        
        # Assert
        assert error is None
        assert user.username == 'newuser'
        mock_user_repo.create.assert_called_once()
```

### Example 3: Integration Test (Repository)

```python
# tests/integration/test_repositories/test_user_repository.py
import pytest
from app.auth.repositories.user_repository import UserRepository
from app.auth.models import User
from app.auth.services.security_service import hash_password

class TestUserRepository:
    """Test UserRepository database operations."""
    
    @pytest.fixture
    def user_repo(self):
        """Create UserRepository instance."""
        return UserRepository()
    
    def test_create_user_saves_to_database(self, user_repo, db_session):
        """Test creating user actually saves to database."""
        # Arrange
        user = User(
            username='dbuser',
            email='dbuser@example.com',
            password_hash=hash_password('password123'),
            role_id=1
        )
        
        # Act
        created_user = user_repo.create(user)
        db_session.commit()
        
        # Assert
        assert created_user.id is not None
        
        # Verify in database
        found_user = user_repo.get_by_username('dbuser')
        assert found_user is not None
        assert found_user.email == 'dbuser@example.com'
    
    def test_get_by_email_finds_user(self, user_repo, db_session, test_user):
        """Test finding user by email."""
        # Act
        found_user = user_repo.get_by_email(test_user.email)
        
        # Assert
        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.username == test_user.username
```

### Example 4: API Test

```python
# tests/api/test_auth_routes.py
import pytest
from flask import json

class TestAuthRoutes:
    """Test authentication endpoints."""
    
    def test_register_endpoint_creates_user(self, client):
        """Test POST /auth/register creates new user."""
        # Arrange
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'role': 'user'
        }
        
        # Act
        response = client.post(
            '/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
        assert data['user']['username'] == 'newuser'
        assert 'password' not in data['user']
    
    def test_login_endpoint_returns_jwt_token(self, client, test_user):
        """Test POST /auth/login returns JWT token."""
        # Arrange
        login_data = {
            'username': test_user.username,
            'password': 'password123'
        }
        
        # Act
        response = client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
        assert data['token_type'] == 'Bearer'
        assert data['user']['username'] == test_user.username
    
    def test_protected_endpoint_requires_authentication(self, client):
        """Test accessing protected endpoint without token fails."""
        # Act
        response = client.get('/auth/users')
        
        # Assert
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
```

### Example 5: E2E Test

```python
# tests/e2e/test_shopping_journey.py
import pytest
from flask import json

class TestShoppingJourney:
    """Test complete customer shopping workflow."""
    
    def test_complete_shopping_journey(self, client, db_session):
        """
        Test complete flow:
        1. Register user
        2. Login
        3. Browse products
        4. Add to cart
        5. Create order
        6. Verify invoice
        """
        # Step 1: Register
        register_response = client.post('/auth/register', json={
            'username': 'shopper',
            'email': 'shopper@example.com',
            'password': 'SecurePass123!',
            'role': 'user'
        })
        assert register_response.status_code == 201
        
        # Step 2: Login
        login_response = client.post('/auth/login', json={
            'username': 'shopper',
            'password': 'SecurePass123!'
        })
        assert login_response.status_code == 200
        token = login_response.get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Step 3: Browse products
        products_response = client.get('/products')
        assert products_response.status_code == 200
        products = products_response.get_json()
        assert len(products) > 0
        product_id = products[0]['id']
        
        # Step 4: Add to cart
        cart_response = client.post(
            '/sales/carts/items',
            headers=headers,
            json={'product_id': product_id, 'quantity': 2}
        )
        assert cart_response.status_code == 201
        
        # Step 5: Create order
        order_response = client.post(
            '/sales/orders',
            headers=headers
        )
        assert order_response.status_code == 201
        order_id = order_response.get_json()['id']
        
        # Step 6: Verify invoice created
        invoices_response = client.get(
            '/sales/invoices',
            headers=headers
        )
        assert invoices_response.status_code == 200
        invoices = invoices_response.get_json()
        assert len(invoices) > 0
        assert invoices[0]['order_id'] == order_id
```

---

## ✅ Summary & Next Steps

### This Proposal Provides:

1. ✅ **Complete testing strategy** for 220+ tests in **3-4 days**
2. ✅ **Organized directory structure** with clear separation
3. ✅ **Multiple testing layers** (unit, integration, API, E2E)
4. ✅ **Modern tooling** (pytest, coverage, mocking)
5. ✅ **Accelerated implementation plan** (intensive 3-4 day sprint)
6. ✅ **Concrete examples** for each test type
7. ✅ **CI/CD integration** ready
8. ✅ **85%+ coverage target** with differentiated levels (industry standard)
9. ✅ **PostgreSQL only** for test database (no SQLite)

### Approved Decisions:

✅ **Coverage Strategy:** 85% overall with differentiated targets
- Auth: 90-95% (critical security)
- Sales: 85-90% (money involved)
- Products: 80-85% (standard CRUD)
- Core: 75-80% (infrastructure)

✅ **Timeline:** 3-4 days intensive work (vs original 6 weeks)

✅ **Database:** PostgreSQL only (matching production)

### Ready to Start Implementation?

**Phase 1 (Day 1) starts with:**
1. Creating tests/ directory structure
2. Installing dependencies: `pytest pytest-cov pytest-flask faker pytest-mock sqlalchemy-utils`
3. Configuring pytest.ini with PostgreSQL
4. Setting up conftest.py with database fixtures
5. Creating first ~70 tests (models + schemas)

### Questions Remaining:

1. **Priority Module**: Should we start with Auth (most critical) or do all modules in parallel?
2. **Test Data**: Should I create realistic test fixtures or use Faker for random data?
3. **Start Time**: Ready to begin Phase 1 now, or schedule for later?

---

**🚀 Say "Let's start" and I'll begin Phase 1 implementation immediately!**
