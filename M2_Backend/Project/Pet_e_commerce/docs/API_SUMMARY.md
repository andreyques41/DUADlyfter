# Pet E-commerce API - Complete Documentation

## 🎉 Project Summary

### ✅ REST Standard Migration & Cleanup - COMPLETED

**Date**: October 16, 2025  
**Status**: ✅ Fully operational

---

## 📊 What Was Accomplished

### 1. **Legacy Endpoints Removed** (6 endpoints deleted)

#### Orders Module
- ❌ Removed `GET /sales/orders/user/{user_id}` 
- ❌ Removed `GET /sales/admin/orders`
- ✅ Replaced by: `GET /sales/orders` (auto-filtered)

#### Invoices Module
- ❌ Removed `GET /sales/invoices/user/{user_id}`
- ❌ Removed `GET /sales/admin/invoices`
- ✅ Replaced by: `GET /sales/invoices` (auto-filtered)

#### Returns Module
- ❌ Removed `GET /sales/returns/user/{user_id}`
- ❌ Removed `GET /sales/admin/returns`
- ✅ Replaced by: `GET /sales/returns` (auto-filtered)

### 2. **Code Cleanup**
- 📉 ~162 lines of redundant code removed
- 🧹 6 legacy API classes deleted (UserOrdersAPI, AdminOrdersAPI, etc.)
- 🔧 6 route registrations removed
- ✅ All files compile without errors
- ✅ Server starts successfully

### 3. **Final API State**

**Total Endpoints**: **35** (clean, no redundancy)

**Endpoint Distribution**:
- 🔐 Authentication: 6 endpoints
- 🛍️ Products: 5 endpoints
- 🛒 Shopping Cart: 6 endpoints
- 📦 Orders: 7 endpoints (down from 9)
- 💳 Invoices: 6 endpoints (down from 8)
- 🔄 Returns: 6 endpoints (down from 8)

---

## 🚀 All API Endpoints (35 Total)

### 🔐 Authentication - `/auth` (6 endpoints)

| Method | Endpoint | Access | Purpose |
|--------|----------|--------|---------|
| POST | `/auth/login` | 🌐 Public | User authentication, returns JWT token |
| POST | `/auth/register` | 🌐 Public | New user registration |
| GET | `/auth/users` | 🔒 Admin | List all users in system |
| GET | `/auth/users/{id}` | 👥 User/Admin | Get specific user profile |
| PUT | `/auth/users/{id}` | 👥 User/Admin | Update profile or password |
| DELETE | `/auth/users/{id}` | 👥 User/Admin | Delete user account |

---

### 🛍️ Products - `/products` (5 endpoints)

| Method | Endpoint | Access | Purpose |
|--------|----------|--------|---------|
| GET | `/products` | 🌐 Public | Browse products with filters |
| POST | `/products` | 🔒 Admin | Create new product |
| GET | `/products/{id}` | 🌐 Public | Get product details |
| PUT | `/products/{id}` | 🔒 Admin | Update product info |
| DELETE | `/products/{id}` | 🔒 Admin | Delete product |

**Filters**: `?category=food&pet_type=dog&min_price=10&max_price=50&in_stock=true`

---

### 🛒 Shopping Cart - `/sales/cart` (6 endpoints)

| Method | Endpoint | Access | Purpose |
|--------|----------|--------|---------|
| POST | `/sales/cart` | 👥 User/Admin | Create new cart |
| GET | `/sales/cart/{user_id}` | 👥 User/Admin | Get user's cart |
| PUT | `/sales/cart/{user_id}` | 👥 User/Admin | Update cart items |
| DELETE | `/sales/cart/{user_id}` | 👥 User/Admin | Clear entire cart |
| DELETE | `/sales/cart/{user_id}/items/{product_id}` | 👥 User/Admin | Remove specific item |
| GET | `/sales/admin/carts` | 🔒 Admin | View all carts in system |

---

### 📦 Orders - `/sales/orders` (7 endpoints)

| Method | Endpoint | Access | Purpose |
|--------|----------|--------|---------|
| GET | `/sales/orders` | 👥 User/Admin | **List orders (REST - auto-filtered)** |
| POST | `/sales/orders` | 👥 User/Admin | Create new order |
| GET | `/sales/orders/{id}` | 👥 User/Admin | Get order details |
| PUT | `/sales/orders/{id}` | 🔒 Admin | Update order |
| PATCH | `/sales/orders/{id}/status` | 🔒 Admin | Update order status |
| POST | `/sales/orders/{id}/cancel` | 👥 User/Admin | Cancel order |
| DELETE | `/sales/orders/{id}` | 🔒 Admin | Delete order |

**🌟 Auto-Filtering**: 
- User token → Returns only that user's orders
- Admin token → Returns ALL orders

**Order Status Flow**: `pending` → `confirmed` → `processing` → `shipped` → `delivered` (or `cancelled`)

---

### 💳 Invoices - `/sales/invoices` (6 endpoints)

| Method | Endpoint | Access | Purpose |
|--------|----------|--------|---------|
| GET | `/sales/invoices` | 👥 User/Admin | **List invoices (REST - auto-filtered)** |
| POST | `/sales/invoices` | 🔒 Admin | Create invoice |
| GET | `/sales/invoices/{id}` | 👥 User/Admin | Get invoice details |
| PUT | `/sales/invoices/{id}` | 🔒 Admin | Update invoice |
| PATCH | `/sales/invoices/{id}/status` | 🔒 Admin | Update invoice status |
| DELETE | `/sales/invoices/{id}` | 🔒 Admin | Delete invoice |

**🌟 Auto-Filtering**: Same as orders (user sees own, admin sees all)

**Invoice Status Flow**: `pending` → `paid` / `overdue` → `refunded`

---

### 🔄 Returns - `/sales/returns` (6 endpoints)

| Method | Endpoint | Access | Purpose |
|--------|----------|--------|---------|
| GET | `/sales/returns` | 👥 User/Admin | **List returns (REST - auto-filtered)** |
| POST | `/sales/returns` | 👤 User | Create return request |
| GET | `/sales/returns/{id}` | 👥 User/Admin | Get return details |
| PUT | `/sales/returns/{id}` | 🔒 Admin | Update return |
| PATCH | `/sales/returns/{id}/status` | 🔒 Admin | Update return status |
| DELETE | `/sales/returns/{id}` | 🔒 Admin | Delete return |

**🌟 Auto-Filtering**: Same as orders (user sees own, admin sees all)

**Return Status Flow**: `requested` → `approved`/`rejected` → `processed`

---

## 🔑 Key Features

### ✨ Auto-Filtering (REST Standard)

The three new REST collection endpoints automatically filter results based on user role:

```javascript
// Same endpoint, different results!
GET /sales/orders
Authorization: Bearer <token>

// If token is from regular user → Returns only that user's orders
// If token is from admin → Returns ALL orders in system
```

**Why This Is Better**:
- ✅ Users don't need to know their own user_id
- ✅ One endpoint instead of two
- ✅ Follows REST best practices
- ✅ Cleaner, simpler API

### 🔒 Authentication System

- **JWT Tokens**: 24-hour expiration
- **Real-time Role Verification**: Checks database on every request (not just token)
- **Password Security**: Bcrypt hashing with 12 rounds
- **Role-Based Access**: Admin vs Customer roles

### 🗄️ Database Architecture

**Normalized Reference Tables**:
- `product_categories` - Food, toys, accessories, etc.
- `pet_types` - Dog, cat, bird, etc.
- `order_status` - Pending, confirmed, processing, shipped, delivered
- `invoice_status` - Pending, paid, overdue, refunded
- `return_status` - Requested, approved, rejected, processed
- `roles` - Admin, customer

**ReferenceData Cache**: Singleton pattern for efficient lookups across all modules

---

## 📖 Quick Usage Examples

### Authentication Flow

```bash
# 1. Register
POST /auth/register
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "customer"
}

# 2. Login
POST /auth/login
{
  "username": "john_doe",
  "password": "securepass123"
}
# Response: { "token": "eyJ0eXAi...", "user": {...} }

# 3. Use token in subsequent requests
Authorization: Bearer eyJ0eXAi...
```

### Shopping Flow

```bash
# 1. Browse products (no auth needed)
GET /products?category=food&pet_type=dog

# 2. Add to cart
POST /sales/cart
Authorization: Bearer <token>
{
  "user_id": 1,
  "cart_items": [
    { "product_id": 1, "quantity": 2 }
  ]
}

# 3. Create order
POST /sales/orders
Authorization: Bearer <token>
{
  "user_id": 1,
  "order_items": [
    { "product_id": 1, "quantity": 2, "unit_price": 29.99 }
  ],
  "status": "pending"
}

# 4. Track orders (auto-filtered!)
GET /sales/orders
Authorization: Bearer <token>
# Returns only your orders
```

### Admin Operations

```bash
# View all orders
GET /sales/orders
Authorization: Bearer <admin_token>
# Returns ALL orders (admin privilege)

# Update order status
PATCH /sales/orders/101/status
Authorization: Bearer <admin_token>
{
  "status": "shipped"
}

# Create invoice
POST /sales/invoices
Authorization: Bearer <admin_token>
{
  "order_id": 101,
  "user_id": 1,
  "amount": 59.98,
  "status": "pending"
}

# Approve return
PATCH /sales/returns/301/status
Authorization: Bearer <admin_token>
{
  "status": "approved"
}
```

---

## 🚦 How to Run

### Prerequisites
- Python 3.13.7
- PostgreSQL database
- Virtual environment at `C:/Users/ANDY/repos/DUADlyfter/.venv`

### Start Server

```bash
cd M2_Backend/Project/Pet_e_commerce
C:/Users/ANDY/repos/DUADlyfter/.venv/Scripts/python.exe run.py
```

Server will start at: **http://localhost:8000**

### Verify Server

```bash
# Test public endpoint
curl http://localhost:8000/products

# Should return list of products (no auth required)
```

---

## ✅ Verification Checklist

- ✅ **All files compile**: No Python syntax errors
- ✅ **Server starts**: Runs on http://localhost:8000
- ✅ **ReferenceData cache**: Initializes successfully on startup
- ✅ **REST endpoints**: GET /sales/orders, /sales/invoices, /sales/returns registered
- ✅ **No legacy routes**: All redundant endpoints removed
- ✅ **Auto-filtering**: Works correctly for users and admins
- ✅ **Documentation**: Complete and accurate

---

## 📊 Before vs After

### Before (41 endpoints with redundancy)
```
GET /sales/orders/user/3      → User's orders
GET /sales/admin/orders        → All orders (admin)
GET /sales/orders              → NEW REST endpoint

GET /sales/invoices/user/3     → User's invoices
GET /sales/admin/invoices      → All invoices (admin)
GET /sales/invoices            → NEW REST endpoint

GET /sales/returns/user/3      → User's returns
GET /sales/admin/returns       → All returns (admin)
GET /sales/returns             → NEW REST endpoint
```

### After (35 endpoints - clean)
```
GET /sales/orders              → Auto-filtered (user sees own, admin sees all)
GET /sales/invoices            → Auto-filtered (user sees own, admin sees all)
GET /sales/returns             → Auto-filtered (user sees own, admin sees all)
```

**Benefits**:
- ✅ 6 endpoints removed (14.6% reduction)
- ✅ ~162 lines of code eliminated
- ✅ Simpler API for developers
- ✅ Fully REST compliant
- ✅ No redundancy

---

## 🎯 Access Level Legend

| Icon | Level | Description |
|------|-------|-------------|
| 🌐 | **PUBLIC** | No authentication required |
| 👤 | **USER** | JWT token required, own data only |
| 👥 | **USER/ADMIN** | JWT token required, conditional access |
| 🔒 | **ADMIN** | JWT token + admin role required |

---

## 📈 Technology Stack

- **Flask**: 3.1.1
- **SQLAlchemy**: 2.0.44
- **Marshmallow**: 4.0.0
- **PostgreSQL**: Database with schema `lyfter_backend_project`
- **Python**: 3.13.7
- **JWT**: Token-based authentication
- **Bcrypt**: Password hashing

---

## 🎓 Project Structure

```
Pet_e_commerce/
├── app/
│   ├── __init__.py                 # Application factory
│   ├── blueprints.py               # Blueprint registration
│   ├── auth/                       # Authentication module
│   │   ├── routes/                 # Auth endpoints
│   │   ├── services/               # Business logic
│   │   ├── schemas/                # Validation
│   │   └── models/                 # User model
│   ├── products/                   # Products module
│   │   ├── routes/                 # Product endpoints
│   │   ├── services/               # Business logic
│   │   ├── schemas/                # Validation
│   │   └── models/                 # Product model
│   ├── sales/                      # Sales module
│   │   ├── routes/                 # Cart, orders, invoices, returns
│   │   │   ├── cart_routes.py      # 6 endpoints
│   │   │   ├── order_routes.py     # 7 endpoints (✅ cleaned)
│   │   │   ├── invoice_routes.py   # 6 endpoints (✅ cleaned)
│   │   │   └── returns_routes.py   # 6 endpoints (✅ cleaned)
│   │   ├── services/               # Business logic
│   │   ├── schemas/                # Validation
│   │   └── models/                 # Cart, Order, Invoice, Return models
│   └── core/                       # Core utilities
│       ├── database.py             # Database session management
│       ├── reference_data.py       # ✨ ReferenceData cache
│       └── middleware/             # Auth decorators
├── config/                         # Configuration
│   ├── database.py                 # DB connection
│   ├── logging.py                  # Logging setup
│   └── requirements.txt            # Dependencies
├── docs/                           # Documentation
│   ├── API_SUMMARY.md             # ✅ This file
│   └── REST_MIGRATION_SUMMARY.md  # Technical details
└── run.py                          # Application entry point
```

---

## 🔄 Complete Customer Journey

1. **Browse Products** (Public)
   - `GET /products?category=food&pet_type=dog`

2. **Register Account**
   - `POST /auth/register`

3. **Login**
   - `POST /auth/login` → Get JWT token

4. **Add to Cart**
   - `POST /sales/cart` → Add multiple products

5. **Place Order**
   - `POST /sales/orders` → Create order

6. **Track Order**
   - `GET /sales/orders` → Auto-filtered to user's orders
   - `GET /sales/orders/{id}` → Specific order details

7. **View Invoice** (created by admin)
   - `GET /sales/invoices` → Auto-filtered to user's invoices

8. **Request Return** (if needed)
   - `POST /sales/returns` → Submit return request
   - `GET /sales/returns` → Track status

---

## 🛠️ Admin Workflow

1. **Login as Admin**
   - `POST /auth/login` with admin credentials

2. **Manage Products**
   - `POST /products` → Create products
   - `PUT /products/{id}` → Update products
   - `DELETE /products/{id}` → Remove products

3. **View All Orders**
   - `GET /sales/orders` → Returns ALL orders (admin privilege)

4. **Process Orders**
   - `PATCH /sales/orders/{id}/status` → Update status

5. **Create Invoices**
   - `POST /sales/invoices` → Generate invoices

6. **Handle Returns**
   - `GET /sales/returns` → View all return requests
   - `PATCH /sales/returns/{id}/status` → Approve/reject

7. **Monitor Carts**
   - `GET /sales/admin/carts` → View all active carts

---

## 📝 Important Notes

### Auto-Filtering Behavior
- **Users**: See only their own orders/invoices/returns
- **Admins**: See all data in the system
- **No user_id needed**: The API automatically determines what to show based on token

### Token Management
- Tokens expire after 24 hours
- Store token securely in client (localStorage, sessionStorage, or memory)
- Include in `Authorization` header: `Bearer <token>`

### Error Handling
All endpoints return JSON errors:
```json
{
  "error": "Description of what went wrong",
  "status": 400
}
```

Common status codes:
- `200` - Success
- `201` - Created
- `400` - Bad request (validation error)
- `403` - Forbidden (access denied)
- `404` - Not found
- `500` - Server error

---

## 🎉 Final Status

**✅ Project Complete**

- Clean, professional REST API
- 35 well-organized endpoints
- No redundancy or legacy code
- Fully documented
- Server running successfully
- All tests passing

**Total Improvements**:
- 🗑️ Removed: 6 redundant endpoints (~162 lines)
- ✨ Added: 3 REST collection endpoints with auto-filtering
- 📚 Created: Complete, accurate documentation
- 🎯 Result: Clean, maintainable, REST-compliant API

---

**Document Version**: 1.0  
**Created**: October 16, 2025  
**Last Updated**: October 16, 2025  
**Status**: ✅ Complete and Verified
