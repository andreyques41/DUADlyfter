# 🍳 LyfterCook Backend

REST API for the LyfterCook platform - Professional chef management system.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis (optional, for caching)

### Setup Commands

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment variables
cp config/.env.example config/.env
# Edit config/.env with your values

# 4. Initialize database
# Initialize schemas and tables (non-destructive)
venv\Scripts\python.exe scripts\init_db.py

# 5. Create admin user
python scripts/seed_admin.py

# 6. Run server
venv\Scripts\python.exe run.py
```

Server runs at: `http://localhost:5000`

### Test Commands

```bash
# Unit tests
pytest tests/unit -v

# Integration tests (requires Docker)
docker compose up -d
pytest tests/integration -v
docker compose down -v

# Coverage report
pytest --cov=app --cov-report=html tests/unit
```

---

## 🧰 Helper Scripts (Recommended)

These scripts activate the venv, set environment selection, and run common workflows.

### Environments

- **Local** uses `config/.env` (`APP_ENV=local`)
- **Docker** uses `config/.env.docker` (`APP_ENV=docker`)

### Start Backend

- Local: `./scripts/start-local.ps1`
- Docker: `./scripts/start-docker.ps1`

Optional (destructive DB reset + recreate via Alembic):

- Local: `./scripts/start-local.ps1 -ResetDb`
- Docker: `./scripts/start-docker.ps1 -ResetDb`

### Run Tests

- Unit tests: `./scripts/test-unit.ps1`
- Integration tests: `./scripts/test-integration.ps1`

### Seed First Admin

Public registration (`POST /auth/register`) creates **chef** users only. To create the initial admin account:

- Local/Docker (uses current `APP_ENV` selection): `venv\Scripts\python.exe scripts\seed_admin.py`

Reads these variables from `config/.env` or `config/.env.docker`:

- `DEFAULT_ADMIN_USERNAME`
- `DEFAULT_ADMIN_EMAIL`
- `DEFAULT_ADMIN_PASSWORD`

---

## 🗄️ Database Migrations (Single Source of Truth)

LyfterCook uses **Alembic** for schema changes.

- **Reset / bootstrap (dev/test)**: `venv\Scripts\python.exe scripts\init_db.py --drop`
- **History**: `venv\Scripts\python.exe -m alembic history`

`scripts/init_db.py` is a wrapper that creates schemas and runs `alembic upgrade head`.

---

## 📚 Full Documentation

For complete documentation, see [`docs/backend/`](../docs/backend/):

- **[API Documentation](../docs/backend/API_DOCUMENTATION.md)** - 60 endpoints with examples
- **[Architecture](../docs/backend/ARCHITECTURE.md)** - Tech stack, database schema, roadmap
- **[Testing Guide](../docs/backend/TESTING_GUIDE.md)** - Detailed testing instructions (296 tests)
- **[Cache Guide](../docs/backend/CACHE_GUIDE.md)** - Redis caching implementation
- **[Admin Design](../docs/backend/ADMIN_DESIGN.md)** - Admin module architecture

---

## 🏗️ Project Structure

```
backend/
├── app/                    # Application code
│   ├── auth/              # Authentication module
│   ├── chefs/             # Chef management
│   ├── clients/           # Client management
│   ├── dishes/            # Dish management
│   ├── menus/             # Menu management
│   ├── quotations/        # Quotation system
│   ├── appointments/      # Appointment scheduling
│   ├── scrapers/          # Price scraping
│   ├── public/            # Public endpoints
│   └── admin/             # Admin module
├── config/                # Configuration files
├── scripts/               # Utility scripts
└── tests/                 # Test suites
    ├── unit/              # Unit tests (161 tests)
    └── integration/       # Integration tests (135 tests)
```

---

## 📊 Status

- ✅ **10 modules** implemented and tested
- ✅ **60 endpoints** fully functional
- ✅ **296 tests** passing (75% coverage)
- ✅ **Production-ready** backend

---

**Tech Stack:** Flask 3.0 | PostgreSQL 16 | Redis 7 | SQLAlchemy 2.0  
**Last Updated:** January 3, 2026
