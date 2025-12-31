# Testing Guide

## Status
**296 tests** (161 unit + 135 integration) | **75% coverage** | **10/10 modules validated** 

## Quick Commands

### Unit Tests
```powershell
# Run with coverage
.\venv\Scripts\python.exe -m pytest tests/unit --cov=app --cov-report=term-missing:skip-covered

# Specific module
.\venv\Scripts\python.exe -m pytest tests/unit/test_auth.py -v
```

### Integration Tests (Real HTTP)
```powershell
# 1. Setup (once)
docker compose up -d
.\venv\Scripts\python.exe scripts\init_db.py

# 2. Start server (keep terminal open)
.\venv\Scripts\python.exe run.py

# 3. Run tests (NEW terminal)
.\venv\Scripts\python.exe -m pytest tests/integration -v

# 4. Cleanup
docker compose down -v
```

 **Never run integration tests in the same terminal as the server**

## Test Organization

### Unit Tests (`tests/unit/`) - 161 tests
Fast, isolated tests with mocked dependencies:
- Auth (16), Appointments (12), Chefs (3), Clients (8)
- Dishes (14), Menus (9), Quotations (8), Scrapers (12)
- Admin (16), Public (15), Coverage tests (43)

**Database:** Local PostgreSQL `lyftercook_test`

### Integration Tests (`tests/integration/`) - 135 tests
Real HTTP tests against live server + Docker:
- CRUD: Clients (12), Dishes (16), Menus (18), Quotations (18), Appointments (17)
- APIs: Chefs (8), Public (10), Scrapers (11), Admin (20)
- Workflows: Multi-step flows (5)

**Infrastructure:** Docker PostgreSQL (5433), Redis (6380)  
**Details:** See `integration/VALIDATION_RESULTS.md` for comprehensive validation report

## Common Issues

| Problem | Solution |
|---------|----------|
| Connection refused | Server not running: `.\venv\Scripts\python.exe run.py` |
| Database does not exist | Initialize: `.\venv\Scripts\python.exe scripts\init_db.py` |
| Admin login failed | Seed admin: `.\venv\Scripts\python.exe scripts\seed_admin.py` |
| Import errors | Run from `backend/` directory |

## Configuration

**Fixtures:** `conftest.py` - auth headers, test users, DB sessions, sample data  
**Helpers:** `test_helpers.py` - assertion validators, data factories  
**Coverage:** `--cov=app` generates reports (75% currently)

---

**Updated:** Dec 31, 2025 | **Version:** 2.0.0