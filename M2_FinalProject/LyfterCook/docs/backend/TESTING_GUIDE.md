# Testing Guide

## Status
**332 tests** (193 unit + 139 integration) | **80% unit-test coverage** | **10/10 modules validated**

> Counts are based on pytest's cached collection (`backend/.pytest_cache/v/cache/nodeids`).
> Coverage is based on the last generated `backend/.coverage` and `backend/htmlcov/`.

## Quick Commands

### Helper Scripts (Recommended)

From `backend/`:

```powershell
# Unit tests
./scripts/test-unit.ps1

# Integration tests (Docker)
./scripts/test-integration.ps1
```

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

# Initialize schemas and tables via Alembic (non-destructive)
.\venv\Scripts\python.exe scripts\init_db.py

# Optional: full reset (destructive)
# .\venv\Scripts\python.exe scripts\init_db.py --drop

# 2. Start server (keep terminal open)
.\venv\Scripts\python.exe run.py

# 3. Run tests (NEW terminal)
.\venv\Scripts\python.exe -m pytest tests/integration -v

# 4. Cleanup
docker compose down -v
```

 **Never run integration tests in the same terminal as the server**

## Test Organization

### Unit Tests (`tests/unit/`) - 193 tests
Fast, isolated tests with mocked dependencies:

| Test File | Tests |
|---|---:|
| tests/unit/test_admin.py | 16 |
| tests/unit/test_admin_schemas_coverage.py | 4 |
| tests/unit/test_appointments.py | 12 |
| tests/unit/test_auth.py | 18 |
| tests/unit/test_cache_decorators_coverage.py | 17 |
| tests/unit/test_chefs.py | 3 |
| tests/unit/test_clients.py | 8 |
| tests/unit/test_controller_coverage_next.py | 13 |
| tests/unit/test_dishes.py | 14 |
| tests/unit/test_hotspot_cache_manager.py | 3 |
| tests/unit/test_hotspot_chef_repo_service.py | 3 |
| tests/unit/test_hotspot_quotation_service.py | 3 |
| tests/unit/test_hotspot_scraper_service.py | 3 |
| tests/unit/test_menus.py | 9 |
| tests/unit/test_public.py | 15 |
| tests/unit/test_quotations.py | 9 |
| tests/unit/test_scraper_controller_coverage.py | 14 |
| tests/unit/test_scrapers.py | 12 |
| tests/unit/test_user_repository_coverage.py | 17 |

**Database:** Local PostgreSQL `lyftercook_test`

### Integration Tests (`tests/integration/`) - 139 tests
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
**Coverage:** `--cov=app` generates reports (~80% for the unit suite, per `backend/.coverage`)

---

**Updated:** Jan 3, 2026 | **Version:** 2.0.0