# 🌐 Integration Tests

Integration tests validate **real HTTP endpoints** against a live backend server with isolated Docker infrastructure (Postgres + Redis).

## 📊 Current Status

**135 integration tests** covering 10 modules:

| Module | Tests | Status |
|--------|-------|--------|
| Clients | 12 | ✅ Validated |
| Dishes | 16 | ✅ Validated |
| Menus | 18 | ✅ Validated |
| Quotations | 18 | ✅ Validated |
| Appointments | 17 | ✅ Validated |
| Chefs | 8 | ✅ Validated |
| Public API | 10 | ✅ Validated |
| Scrapers | 11 | ✅ Validated |
| Admin | 20 | ✅ Validated |
| Workflows | 5 | ✅ Validated |

**See `VALIDATION_RESULTS.md` for detailed validation reports per module.**

---

## � Quick Start

### Prerequisites
- Docker Desktop installed and running
- Python virtual environment activated

### Running Integration Tests

```powershell
# 1. Start isolated Docker infrastructure
docker compose up -d

# 2. Verify containers are running
docker ps
# Should show: postgres (5433) and redis (6380)

# 3. Initialize database schemas
.\venv\Scripts\python.exe scripts\init_db.py

# 4. Start backend server (KEEP THIS TERMINAL OPEN)
.\venv\Scripts\python.exe run.py
# Server: http://localhost:5000

# 5. Open NEW terminal and run integration tests
.\venv\Scripts\python.exe -m pytest tests/integration -v

# Or run specific module
.\venv\Scripts\python.exe -m pytest tests/integration/test_clients_crud_api.py -v

# 6. Cleanup when done
docker compose down -v
```

### 🐳 Docker Infrastructure

| Service | Port | Database/Config |
|---------|------|-----------------|
| PostgreSQL 16 | 5433 → 5432 | `lyftercook_docker` |
| Redis 7 | 6380 → 6379 | `testredispassword` |

**Note:** Ports are offset to avoid conflicts with local installations.

### ⚠️ Important Rules

1. **Never run tests in the server terminal** - Tests need the server running separately
2. **Use Docker for integration tests** - Provides isolated, reproducible environment
3. **Clean up after testing** - `docker compose down -v` removes all test data

---

## 📝 What Gets Validated

Each integration test validates:

✅ **HTTP Contracts:** Real requests/responses match API documentation  
✅ **Status Codes:** Correct codes for success (200/201), errors (400/404), auth (401/403)  
✅ **Response Structures:** JSON envelopes, nested objects, field types  
✅ **CRUD Lifecycle:** Create → Read → Update → Delete workflows  
✅ **Error Handling:** Validation errors with `details`, not-found errors  
✅ **Authentication:** JWT required, RBAC enforcement  
✅ **Caching:** Cache-Control headers, Redis integration  
✅ **Business Logic:** Status transitions, calculated fields, cascade deletes

## 🔍 Validation Report

Detailed validation results for each module (status codes, behaviors, data structures, bugs fixed) are documented in:

📄 **`VALIDATION_RESULTS.md`** (comprehensive report, ~500 lines)

## 💡 Tips

- **Faster feedback:** Run single module tests during development
- **Fresh state:** Use `docker compose down -v` to reset database between runs
- **Debug failures:** Check server terminal for backend errors
- **Admin tests:** Default admin is auto-seeded if missing (username: `admin`, password: `Admin123!@#`)
