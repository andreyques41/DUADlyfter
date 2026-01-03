# 🍳 LyfterCook Documentation

Central hub for all project documentation.

## 📁 Documentation Structure

```
docs/
├── INDEX.md                    # You are here
├── api/                        # API Reference
│   └── API_DOCUMENTATION.md    # 60 endpoints + health checks
├── architecture/               # System Design
│   ├── PROJECT_PLAN.md         # Tech stack, roadmap, database schema
│   ├── CACHE_GUIDE.md          # Complete Redis caching guide
│   └── ADMIN_ENDPOINTS_DESIGN.md # Admin module architecture
├── decisions/                  # Architectural Decision Records (ADRs)
│   └── 001_public_vs_protected_endpoints.md
└── archive/                    # Historical docs (completed phases)
    ├── SCHEMA_MIGRATION_HISTORY.md # Database setup history
    ├── ADMIN_PHASE1_COMPLETED.md
    ├── ADMIN_PHASE2_COMPLETED.md
    ├── ADMIN_PHASE3_COMPLETED.md
    ├── TYPE_STANDARDIZATION_REPORT.md
    ├── API_RESPONSE_AUDIT.md
    └── CHEF_ENDPOINTS_TESTING.md
```

---

## 🚀 Quick Links

### For API Consumers
| Document | Description |
|----------|-------------|
| [API Documentation](api/API_DOCUMENTATION.md) | Complete endpoint reference (60 routes) |
| [Backend README](../backend/README.md) | Quick start, setup instructions |

### For Developers
| Document | Description |
|----------|-------------|
| [Project Plan](architecture/PROJECT_PLAN.md) | Tech stack, roadmap, database schema |
| [Testing Guide](../backend/tests/TESTING_GUIDE.md) | How to run 326 tests |
| [Validation Results](../backend/tests/integration/VALIDATION_RESULTS.md) | Integration test details |

### System Architecture
| Document | Description |
|----------|-------------|
| [Cache Guide](architecture/CACHE_GUIDE.md) | Complete Redis caching system guide |
| [Admin Design](architecture/ADMIN_ENDPOINTS_DESIGN.md) | Admin module architecture |

### Frontend
| Document | Description |
|----------|-------------|
| [Frontend README](../frontend/README.md) | Frontend structure and setup |

---

## 📊 Project Status

| Area | Status | Details |
|------|--------|---------|
| **Backend** | ✅ Complete | 60 endpoints, 10 modules |
| **Testing** | ✅ Complete | 326 tests (191 unit + 135 integration), 80% unit-test coverage |
| **Documentation** | ✅ Complete | API, architecture, testing guides |
| **Frontend** | 🔄 In Progress | Auth pages, dashboard structure |
| **Integrations** | ⏳ Pending | PDF, Email, Calendar |

---

## 🗂️ Archive

Historical documents from completed phases are preserved in [archive/](archive/) for reference.

---

**Last Updated:** January 2, 2026
