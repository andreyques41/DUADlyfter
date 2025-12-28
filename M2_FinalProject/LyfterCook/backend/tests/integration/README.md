# 🧪 Integration Tests

This directory contains integration tests that exercise multi-step workflows across
the LyfterCook backend. Each scenario uses the real Flask application, PostgreSQL test
database, and HTTP endpoints through the Flask test client.

## ✅ Current Scenarios

| File | Scenario | Modules Covered |
|------|----------|-----------------|
| `test_chef_workflows.py` | Chef creates dish → menu → client → appointment | Dishes, Menus, Clients, Appointments |

## ▶️ Running Integration Tests

```bash
# From backend directory
.\venv\Scripts\python.exe -m pytest tests/integration -m integration

# Optional: warnings-as-errors (useful for deprecation cleanup)
.\venv\Scripts\python.exe -m pytest tests/integration -m integration -W error --maxfail=1
```

Integration tests share fixtures with unit tests (see `tests/conftest.py`) so PostgreSQL
(`lyftercook_test`) must be available locally.

## 🗺️ Roadmap

- Menu + quotation workflow
- Public endpoints caching verification
- Admin supervision flows
