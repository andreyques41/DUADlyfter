# 🍳 LyfterCook - Development Plan

## 📋 Tech Stack

### Backend
- **Framework**: Flask 3.1+
- **Database**: PostgreSQL + SQLAlchemy 2.0
- **Auth**: OAuth2 + JWT (PyJWT + bcrypt)
- **PDF**: WeasyPrint (HTML/CSS → PDF)
- **Email**: SendGrid API
- **Images**: Cloudinary SDK
- **Validation**: Marshmallow
- **Testing**: pytest + coverage
- **Scraping**: BeautifulSoup4 + requests (supermarket scraper)
- **Scheduling**: Calendly API / Google Calendar API

### Frontend
- **Framework**: Vanilla JavaScript (ES6 Modules)
- **HTTP**: Axios
- **Styles**: CSS3 (modular)
- **Storage**: LocalStorage + API
- **Upload**: Cloudinary Widget

### DevOps
- **Cache**: Redis (optional for optimization)
- **Variables**: python-dotenv
- **CORS**: flask-cors

---

## 🗄️ Database

### Multi-Schema Organization

**Schema `auth`** - Authentication and users

**1. auth.users**
- id, username, email, password_hash, role (chef/admin), profile_photo_url
- created_at, updated_at

**Schema `core`** - Main business logic

**2. core.chefs**
- id, user_id (FK → auth.users), bio, specialty, phone, location, is_active
- created_at, updated_at

**3. core.clients**
- id, chef_id (FK → core.chefs), name, email, phone, company, notes
- created_at, updated_at

**4. core.dishes**
- id, chef_id (FK → core.chefs), name, description, price, category
- preparation_steps, prep_time, servings
- photo_url, is_active, created_at, updated_at

**5. core.ingredients**
- id, dish_id (FK → core.dishes), name, quantity, unit, is_optional
- created_at, updated_at

**6. core.menus**
- id, chef_id (FK → core.chefs), name, description, status (active/inactive)
- created_at, updated_at

**7. core.menu_dishes** (many-to-many)
- menu_id (FK → core.menus), dish_id (FK → core.dishes), order_position

**8. core.quotations**
- id, chef_id (FK → core.chefs), client_id (FK → core.clients), menu_id (FK → core.menus, nullable)
- quotation_number, total_amount, status (draft/sent/accepted/rejected)
- valid_until, notes, pdf_url
- created_at, sent_at, updated_at

**9. core.quotation_items** (additional items without menu)
- id, quotation_id (FK → core.quotations), description, quantity, unit_price, subtotal

**Schema `integrations`** - External services

**10. integrations.appointments**
- id, chef_id (FK → core.chefs), client_id (FK → core.clients, nullable)
- client_name, client_email, client_phone
- appointment_date, appointment_time, duration_minutes, status (pending/confirmed/cancelled)
- calendly_event_id, google_event_id, notes
- created_at, updated_at

**11. integrations.scraped_products** (cached product data)
- id, ingredient_name, store_name, product_name, price, url, image_url
- last_scraped_at, created_at

### Cross-Schema Relationships
- auth.users (1) ←→ (1) core.chefs
- core.chefs (1) → (N) core.clients
- core.chefs (1) → (N) core.dishes
- core.chefs (1) → (N) core.menus
- core.chefs (1) → (N) core.quotations
- core.chefs (1) → (N) integrations.appointments
- core.menus (N) ←→ (N) core.dishes (through core.menu_dishes)
- core.quotations (N) → (1) core.menus (optional)
- core.quotations (1) → (N) core.quotation_items
- core.dishes (1) → (N) core.ingredients
- core.clients (1) → (N) integrations.appointments

### Multi-Schema Organization Benefits
- **Clarity**: Logical separation of modules
- **Security**: Granular permissions per schema
- **Scalability**: Easy to add new modules/schemas
- **Maintainability**: More organized migrations

---

## 🏗️ Backend Architecture

### Pattern: 3-Tier Layered Architecture

```
┌─────────────────────────────────────┐
│   PRESENTATION LAYER                │ ← Routes, Controllers
├─────────────────────────────────────┤
│   BUSINESS LOGIC LAYER              │ ← Services
├─────────────────────────────────────┤
│   DATA ACCESS LAYER                 │ ← Repositories, Models
└─────────────────────────────────────┘
```

### Layer Responsibilities

#### **Routes Layer** (`routes/`)
- Blueprint registration and route definition
- Authentication decorators (@admin_required, @jwt_required)
- Delegation to controllers
- **NO** business logic

#### **Controllers Layer** (`controllers/`)
- HTTP request/response handling
- Schema validation (Marshmallow)
- JSON response formatting
- HTTP error handling
- Delegation to services
- **NO** direct database access

#### **Services Layer** (`services/`)
- Business logic
- Operation orchestration
- Complex validations
- Cache management (Redis)
- Delegation to repositories
- **NO** direct HTTP handling

#### **Repositories Layer** (`repositories/`)
- CRUD database operations
- SQLAlchemy queries
- Transactions
- **ONLY** data access, no business logic

#### **Models Layer** (`models/`)
- Table definitions (SQLAlchemy ORM)
- Model relationships
- Enums and constraints

#### **Schemas Layer** (`schemas/`)
- Input validation (Marshmallow)
- Serialization/deserialization
- Request and response schemas

---

## 📁 Project Structure

```
LyfterCook/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── blueprints.py           # Blueprint registration
│   │   │
│   │   ├── auth/                   # Authentication module
│   │   │   ├── __init__.py
│   │   │   ├── models/
│   │   │   │   └── user_model.py
│   │   │   ├── schemas/
│   │   │   │   └── user_schema.py
│   │   │   ├── repositories/
│   │   │   │   └── user_repository.py
│   │   │   ├── services/
│   │   │   │   ├── auth_service.py
│   │   │   │   └── security_service.py
│   │   │   ├── controllers/
│   │   │   │   └── auth_controller.py
│   │   │   └── routes/
│   │   │       └── auth_routes.py
│   │   │
│   │   ├── chefs/                  # Chef profiles
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── repositories/
│   │   │   ├── services/
│   │   │   ├── controllers/
│   │   │   └── routes/
│   │   │
│   │   ├── clients/                # Client management
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── repositories/
│   │   │   ├── services/
│   │   │   ├── controllers/
│   │   │   └── routes/
│   │   │
│   │   ├── dishes/                 # Dish CRUD
│   │   ├── menus/                  # Menu CRUD
│   │   ├── quotations/             # Quotations + PDF
│   │   ├── appointments/           # Calendar scheduling
│   │   ├── scraper/                # Product scraper service
│   │   ├── public/                 # Landing + chef profiles (no auth)
│   │   │
│   │   └── core/                   # Shared infrastructure
│   │       ├── database.py         # SQLAlchemy setup
│   │       ├── cache_manager.py    # Redis cache (optional)
│   │       ├── middleware/         # JWT decorators, RBAC
│   │       │   ├── auth_middleware.py
│   │       │   └── cache_decorators.py
│   │       └── lib/                # Utilities
│   │           ├── error_utils.py
│   │           ├── jwt_utils.py
│   │           └── validators.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── logging.py
│   │   └── .env
│   │
│   ├── scripts/
│   │   ├── init_db.py
│   │   └── run_tests.py
│   │
│   ├── tests/
│   │   ├── unit/                   # Tests per layer
│   │   │   ├── test_models/
│   │   │   ├── test_repositories/
│   │   │   ├── test_services/
│   │   │   └── test_controllers/
│   │   └── integration/            # Endpoint tests
│   │       └── test_routes/
│   │
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── index.html         # Landing page
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard/
│   │   ├── clients.html
│   │   ├── dishes.html
│   │   ├── menus.html
│   │   ├── quotations.html
│   │   └── appointments.html
│   ├── public/
│   │   ├── chefs.html     # Chef list
│   │   └── chef-profile.html
│   ├── scripts/
│   │   ├── core/          # Config, auth, session
│   │   ├── services/      # API calls
│   │   ├── components/    # UI reusables
│   │   └── views/         # Page logic
│   ├── styles/
│   └── assets/
│
└── docs/
    ├── API_ROUTES.md
    ├── DATABASE_SCHEMA.md
    └── DEVELOPMENT_PHASES.md
```

---

## 📐 Flow Example (Auth Module)

### File structure:
```python
app/auth/
├── models/
│   └── user_model.py          # User ORM model
├── schemas/
│   └── user_schema.py         # UserRegisterSchema, UserLoginSchema
├── repositories/
│   └── user_repository.py     # get_by_email(), create(), etc.
├── services/
│   ├── auth_service.py        # register_user(), authenticate_user()
│   └── security_service.py    # hash_password(), verify_password()
├── controllers/
│   └── auth_controller.py     # HTTP handling, response formatting
└── routes/
    └── auth_routes.py         # Blueprint registration
```

### Execution flow:
```
1. REQUEST:  POST /auth/register
             ↓
2. ROUTE:    auth_routes.py → AuthAPI.post()
             ↓
3. CONTROLLER: AuthController.register()
             - Validates with UserRegisterSchema
             - Extracts request data
             ↓
4. SERVICE:  AuthService.register_user()
             - Verifies unique email
             - Hash password (SecurityService)
             - Orchestrates User + Chef creation
             ↓
5. REPOSITORY: UserRepository.create()
             - db.add(user)
             - db.commit()
             ↓
6. RESPONSE: Controller formats response
             - UserResponseSchema.dump(user)
             - return jsonify(...), 201
```

---

## 🎯 Development Phases

### **Phase 1: Foundation (Week 1-2)** ✅ COMPLETED
1. ✅ Initial setup (repos, venv, DB)
2. ✅ Create PostgreSQL multi-schema
3. ✅ SQLAlchemy models (11 tables)
4. ⏳ Backend: Auth (register, login, JWT)
5. ⏳ Frontend: Login/Register pages
6. ⏳ Protected routes middleware

### **Phase 2: Base Management (Week 3-4)**
1. Backend: Clients CRUD
2. Backend: Dishes CRUD + Cloudinary upload
3. Frontend: Clients page (table + forms)
4. Frontend: Dishes page (cards + upload)

### **Phase 3: Menus (Week 5)**
1. Backend: Menus CRUD + dish assignment
2. Frontend: Menu builder (optional drag & drop)
3. Active/Inactive status toggle

### **Phase 4: Quotations (Week 6-7)**
1. Backend: Quotations CRUD
2. Backend: PDF generation (WeasyPrint)
3. Backend: SendGrid email integration
4. Frontend: Quotation form + preview

### **Phase 5: Advanced Features (Week 8-9)**
1. Backend: Ingredients model + scraper service
2. Backend: Web scraping (BeautifulSoup) - supermarkets
3. Frontend: Ingredient search + price comparison
4. Backend: Appointments CRUD + Calendly/Google Calendar API
5. Frontend: Calendar widget + booking system

### **Phase 6: Public (Week 10)**
1. Landing page (chef list)
2. Chef profile page (public)
3. Contact form + booking integration
4. Basic SEO

### **Phase 7: Polish (Week 11)**
1. Testing (pytest backend, manual frontend)
2. Error handling refinement
3. UI/UX improvements
4. Documentation

---

## 🔑 API Endpoints (Summary)

### Auth
- POST /auth/register
- POST /auth/login
- GET /auth/me

### Chefs
- GET /chefs (public)
- GET /chefs/:id (public)
- PUT /chefs/profile
- PATCH /chefs/photo

### Clients (protected)
- GET /clients
- POST /clients
- PUT /clients/:id
- DELETE /clients/:id

### Dishes (protected)
- GET /dishes
- POST /dishes (+ upload)
- PUT /dishes/:id
- DELETE /dishes/:id

### Menus (protected)
- GET /menus
- POST /menus
- PUT /menus/:id
- PATCH /menus/:id/status
- POST /menus/:id/dishes

### Quotations (protected)
- GET /quotations
- POST /quotations
- PUT /quotations/:id
- POST /quotations/:id/send (generate PDF + email)
- GET /quotations/:id/pdf

### Appointments (protected chef, public booking)
- GET /appointments
- POST /appointments
- PUT /appointments/:id
- PATCH /appointments/:id/status
- POST /appointments/calendly-webhook
- GET /appointments/availability

### Scraper (protected)
- POST /scraper/search (search ingredients)
- GET /scraper/products/:ingredient_id

### Public
- GET /public/chefs (landing)
- GET /public/chefs/:id (profile)
- POST /public/contact
- POST /public/appointments (public booking)

---

## 🔐 Security

### Authentication and Authorization
- **Passwords**: bcrypt (12 rounds)
- **JWT tokens**: HS256, 24h expiration
- **Refresh tokens**: 7 days (optional)
- **Middleware**: @jwt_required, @admin_required decorators
- **RBAC**: Role-based access control (CHEF, ADMIN)

### Validation and Sanitization
- **Input validation**: Marshmallow schemas
- **SQL injection**: SQLAlchemy ORM (prepared statements)
- **XSS protection**: Input sanitization
- **CSRF**: Token validation (for forms)

### Infrastructure
- **CORS**: flask-cors with domain whitelist
- **Rate limiting**: flask-limiter (optional)
- **File uploads**: Validate type/size with Cloudinary
- **HTTPS**: Required in production

---

## 🛒 Feature: Supermarket Scraper

**Supported supermarkets** (initially):
- Walmart (basic scraping)
- Optional: Amazon Fresh, local markets

**Flow**:
1. Chef adds ingredients to a dish
2. Scraper system searches prices in supermarkets
3. Shows price comparison
4. Direct links to products

**Implementation**:
- BeautifulSoup4 for HTML parsing
- requests-html for JS rendering (optional)
- DB cache (24-48h) to avoid spam
- Request rate limiting
- User-Agent rotation to avoid blocking

## 📅 Feature: Appointment System

**Calendly API** ✅ (Selected)
- Easy integration
- Professional embed UI
- Time zone handling
- Automatic confirmations
- Free tier available
- Webhooks for synchronization

**Flow**:
1. Chef configures availability
2. Public client schedules session
3. Automatic confirmation via email
4. Bidirectional calendar sync

## 📊 Optional Improvements (Post-MVP)

- [ ] Dashboard analytics
- [ ] In-app notifications
- [ ] Multi-language (i18n)
- [ ] Dark mode
- [ ] PWA capabilities
- [ ] Export CSV/Excel
- [ ] Quotation templates
- [ ] Review system
- [ ] More supermarket scraping
- [ ] Automatic appointment reminders

---

## 🚀 Quick Commands

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py

# Frontend
cd frontend
# Open with Live Server or serve with:
python -m http.server 8080

# Database
psql -U postgres
CREATE DATABASE lyftercook;

# Initialize schemas and tables
cd backend
python scripts\init_db.py
```

---

## ⚠️ Technical Considerations

### Scraper
- **Legal**: Verify supermarket terms of service
- **Rate limiting**: Max 10 requests/min per supermarket
- **Cache**: 24-48h to reduce load
- **Fallback**: If scraper fails, show generic message
- **Async**: Use background jobs (Celery optional)

### Calendar
- **Calendly**: Requires account (free tier sufficient)
- **Google Calendar**: More complex OAuth2
- **Time zones**: Handle correctly (UTC + conversion)
- **Conflicts**: Validate availability before confirming

## 🧪 Testing Strategy

### Unit Tests (per layer)
```python
# test_user_repository.py
def test_get_by_email():
    user = user_repo.get_by_email("test@example.com")
    assert user.email == "test@example.com"

# test_auth_service.py
def test_register_user_success():
    user = auth_service.register_user("john", "john@example.com", "pass123")
    assert user.username == "john"

# test_auth_controller.py
def test_register_endpoint(client):
    response = client.post('/auth/register', json={...})
    assert response.status_code == 201
```

### Integration Tests
- Full endpoint tests (request → response)
- Business flow tests (create complete order)
- External integration tests (mocked)

### Coverage Targets
- **Repositories**: 90%+
- **Services**: 85%+
- **Controllers**: 80%+
- **Overall**: 80%+

---

## 🚀 Implemented Best Practices

### Dependency Injection
```python
# Services receive dependencies in __init__
class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

# In controller
auth_service = AuthService(UserRepository())
```

### Centralized Error Handling
```python
# app/core/lib/error_utils.py
def error_response(message, status_code):
    return jsonify({"error": message}), status_code

# In controller
try:
    user = auth_service.register_user(...)
except ValueError as e:
    return error_response(str(e), 400)
```

### Consistent Logging
```python
from config.logging import get_logger
logger = get_logger(__name__)

logger.info(f"User {user.username} registered successfully")
logger.error(f"Failed to create user: {e}", exc_info=True)
```

### Cache Management (optional)
```python
from app.core.cache_manager import get_cache

cache = get_cache()
cache.store_data("product:123", product_data, ttl=3600)
```

---

## 📝 Immediate Next Steps

### 1. Complete Auth Module (Phase 1)
- [x] Models (User) - ✅ Completed
- [ ] Schemas (UserRegisterSchema, UserLoginSchema)
- [ ] Repositories (UserRepository)
- [ ] Services (AuthService, SecurityService)
- [ ] Controllers (AuthController)
- [ ] Routes (auth_routes.py)
- [ ] Middleware (jwt_required decorator)
- [ ] Unit tests

### 2. External Services Setup
- [ ] Create Cloudinary account
- [ ] Create SendGrid account
- [ ] Configure API keys in .env
- [ ] Decide: Calendly vs Google Calendar

### 3. Frontend Base
- [ ] Login page (HTML + CSS)
- [ ] Register page
- [ ] JWT token handling in LocalStorage
- [ ] Axios config with interceptors

**🎯 Immediate Goal: Complete functional authentication (register + login) in 2-3 days**

---

## 🔒 Production Security Strategy

### Admin Account Management

#### Development Environment
- Use `seed_admin.py` script with `.env` credentials
- Default credentials acceptable for local testing
- Focus on rapid development iteration

#### Staging Environment
- Run seed script **once** during initial setup
- Immediately change password after first login
- Add second admin account as backup
- Test credential recovery procedures

#### Production Environment
**Initial Setup:**
1. Run seed script with strong credentials
2. Store credentials in secure vault (LastPass, 1Password, etc.)
3. Change password immediately after first login
4. Create 2-3 additional admin accounts
5. **Delete seed script from production server**

**Required Security Features:**
- ✅ Public registration creates only CHEF users (role parameter ignored)
- ⏳ Email-based password recovery system
- ⏳ Recovery codes (backup 2FA codes)
- ⏳ Admin-only endpoint to create additional admins
- ⏳ Multi-factor authentication (MFA) for admin accounts
- ⏳ Audit logging for all admin actions

### Credential Recovery Chain

**Priority order when admin credentials are lost:**

1. **Email Recovery** (Primary)
   - POST /auth/forgot-password endpoint
   - Time-limited reset token (15-30 minutes)
   - Secure email delivery via SendGrid
   - Rate limiting to prevent abuse

2. **Recovery Codes** (Backup)
   - One-time use backup codes
   - Generated during admin creation
   - Stored securely by admin (printed/vault)
   - Can bypass email requirement

3. **Another Admin** (Fallback)
   - Multiple admin accounts reduce single point of failure
   - Admins can reset each other's passwords
   - Requires admin-only password reset endpoint

4. **Database Access** (Last Resort)
   - Direct database manipulation
   - Hash new password manually
   - Requires infrastructure access (DevOps/DB admin)
   - Should be documented but rarely used

### Attack Prevention Measures

**Currently Implemented:**
- ✅ Role parameter ignored in public registration
- ✅ Role hardcoded to CHEF in `auth_service.py`
- ✅ Seed script uses environment variables

**Production Requirements:**
- ⏳ Remove seed script from production deployment
- ⏳ MFA for all admin accounts
- ⏳ IP whitelisting for admin endpoints (optional)
- ⏳ Rate limiting on all auth endpoints
- ⏳ Audit logs for admin actions (who, what, when, IP)
- ⏳ Failed login attempt monitoring
- ⏳ Automated alerts for suspicious admin activity

### Industry Standards Reference

**Patterns researched:**
- **Django**: `createsuperuser` CLI command (server access required)
- **Rails**: `rails console` for admin creation (server access required)
- **WordPress**: Database manipulation for password reset
- **Auth0**: Invitation-based admin onboarding
- **AWS IAM**: Multiple admin users, MFA enforced, recovery via root account
- **GitHub**: MFA required, recovery codes, SMS backup

**OWASP/NIST Guidelines:**
- Never expose admin creation in public APIs
- Enforce MFA for privileged accounts
- Implement comprehensive audit logging
- Use time-limited recovery tokens
- Rate limit authentication attempts

### Production Deployment Phases

#### Phase 1: Development (Current State)
- [x] Seed script functional
- [x] Role parameter ignored in public registration
- [x] Basic security documentation
- [x] All auth endpoints tested

#### Phase 2: Staging Preparation
- [ ] Implement email recovery system
- [ ] Implement recovery codes
- [ ] Add admin-only user creation endpoint
- [ ] Add comprehensive audit logging
- [ ] Test credential recovery procedures

#### Phase 3: Production Hardening
- [ ] Remove seed script from deployment
- [ ] Enforce MFA for admin accounts
- [ ] Set up monitoring and alerts
- [ ] Create incident response playbook
- [ ] Train team on credential recovery procedures
- [ ] Store admin credentials in secure vault
- [ ] Create multiple admin accounts

#### Phase 4: Ongoing Operations
- [ ] Regular security audits
- [ ] Quarterly admin credential rotation
- [ ] Review audit logs for suspicious activity
- [ ] Update recovery procedures as needed
- [ ] Test disaster recovery scenarios

**📌 Note**: Production security features should be implemented AFTER core functionality is complete and tested in staging environment.
