# 🚀 Pet E-commerce API - Complete Reference

**Base URL**: `http://localhost:8000`  
**Format**: JSON  
**Auth**: JWT Bearer Token  
**Endpoints**: 42 (All validated ✅)

---

## 📑 Quick Navigation

| Module | Endpoints | Description |
|--------|-----------|-------------|
| [🔐 Authentication](#-authentication) | 2 | Register, Login |
| [👤 Users](#-users) | 8 | User CRUD, Role Management |
| [🛍️ Products](#️-products) | 5 | Product Catalog |
| [🛒 Carts](#-shopping-cart) | 8 | Shopping Cart Management |
| [📦 Orders](#-orders) | 7 | Order Lifecycle |
| [💳 Invoices](#-invoices) | 6 | Invoice Tracking |
| [🔄 Returns](#-returns) | 6 | Return Workflow |

**Access Levels**: 🌐 Public | 🔒 Authenticated | 👑 Admin

---

## 🔐 Authentication

### 1. Register User
`POST /auth/register` | 🌐 Public

**Request**:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role": "user"
}
```

**Required**: `username` (3-50 chars), `email`, `password` (8+ chars)  
**Optional**: `first_name`, `last_name`, `phone`, `role` (default: "user")

**Response 201**:
```json
{
  "message": "User registered successfully",
  "user": { "id": 1, "username": "johndoe", "email": "john@example.com", "roles": ["user"] }
}
```

---

### 2. Login
`POST /auth/login` | 🌐 Public

**Request**:
```json
{
  "username": "johndoe",
  "password": "securepass123"
}
```

**Response 200**:
```json
{
  "message": "Login successful",
  "user": { "id": 1, "username": "johndoe", "roles": ["user"] },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

💡 **Save the token** and include in all authenticated requests:  
`Authorization: Bearer {token}`

---

## 👤 Users

**Endpoints**: 8 | **Access**: 🔒 Authenticated (own profile) or 👑 Admin (all users)

| # | Method | Endpoint | Description | Access |
|---|--------|----------|-------------|--------|
| 3 | GET | `/auth/users` | List all users | 👑 Admin |
| 4 | GET | `/auth/users/{id}` | View user profile | 🔒 Own / 👑 Admin |
| 5 | PUT | `/auth/users/{id}` | Update profile | 🔒 Own / 👑 Admin |
| 6 | GET | `/auth/users/{id}/roles` | View user roles | 👑 Admin |
| 7 | POST | `/auth/users/{id}/roles` | Assign role | 👑 Admin |
| 8 | DELETE | `/auth/users/{id}/roles` | Remove role | 👑 Admin |
| 9 | PUT | `/auth/users/{id}` | Change password | 🔒 Own |
| 10 | DELETE | `/auth/users/{id}` | Delete user | 🔒 Own / 👑 Admin |

### Key Operations

**List All Users** (3):
```bash
GET /auth/users
Authorization: Bearer {admin_token}
# Returns: Array of all users with id, username, email, roles
```

**View Profile** (4):
```bash
GET /auth/users/1
# Returns: User details (id, username, email, first_name, last_name, phone, roles)
```

**Update Profile** (5):
```json
PUT /auth/users/1
{ "first_name": "Jonathan", "email": "new@example.com", "phone": "+999" }
```

**Role Management** (6-8):
```json
POST /auth/users/1/roles
{ "role": "admin" }  // Assign admin role

DELETE /auth/users/1/roles
{ "role": "admin" }  // Remove admin role

GET /auth/users/1/roles  // View current roles
```

**Change Password** (9):
```json
PUT /auth/users/1
{
  "current_password": "old123",
  "new_password": "new456",
  "confirm_password": "new456"
}
```

---

## 🛍️ Products

**Endpoints**: 5 | **Access**: 🌐 Public (read) | 👑 Admin (write)

| # | Method | Endpoint | Description | Access |
|---|--------|----------|-------------|--------|
| 11 | GET | `/products` | List all products | 🌐 Public |
| 12 | GET | `/products/{id}` | View product details | 🌐 Public |
| 13 | POST | `/products` | Create product | 👑 Admin |
| 14 | PUT | `/products/{id}` | Update product | 👑 Admin |
| 15 | DELETE | `/products/{id}` | Delete product | 👑 Admin |

### Key Operations

**List Products** (11) - **Filters Available**:
```bash
GET /products?category=food&pet_type=dog&min_price=10&max_price=50
```

**Filters**:
- `category`: food, toys, accessories, health, grooming
- `pet_type`: dog, cat, bird, fish, reptile, other
- `min_price`, `max_price`: Price range

**Response**:
```json
[
  {
    "id": 1,
    "sku": "DOG01",
    "description": "Premium Dog Food 15kg",
    "category": "food",
    "pet_type": "dog",
    "stock_quantity": 50,
    "price": 45.99,
    "brand": "PetNutrition",
    "is_active": true
  }
]
```

**Create Product** (13):
```json
POST /products
{
  "sku": "DOG03",
  "description": "Organic Dog Treats",
  "category": "food",
  "pet_type": "dog",
  "stock_quantity": 200,
  "price": 15.99,
  "cost": 8.50,
  "brand": "OrganicPets",
  "is_active": true
}
```

**Required**: `sku`, `description`, `category`, `pet_type`, `stock_quantity`, `price`

---

## 🛒 Shopping Cart

**Endpoints**: 8 | **Access**: 🔒 Authenticated (own cart) | 👑 Admin (all carts)

| # | Method | Endpoint | Description | Access |
|---|--------|----------|-------------|--------|
| 16 | GET | `/sales/carts` | List carts (role-based) | 🔒 Auth |
| 17 | POST | `/sales/carts` | Create cart | 🔒 Auth |
| 18 | GET | `/sales/carts/{user_id}` | View cart | 🔒 Own / 👑 Admin |
| 19 | PUT | `/sales/carts/{user_id}` | Update cart | 🔒 Own / 👑 Admin |
| 20 | DELETE | `/sales/carts/{user_id}` | Clear cart | 🔒 Own / 👑 Admin |
| 21 | POST | `/sales/carts/{user_id}/items/{product_id}` | Add item | 🔒 Own / 👑 Admin |
| 22 | PUT | `/sales/carts/{user_id}/items/{product_id}` | Update item quantity | 🔒 Own / 👑 Admin |
| 23 | DELETE | `/sales/carts/{user_id}/items/{product_id}` | Remove item | 🔒 Own / 👑 Admin |

### Key Operations

**Create Cart** (17):
```json
POST /sales/carts
{
  "user_id": 1,
  "items": [
    { "product_id": 1, "quantity": 2 },
    { "product_id": 2, "quantity": 1 }
  ]
}
```

**Limits**: 1-100 items per cart, 1-50 quantity per product

**Add Item** (21):
```json
POST /sales/carts/1/items/3
{ "quantity": 2 }
```

**Update Item** (22):
```json
PUT /sales/carts/1/items/3
{ "quantity": 5 }
```

---

## 📦 Orders

**Endpoints**: 7 | **Access**: 🔒 Authenticated (own orders) | 👑 Admin (all orders, status updates)

| # | Method | Endpoint | Description | Access |
|---|--------|----------|-------------|--------|
| 24 | GET | `/sales/orders` | List orders (role-based) | 🔒 Auth |
| 25 | GET | `/sales/orders/{id}` | View order details | 🔒 Own / 👑 Admin |
| 26 | POST | `/sales/orders` | Create order (checkout) | 🔒 Auth |
| 27 | PUT | `/sales/orders/{id}` | Update order | 👑 Admin |
| 28 | PATCH | `/sales/orders/{id}/status` | Update order status | 👑 Admin |
| 29 | POST | `/sales/orders/{id}/cancel` | Cancel order | 🔒 Own / 👑 Admin |
| 30 | DELETE | `/sales/orders/{id}` | Delete order | 👑 Admin |

### Key Operations

**Create Order** (26) - **Auto-creates invoice**:
```json
POST /sales/orders
{
  "user_id": 1,
  "items": [
    { "product_id": 1, "quantity": 2 },
    { "product_id": 2, "quantity": 1 }
  ],
  "shipping_address": "123 Main St, City"
}
```

**Status Workflow** (28):
```
pending → confirmed → processing → shipped → delivered
                                              ↓
                                         cancelled (from any status)
```

**Cancel Order** (29):
```json
POST /sales/orders/1/cancel
# Returns 200 on success, 400 if already cancelled
```

**Update Status**:
```json
PATCH /sales/orders/1/status
{ "status": "shipped" }
```

**Filter Orders** (24):
```bash
GET /sales/orders?status=pending
```

---

## 💳 Invoices

**Endpoints**: 6 | **Access**: 🔒 Authenticated (own invoices) | 👑 Admin (all invoices, CRUD)

| # | Method | Endpoint | Description | Access |
|---|--------|----------|-------------|--------|
| 31 | GET | `/sales/invoices` | List invoices (role-based) | 🔒 Auth |
| 32 | GET | `/sales/invoices/{id}` | View invoice details | 🔒 Own / 👑 Admin |
| 33 | POST | `/sales/invoices` | Create invoice | 👑 Admin |
| 34 | PUT | `/sales/invoices/{id}` | Update invoice | 👑 Admin |
| 35 | PATCH | `/sales/invoices/{id}/status` | Update invoice status | 👑 Admin |
| 36 | DELETE | `/sales/invoices/{id}` | Delete invoice | 👑 Admin |

### Key Operations

**Create Invoice** (33):
```json
POST /sales/invoices
{
  "user_id": 1,
  "order_id": 1,
  "due_date": "2025-11-15T23:59:59",
  "status": "pending"
}
```

**Note**: Invoices are auto-created when orders are placed (30-day due date)

**Status Workflow** (35):
- `pending` → `paid` → `overdue` → `refunded`

**Update Status**:
```json
PATCH /sales/invoices/1/status
{ "status": "paid" }
```

**Filter Invoices** (31):
```bash
GET /sales/invoices?status=paid
```

---

## 🔄 Returns

**Endpoints**: 6 | **Access**: 🔒 Authenticated (own returns, create) | 👑 Admin (all returns, approve/reject)

| # | Method | Endpoint | Description | Access |
|---|--------|----------|-------------|--------|
| 37 | GET | `/sales/returns` | List returns (role-based) | 🔒 Auth |
| 38 | GET | `/sales/returns/{id}` | View return details | 🔒 Own / 👑 Admin |
| 39 | POST | `/sales/returns` | Create return request | 🔒 Auth |
| 40 | PUT | `/sales/returns/{id}` | Update return | 👑 Admin |
| 41 | PATCH | `/sales/returns/{id}/status` | Update return status | 👑 Admin |
| 42 | DELETE | `/sales/returns/{id}` | Delete return | 👑 Admin |

### Key Operations

**Create Return Request** (39):
```json
POST /sales/returns
{
  "order_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 1,
      "reason": "Product arrived damaged",
      "refund_amount": 45.99
    }
  ],
  "status": "requested"
}
```

**Status Workflow** (41):
```
requested → approved → processed
         → rejected
```

**Update Status**:
```json
PATCH /sales/returns/1/status
{ "status": "approved" }
```

**Update with Admin Notes** (40):
```json
PUT /sales/returns/1
{
  "status": "approved",
  "admin_notes": "Refund approved, product will be restocked"
}
```

**Filter Returns** (37):
```bash
GET /sales/returns?status=requested
```

---

## 📝 HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Duplicate/constraint violation |
| 500 | Internal Server Error |

---

## 🔑 Authentication Flow

### 1. Register & Login
```bash
# Register
POST /auth/register
{ "username": "newuser", "email": "user@example.com", "password": "pass123" }

# Login
POST /auth/login
{ "username": "newuser", "password": "pass123" }
# Response: { "token": "eyJhbG..." }
```

### 2. Use Token
```bash
# Include in all authenticated requests
curl -H "Authorization: Bearer eyJhbG..." http://localhost:8000/auth/users
```

### 3. Token Info
- **Expiration**: 24 hours
- **Verification**: Real-time database role check on every request
- **Storage**: Save in localStorage/sessionStorage (frontend)

---

## 🎯 Example Workflows

### Complete Purchase Flow
```bash
# 1. Browse products (public)
GET /products?category=food&pet_type=dog

# 2. Register/Login
POST /auth/register
POST /auth/login  # Get token

# 3. Create cart
POST /sales/carts
{ "user_id": 1, "items": [{"product_id": 1, "quantity": 2}] }

# 4. Add more items
POST /sales/carts/1/items/2
{ "quantity": 1 }

# 5. Checkout (creates order + invoice)
POST /sales/orders
{ "user_id": 1, "items": [...], "shipping_address": "123 Main St" }

# 6. View order
GET /sales/orders/1

# 7. View invoice
GET /sales/invoices/1
```

### Admin Product Management
```bash
# Login as admin
POST /auth/login
{ "username": "admin", "password": "adminpass" }

# Create product
POST /products
{ "sku": "NEW01", "description": "New Product", ... }

# Update stock
PUT /products/1
{ "stock_quantity": 150, "price": 29.99 }

# View all orders
GET /sales/orders

# Update order status
PATCH /sales/orders/1/status
{ "status": "shipped" }

# Approve return
PATCH /sales/returns/1/status
{ "status": "approved" }
```

---

## 💡 Best Practices

1. **Always include Authorization header** for protected endpoints
2. **Validate input** before sending requests
3. **Handle errors** appropriately (check status codes)
4. **Renew tokens** when they expire (24h default)
5. **Use HTTPS** in production
6. **Never expose tokens** in URLs or public logs

---

## 🚨 Common Errors

### 401 Unauthorized
```json
{ "error": "Authorization header missing" }
```
**Solution**: Include `Authorization: Bearer {token}`

### 403 Forbidden
```json
{ "error": "Admin access required" }
```
**Solution**: User needs admin role for this operation

### 409 Conflict
```json
{ "error": "Username already exists" }
```
**Solution**: Username/email already registered

### 404 Not Found
```json
{ "error": "Resource not found" }
```
**Solution**: Invalid ID or resource doesn't exist

---

## 📢 Version History

### v1.1 (October 19, 2025) - Current ✅

**Major Changes**:
- ✅ All 42 endpoints validated and tested
- ✅ REST-compliant cart routes (`/sales/cart` → `/sales/carts`)
- ✅ Role-based filtering for all list endpoints
- ✅ Status updates use `PATCH` instead of `PUT`
- ✅ Removed `/admin/carts` route (use `GET /carts` with admin token)

**Migration from v1.0**:
```javascript
// Old (v1.0)
GET /sales/admin/carts
GET /sales/cart/123

// New (v1.1)
GET /sales/carts  // With admin token
GET /sales/carts/123
```

---

**Last Updated**: October 19, 2025  
**API Version**: 1.1  
**Status**: Production-ready ✅  
**Documentation**: Complete and validated
