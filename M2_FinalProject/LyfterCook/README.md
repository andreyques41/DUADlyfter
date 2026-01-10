# CaterPro

> Professional catering platform for managing chef services, menus, and client quotations

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![Tests](https://img.shields.io/badge/Tests-497%20passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/Coverage-85%25-brightgreen.svg)]()

## 📋 Overview

LyfterCook is a **production-ready full-stack platform** designed for professional chefs to manage their services, clients, menus, and quotations. The system demonstrates enterprise-grade architecture patterns, comprehensive testing, and modern development practices.

### Problem Statement

Independent chefs and catering professionals need a centralized system to:
- Manage client relationships and appointments
- Create and price custom menus with dish compositions
- Generate accurate quotations with ingredient cost tracking
- Handle authentication and role-based access (Admin/Chef/Client)

### Solution

A layered full-stack application with:
- **RESTful API** with 60 validated endpoints
- **JWT authentication** with role-based access control
- **Modular architecture** separating concerns across 10 business modules
- **Comprehensive test suite** with 497 tests (unit + integration)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Vite + Vanilla JS)           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Auth    │ │Dashboard │ │  Menus   │ │Quotations│       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (Flask)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    ROUTES (Blueprints)               │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  CONTROLLERS (HTTP handling)         │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  SERVICES (Business logic)           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                REPOSITORIES (Data access)            │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            MODELS (SQLAlchemy ORM)                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │   PostgreSQL     │    │      Redis       │              │
│  │   (Primary DB)   │    │    (Caching)     │              │
│  └──────────────────┘    └──────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Layered architecture** | Clean separation of concerns; each layer testable in isolation |
| **Repository pattern** | Abstracts data access; enables easy DB switching and mocking |
| **Service layer** | Encapsulates business logic; keeps controllers thin |
| **Alembic migrations** | Version-controlled schema changes; safe production deployments |
| **Redis caching** | Reduces DB load for frequently accessed data |
| **JWT + bcrypt** | Stateless auth with secure password hashing |

---

## 🧰 Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.11, Flask 3.0, SQLAlchemy 2.0, Marshmallow |
| **Database** | PostgreSQL 15, Redis 7, Alembic |
| **Frontend** | Vanilla JavaScript (ES6 Modules), Vite 5, Axios |
| **Auth** | JWT (PyJWT), bcrypt |
| **Testing** | pytest, pytest-cov, Docker Compose |
| **DevOps** | Docker, GitHub Actions |

---

## 📦 Modules

| Module | Endpoints | Description |
|--------|-----------|-------------|
| `auth` | 4 | Registration, login, token refresh, password management |
| `chefs` | 6 | Chef profile CRUD, availability management |
| `clients` | 6 | Client management with contact information |
| `dishes` | 8 | Dish catalog with ingredients and pricing |
| `menus` | 8 | Menu composition from multiple dishes |
| `quotations` | 10 | Quote generation with ingredient cost aggregation |
| `appointments` | 8 | Scheduling and calendar management |
| `scrapers` | 4 | Price scraping for ingredient cost updates |
| `public` | 3 | Public endpoints (no auth required) |
| `admin` | 3 | Admin-only operations and user management |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional, for caching)
- Node.js 18+ (for frontend)

### Backend Setup

```bash
# Clone and navigate
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/.env.example config/.env
# Edit config/.env with your database credentials

# Initialize database
python scripts/init_db.py

# Create admin user
python scripts/seed_admin.py

# Run server
python run.py
```

Backend runs at: `http://localhost:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies (choose one)
pnpm install
# or
npm install
# or (no global installs; uses the repo's pinned pnpm version)
npx -y pnpm@10.20.0 install

# Start development server (choose one)
pnpm dev
# or
npm run dev
# or
npx -y pnpm@10.20.0 dev
```

Frontend runs at: `http://localhost:3000`

API calls from the frontend should use `/api/*` (Vite proxies to the backend at `http://localhost:5000` via `frontend/vite.config.js`).

---

## 🧪 Testing

```bash
# Unit tests (358 tests)
pytest tests/unit -v

# Integration tests (139 tests) - requires Docker
docker compose up -d
pytest tests/integration -v
docker compose down -v

# Coverage report
pytest --cov=app --cov-report=html tests/unit
```

### Test Coverage

Unit-test coverage is currently **85%** overall (see `backend/htmlcov/index.html` for details).

---

## 📊 Project Status

| Component | Status |
|-----------|--------|
| Backend API | ✅ Complete (60 endpoints) |
| Database Schema | ✅ Complete with migrations |
| Authentication | ✅ JWT + role-based access |
| Unit Tests | ✅ 358 tests passing |
| Integration Tests | ✅ 139 tests passing |
| Frontend Auth | ✅ Login/Register |
| Frontend Dashboard | 🔄 In Progress |
| Production Deployment | ⏳ Planned |

---

## 🎯 What This Demonstrates

### Engineering Skills
- **Clean Architecture**: Strict separation between HTTP, business logic, and data layers
- **API Design**: RESTful principles, proper status codes, consistent error handling
- **Database Design**: Normalized schema, proper relationships, schema-based organization
- **Security**: JWT authentication, password hashing, input validation

### Professional Practices
- **Testing Strategy**: Unit tests for isolation, integration tests for workflows
- **Documentation**: API docs, architecture guides, setup instructions
- **DevOps**: Docker containerization, CI configuration, environment management
- **Code Organization**: Modular structure, clear naming, consistent patterns

---

## 📚 Documentation

- [API Documentation](docs/backend/API_DOCUMENTATION.md) - 60 endpoints with examples
- [Architecture Guide](docs/backend/ARCHITECTURE.md) - Tech stack and design decisions
- [Testing Guide](docs/backend/TESTING_GUIDE.md) - Test strategy and commands
- [Cache Guide](docs/backend/CACHE_GUIDE.md) - Redis implementation details

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

*Developed as part of the Lifter Software Engineering Program (Costa Rica, 2024-2025)*
