# 🧪 Integration Tests

This directory contains integration tests that exercise multi-step workflows across
the LyfterCook backend. Each scenario uses the real Flask application, PostgreSQL test
database, and HTTP endpoints through the Flask test client.

## ✅ Current Scenarios

| File | Scenario | Modules Covered |
|------|----------|-----------------|
| `test_chef_workflows.py` | Chef creates dish → menu → client → appointment | Dishes, Menus, Clients, Appointments |
| `test_clients_crud_api.py` | Full CRUD validation against live HTTP server | Clients |

---

## 🐳 Docker-Based Validation (Recommended)

Use Docker to run Postgres + Redis in isolated containers for endpoint validation.

### Prerequisites
- Docker Desktop installed and running
- WSL 2 integration enabled (Windows)

### Step-by-Step

**1. Start Docker containers:**
```powershell
cd backend
docker compose up -d
```

**2. Verify containers are running:**
```powershell
docker ps
# Should show: lyftercook_postgres_test, lyftercook_redis_test
```

**3. Initialize the database schemas:**
```powershell
# Copy Docker env (or set env vars manually)
copy config\.env.docker config\.env.backup
copy config\.env.docker config\.env

# Run migrations/init
.\venv\Scripts\python.exe scripts\init_db.py
```

**4. Start the backend server:**
```powershell
.\venv\Scripts\python.exe run.py
# Server runs on http://localhost:5000
```

**5. Run integration tests (in another terminal):**
```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests/integration/test_clients_crud_api.py -v
```

**6. Cleanup (stop containers and delete data):**
```powershell
docker compose down -v
# Restore original .env if needed
copy config\.env.backup config\.env
```

### Docker Compose Services

| Service | Container Name | Port (Host) | Port (Container) |
|---------|----------------|-------------|------------------|
| PostgreSQL | lyftercook_postgres_test | 5433 | 5432 |
| Redis | lyftercook_redis_test | 6380 | 6379 |

Ports are offset (5433/6380) to avoid conflicts with local installations.

---

## ▶️ Running Integration Tests (Without Docker)

For tests that use the Flask test client (not HTTP), use the local test database:

```bash
# From backend directory
.\venv\Scripts\python.exe -m pytest tests/integration -m integration

# Optional: warnings-as-errors (useful for deprecation cleanup)
.\venv\Scripts\python.exe -m pytest tests/integration -m integration -W error --maxfail=1
```

Integration tests share fixtures with unit tests (see `tests/conftest.py`) so PostgreSQL
(`lyftercook_test`) must be available locally.

---

## 🗺️ Roadmap

- [x] Clients CRUD API validation
- [ ] Dishes CRUD API validation
- [ ] Menus CRUD API validation
- [ ] Quotations CRUD API validation
- [ ] Appointments CRUD API validation
- [ ] Public endpoints caching verification
- [ ] Admin supervision flows
