# 🍳 LyfterCook Documentation

Central hub for all project documentation - consolidated monorepo structure.

## 📁 Documentation Structure

```
docs/
├── INDEX.md                    # You are here
├── backend/                    # Backend Documentation
│   ├── API_DOCUMENTATION.md    # 60 endpoints + health checks
│   ├── ARCHITECTURE.md         # Tech stack, roadmap, database schema
│   ├── TESTING_GUIDE.md        # 497 tests, 85% unit coverage
│   ├── CACHE_GUIDE.md          # Complete Redis caching guide
│   └── ADMIN_DESIGN.md         # Admin module architecture
├── frontend/                   # Frontend Documentation
│   ├── FRONTEND_PLAN.md        # Development roadmap
│   ├── GAPS_FRONTEND_IMPLEMENTATION.md  # GAPs implementation status
│   ├── TOOLS_AND_RESOURCES.md  # Design tools & assets
│   └── VITE_GUIDE.md           # Vite configuration
├── decisions/                  # Architectural Decision Records (ADRs)
│   ├── 001_public_vs_protected_endpoints.md
│   ├── 002_monorepo_documentation_structure.md
│   └── 003_client_users_and_requirements_audit.md  # Requirements audit + action plan
└── archive/                    # Historical docs (completed phases)
    ├── SCHEMA_MIGRATION_HISTORY.md
    ├── ADMIN_PHASE1_COMPLETED.md
    ├── ADMIN_PHASE2_COMPLETED.md
    ├── ADMIN_PHASE3_COMPLETED.md
    ├── TYPE_STANDARDIZATION_REPORT.md
    ├── API_RESPONSE_AUDIT.md
    └── CHEF_ENDPOINTS_TESTING.md
```

---

## 🚀 Quick Links

### Frontend Quick Start (Vite)

```powershell
cd frontend

# Install deps (recommended, no global installs)
npx -y pnpm@10.20.0 install

# Run dev server
npx -y pnpm@10.20.0 dev
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Frontend calls backend via `/api/*` (Vite proxy in `frontend/vite.config.js`)

### For Backend Developers
| Document | Description |
|----------|-------------|
| [API Documentation](backend/API_DOCUMENTATION.md) | Complete endpoint reference (60 routes) |
| [Architecture](backend/ARCHITECTURE.md) | Tech stack, roadmap, database schema |
| [Testing Guide](backend/TESTING_GUIDE.md) | How to run 497 tests (85% unit coverage) |
| [Cache Guide](backend/CACHE_GUIDE.md) | Complete Redis caching system guide |
| [Admin Design](backend/ADMIN_DESIGN.md) | Admin module architecture |

### For Frontend Developers
| Document | Description |
|----------|-------------|
| [Frontend Plan](frontend/FRONTEND_PLAN.md) | Development roadmap & milestones |
| [GAPs Implementation](frontend/GAPS_FRONTEND_IMPLEMENTATION.md) | Frontend gaps implementation status |
| [Tools & Resources](frontend/TOOLS_AND_RESOURCES.md) | Design tools, assets, icons |
| [Vite Guide](frontend/VITE_GUIDE.md) | Vite configuration & deployment |

### For DevOps
| Document | Description |
|----------|-------------|
| [Backend Setup](../backend/README.md) | Quick start commands |
| [Frontend Setup](../frontend/README.md) | Quick start commands |
| [Integration Tests](../backend/tests/integration/VALIDATION_RESULTS.md) | Validation results |

---

## 🏛️ Architecture Decisions

| Document | Description |
|----------|-------------|
| [001: Public vs Protected Endpoints](decisions/001_public_vs_protected_endpoints.md) | API design philosophy |
| [003: Requirements Audit & Client Users](decisions/003_client_users_and_requirements_audit.md) | Requirements audit + action plan for gaps |
| [002: Monorepo Documentation Structure](decisions/002_monorepo_documentation_structure.md) | Consolidated docs organization |

---

## 📊 Project Status

| Area | Status | Details |
|------|--------|---------|
| **Backend** | ✅ Complete | 60 endpoints, 10 modules |
| **Testing** | ✅ Complete | 497 tests (358 unit + 139 integration), 85% unit coverage |
| **Documentation** | ✅ Complete | Consolidated monorepo structure, gaps implemented |
| **Integrations** | ✅ Complete | PDF, Email, Calendar (.ics export) |

---

## 📚 Additional Resources

- **Quick Start**: See [`backend/README.md`](../backend/README.md) and [`frontend/README.md`](../frontend/README.md)
- **ADRs**: Architectural decisions in [`decisions/`](decisions/)
- **Archive**: Historical documents in [`archive/`](archive/)

---

**Last Updated:** January 5, 2026  
**Structure:** Consolidated monorepo (backend/ + frontend/)
