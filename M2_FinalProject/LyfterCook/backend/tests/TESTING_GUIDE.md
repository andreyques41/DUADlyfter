# Testing Suite - LyfterCook Backend

## 📋 Overview

Comprehensive test suite for the LyfterCook backend API using pytest. Tests all 10 modules with 60 endpoints total.

## 🧪 Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── setup_test_db.py         # PostgreSQL test DB setup script
├── TESTING_GUIDE.md         # This file
├── pytest.ini               # Pytest configuration (in backend/)
├── unit/                    # ✅ Unit tests (110 tests - 100%)
│   ├── README.md            # Unit tests documentation
│   ├── test_helpers.py      # Helper functions and utilities
│   ├── test_auth.py         # Auth module tests (16 tests)
│   ├── test_appointments.py # Appointment tests (12 tests)
│   ├── test_chefs.py        # Chef module tests (3 tests)
│   ├── test_clients.py      # Client module tests (8 tests)
│   ├── test_dishes.py       # Dish module tests (14 tests)
│   ├── test_menus.py        # Menu module tests (9 tests)
│   ├── test_quotations.py   # Quotation module tests (8 tests)
│   ├── test_scrapers.py     # Scraper module tests (12 tests)
│   ├── test_admin.py        # Admin + middleware tests (16 tests)
│   └── test_public.py       # Public module tests (15 tests)
└── integration/             # ✅ Integration tests (initial workflows)
    ├── README.md            # Integration tests documentation
    └── test_chef_workflows.py # Chef multi-step workflow test
```

## 🚀 Running Tests

### Run All Tests
```bash
# Activate virtual environment
.\venv\Scripts\python.exe -m pytest

# Unit tests only
.\venv\Scripts\python.exe -m pytest tests/unit/ -v

# With verbose output
.\venv\Scripts\python.exe -m pytest tests/unit/ -v

# With coverage report
.\venv\Scripts\python.exe -m pytest tests/unit/ --cov=app --cov-report=html
```

### Run Specific Module Tests
```bash
# Auth module only
.\venv\Scripts\python.exe -m pytest tests/unit/test_auth.py -v

# Chef module only
.\venv\Scripts\python.exe -m pytest tests/unit/test_chefs.py -v

# Public module only
.\venv\Scripts\python.exe -m pytest tests/unit/test_public.py -v
```

### Run Tests by Marker
```bash
# Run only auth tests
.\venv\Scripts\python.exe -m pytest -m auth

# Run only public tests
.\venv\Scripts\python.exe -m pytest -m public

# Run integration tests
.\venv\Scripts\python.exe -m pytest -m integration
```

### Run Specific Test Class or Function
```bash
# Run specific test class
.\venv\Scripts\python.exe -m pytest tests/unit/test_auth.py::TestAuthLogin -v

# Run specific test function
.\venv\Scripts\python.exe -m pytest tests/unit/test_auth.py::TestAuthLogin::test_login_success -v
```

## 🔧 Test Configuration

### Database
- Uses **PostgreSQL test database** (`lyftercook_test`)
- Supports PostgreSQL schemas (auth, core, integrations)
- Each test gets fresh database session
- Automatic rollback after each test
- No persistent data between tests

**Important:** Make sure PostgreSQL is running and `lyftercook_test` database exists before running tests.

### Authentication
- JWT tokens generated automatically via fixtures
- `auth_headers` - Admin user headers
- `chef_headers` - Chef user headers
- `client_headers` - Client user headers

### Fixtures Available
- `app` - Flask application instance
- `client` - Flask test client
- `db_session` - Database session (auto-rollback)
- `test_user` - Admin user
- `test_chef_user` - Chef user with profile
- `test_client_user` - Client user with profile
- `test_chef` - Chef profile
- `test_client_profile` - Client profile
- `test_dish` - Sample dish with ingredients
- `test_menu` - Sample menu
- `test_quotation` - Sample quotation
- `test_appointment` - Sample appointment
- `test_price_source` - Sample price source

## 📊 Test Coverage

### Module Coverage Status

| Module | Tests | Endpoints Covered | Status |
|--------|-------|-------------------|--------|
| Auth | 16 | 3/3 | ✅ Complete |
| Appointments | 12 | 6/6 | ✅ Complete |
| Chefs | 3 | 5/5 | ✅ Complete |
| Clients | 8 | 5/5 | ✅ Complete |
| Dishes | 10 | 5/5 | ✅ Complete |
| Menus | 9 | 6/6 | ✅ Complete |
| Quotations | 6 | 6/6 | ✅ Complete (1 skipped) |
| Scrapers | 14 | 9/9 | ✅ Complete |
| Public | 15 | 6/6 | ✅ Complete |

**Total: 93 tests covering 53 endpoints (100% passing)**

## 🎯 Test Categories

### 1. **Auth Module** (`test_auth.py`)
- User registration (chef/client roles)
- Login with password validation
- Token refresh mechanism
- JWT authentication middleware
- Invalid credentials handling
- Expired token handling

### 2. **Chef Module** (`test_chefs.py`)
- Chef profile CRUD
- Search by specialty/location
- Pagination
- Authorization checks

### 3. **Client Module** (`test_clients.py`)
- Client profile CRUD
- Dietary preferences
- Address management

### 4. **Dish Module** (`test_dishes.py`)
- Dish CRUD with ingredients
- Availability toggle
- Category filtering
- Price management

### 5. **Menu Module** (`test_menus.py`)
- Menu CRUD
- Dish associations
- Status workflow (active/inactive)
- Order positioning

### 6. **Quotation Module** (`test_quotations.py`)
- Quotation CRUD
- Status workflow (pending/approved/rejected)
- Price calculations
- Event management

### 7. **Appointment Module** (`test_appointments.py`)
- Appointment scheduling
- Rescheduling
- Status updates
- Cancellation

### 8. **Scraper Module** (`test_scrapers.py`)
- Price source management
- Web scraping operations
- Price comparison
- Cached prices
- Cleanup old data

### 9. **Public Module** (`test_public.py`)
- Public chef listing (no auth)
- Search functionality
- Filters (specialty/location)
- Chef profiles with dishes/menus
- Menu details
- Dish details

## 🛠️ Helper Functions

### Response Validators
```python
from tests.unit.test_helpers import (
    assert_success_response,
    assert_error_response,
    assert_validation_error,
    assert_unauthorized_error,
    assert_not_found_error
)
```

### Data Validators
```python
from tests.unit.test_helpers import ResponseValidator

ResponseValidator.validate_pagination(data)
ResponseValidator.validate_chef_response(chef)
ResponseValidator.validate_dish_response(dish)
ResponseValidator.validate_menu_response(menu)
```

### Test Data Factories
```python
from tests.unit.test_helpers import (
    create_test_user,
    create_test_chef,
    create_test_client,
    create_test_dish,
    create_test_menu
)
```

## 🌉 Integration Tests

- **Scenario:** `tests/integration/test_chef_workflows.py` validates a full chef workflow  
  (dish → menu assignment → client → appointment) with the real HTTP layer.
- **Markers:** Use `pytest -m integration` to run only integration scenarios.
- **Dependencies:** Requires the PostgreSQL `lyftercook_test` database and the same fixtures
  used by unit tests. See `tests/integration/README.md` for details and roadmap.

## 📈 Coverage Reports

### Generate HTML Coverage Report
```bash
.\venv\Scripts\python.exe -m pytest --cov=app --cov-report=html
```

Open `htmlcov/index.html` in browser to view detailed coverage.

### Generate Terminal Coverage Report
```bash
.\venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing
```

## 🔍 Debugging Tests

### Run with Print Statements
```bash
.\venv\Scripts\python.exe -m pytest -s tests/unit/test_auth.py
```

### Run Last Failed Tests
```bash
.\venv\Scripts\python.exe -m pytest --lf
```

### Run with PDB Debugger
```bash
.\venv\Scripts\python.exe -m pytest --pdb
```

### Verbose Output
```bash
.\venv\Scripts\python.exe -m pytest -vv
```

## ✅ Best Practices

1. **Test Isolation**: Each test is independent and doesn't affect others
2. **Fixtures**: Use fixtures for common setup/teardown
3. **Assertions**: Use helper functions for consistent assertions
4. **Naming**: Test names clearly describe what they test
5. **Coverage**: Aim for >80% code coverage
6. **Speed**: In-memory database keeps tests fast
7. **Mocking**: Mock external services (email, Cloudinary, etc.)

## 🚨 Common Issues

### Import Errors
Make sure you're running from backend directory:
```bash
cd C:\Users\ANDY\repos\DUADlyfter\M2_FinalProject\LyfterCook\backend
```

### Database Errors
Tests use PostgreSQL `lyftercook_test` database. Make sure:
1. PostgreSQL is running
2. Database `lyftercook_test` exists: `createdb lyftercook_test`
3. User `postgres` has access with password `postgres`

### Token Errors
Use provided fixtures (`auth_headers`, `chef_headers`, `client_headers`).

## 📝 Adding New Tests

1. Create test file in `tests/unit/`: `test_yourmodule.py`
2. Import helpers: `from tests.unit.test_helpers import *`
3. Create test class: `class TestYourFeature:`
4. Add test methods: `def test_your_case(self, client, fixtures):`
5. Run tests: `.\venv\Scripts\python.exe -m pytest tests/unit/test_yourmodule.py`

## 🎓 Example Test

```python
def test_create_chef_success(self, client, chef_headers):
    """Test successful chef creation."""
    data = {
        'name': 'New Chef',
        'specialty': 'Italian Cuisine',
        'location': 'Miami, FL'
    }
    
    response = client.post('/chefs', json=data, headers=chef_headers)
    
    result = assert_success_response(response, 201)
    assert result['data']['name'] == 'New Chef'
```

## 📞 Support

For issues or questions about testing:
1. Check this guide
2. Review unit tests: `tests/unit/README.md`
3. Review integration tests: `tests/integration/README.md`
4. Check pytest documentation: https://docs.pytest.org/

---

**Last Updated:** December 27, 2025  
**Test Suite Version:** 1.1.0  
**Total Tests:** 100+  
**Total Endpoints:** 53  
**Pass Rate:** 100%
