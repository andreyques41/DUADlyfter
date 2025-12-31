# LyfterCook Project - Workspace Scope

## ⚠️ CRITICAL: Workspace Boundaries

**This workspace contains ONLY the LyfterCook project:**
- **Root**: `c:\Users\ANDY\repos\DUADlyfter\M2_FinalProject\LyfterCook`
- **Folders**: `backend/`, `frontend/`, `docs/`, `.github/`

### DO NOT Reference Files Outside This Folder
- ❌ Parent directory: `M2_FinalProject/`
- ❌ Sibling projects in `DUADlyfter/`
- ❌ Any files outside the LyfterCook root

### Workspace Structure
```
LyfterCook/                           ← WORKSPACE ROOT (focus here)
├── .github/
│   └── copilot-instructions-*.md     ← Agent instructions
├── .vscode/
│   ├── settings.json                 ← VS Code configuration
│   └── tasks.json                    ← Build/test tasks
├── backend/                          ← Flask API
│   ├── app/                          ← Application code
│   ├── tests/                        ← Test suites
│   ├── config/                       ← Configuration
│   └── scripts/                      ← Utilities
├── frontend/                         ← Frontend code (HTML/JS)
├── docs/                             ← Documentation
└── .gitignore                        ← Git exclusions
```

---

## Agent Roles

Each agent has specialized instructions in `.github/copilot-instructions-{role}.md`:

1. **Main Agent** (`-main.md`) - Feature development, bug fixes, architecture
2. **Testing Agent** (`-testing.md`) - Test writing, coverage, validation
3. **Database Agent** (`-database.md`) - Schema, migrations, optimization
4. **Security Agent** (`-security.md`) - Auth, validation, vulnerabilities
5. **Documentation Agent** (`-documentation.md`) - API docs, technical writing
6. **Frontend Agent** (`-frontend.md`) - UI/UX, API consumption

### How to Activate an Agent
The user will use `@workspace` with context to activate a specific agent. For example:
- "As main agent, add a new endpoint"
- "As testing agent, write tests for the new endpoint"
- "As database agent, optimize this query"

---

## Project Overview

**LyfterCook** - A platform connecting chefs with clients for custom catering services.

### Tech Stack
- **Backend**: Flask 3.0 + PostgreSQL 16 + Redis 7 + SQLAlchemy 2.0
- **Frontend**: HTML/CSS/JavaScript (Vanilla JS)
- **Testing**: pytest (296 tests, 75% coverage)
- **Auth**: JWT with role-based access control
- **Architecture**: Layered (Route → Controller → Service → Repository → Model)

### Current Status (Dec 31, 2025)
- ✅ Backend: Production-ready, 10 modules, 60+ endpoints
- ✅ Database: 3 schemas (auth, core, integrations)
- ✅ Tests: All passing (161 unit + 135 integration)
- ✅ Coverage: 75%

---

## Quick Start Commands

### Development
```powershell
# Start backend server
cd backend
.\venv\Scripts\python.exe run.py

# Run unit tests
.\venv\Scripts\python.exe -m pytest tests/unit -v

# Initialize database
.\venv\Scripts\python.exe scripts\init_db.py
```

### Integration Tests (Docker Required)
```powershell
# 1. Start Docker infrastructure
docker compose up -d

# 2. Initialize test database
.\venv\Scripts\python.exe scripts\init_db.py

# 3. Start server (keep terminal open)
.\venv\Scripts\python.exe run.py

# 4. Run tests (new terminal)
.\venv\Scripts\python.exe -m pytest tests/integration -v

# 5. Cleanup
docker compose down -v
```

---

## Key Files to Read

### Architecture & Patterns
- [.github/copilot-instructions-main.md](.github/copilot-instructions-main.md) - Main agent guide
- [backend/README.md](backend/README.md) - Backend setup
- [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) - API reference

### Code Organization
- [backend/app/__init__.py](backend/app/__init__.py) - Application factory
- [backend/app/blueprints.py](backend/app/blueprints.py) - Blueprint registration
- [backend/config/settings.py](backend/config/settings.py) - Configuration

### Testing
- [tests/TESTING_GUIDE.md](backend/tests/TESTING_GUIDE.md) - Testing patterns
- [tests/conftest.py](backend/tests/conftest.py) - Shared fixtures

---

## Critical Rules for All Agents

### ✅ DO
1. **Stay within workspace boundaries** - Only reference files in LyfterCook/
2. **Follow agent-specific instructions** - Read your copilot-instructions-{role}.md
3. **Use absolute paths** - Always use full paths from workspace root
4. **Coordinate with other agents** - Know when to hand off to specialized agents
5. **Test before committing** - Verify changes don't break existing functionality

### ❌ DON'T
1. **Don't reference parent directories** - No files outside LyfterCook/
2. **Don't break agent boundaries** - Testing Agent owns tests/, Main Agent owns app/
3. **Don't skip validation** - Always validate inputs and outputs
4. **Don't modify files without understanding context** - Read related code first
5. **Don't create unnecessary files** - Only create what's needed for the task

---

## Environment

- **OS**: Windows
- **Python**: 3.11+ (via venv in `backend/venv/`)
- **Database**: PostgreSQL (local: 5432, Docker: 5433)
- **Cache**: Redis (local: 6379, Docker: 6380)
- **Server**: http://localhost:5000

---

## Documentation Index

- **API Reference**: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- **Project Plan**: [docs/architecture/PROJECT_PLAN.md](docs/architecture/PROJECT_PLAN.md)
- **Cache Design**: [docs/architecture/CACHE_IMPLEMENTATION.md](docs/architecture/CACHE_IMPLEMENTATION.md)
- **Testing Guide**: [backend/tests/TESTING_GUIDE.md](backend/tests/TESTING_GUIDE.md)

---

**Last Updated**: December 31, 2025  
**Project Status**: Production-ready backend, all modules validated
