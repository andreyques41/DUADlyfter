# 🍳 LyfterCook API Documentation

## 📋 Base URL

```
Development: http://localhost:5000
Production: https://api.lyftercook.com (TBD)
```

---

## 🎯 Quick Summary

| Icon | Meaning | Description |
|-------|-------------|-------------|
| 🌐 | **Public** | No authentication required. Anyone can access. |
| 🔒 | **Chef** | Requires JWT token. Only authenticated users with `chef` role. |
| 👑 | **Admin** | Requires JWT token + `admin` role. Full system access. |
| ⚡ | **Cached** | Endpoint uses caching for improved performance. |

**Total Endpoints:** 60 (9 public + 40 chef + 11 admin)
**Cached Endpoints:** 8 (marked with ⚡)

---

## 🔐 Authentication

### Endpoint Types

**🌐 Public (No authentication):**
- Don't require JWT token
- Anyone can access
- Examples: `/public/chefs`, `/auth/register`, `/auth/login`

**🔒 Protected (Requires Chef authentication):**
- Require valid JWT token in Authorization header
- Only authenticated users with `chef` role
- Each chef can only manage their own resources (chefs cannot view/modify other chefs' data)

**👑 Admin (Requires Administrator authentication):**
- Require valid JWT token in Authorization header
- Only users with `admin` role
- Full access: can view and manage resources from all chefs
- Includes supervision, statistics, and moderation endpoints

**⚡ Cached (Performance optimized):**
- Endpoint implements caching for faster responses
- First request fetches from database, subsequent requests serve from cache
- Cache automatically invalidates on data updates

### How to get the token

1. Register: `POST /auth/register` (default role: `chef`)
2. Login: `POST /auth/login` (you'll receive the `token`)
3. Include the token in all protected endpoints:

```http
Authorization: Bearer <your_jwt_token>
```

**Token expiration:** 24 hours

### Important notes

- Protected endpoints (🔒) operate on the authenticated chef's data
- Admin endpoints (👑) have full access to all system resources
- A chef **CANNOT** access/modify another chef's data
- Admins **CAN** view and manage data from all chefs
- To create content (dishes/menus), an admin must have a separate chef profile
- Cached endpoints (⚡) provide faster responses after the first request

---

## 📊 Testing Status

| Module | Endpoints | Tests | Test Status | User Validation | Last Update |
|--------|-----------|-------|-------------|-----------------|-------------|
| Auth | 3 | 16 | ✅ **100%** | ✅ **VALIDATED** | 2025-12-28 |
| Chef | 3 | 3 | ✅ **100%** | ✅ **VALIDATED** | 2025-12-28 |
| Client | 5 | 8 | ✅ **100%** | ⏳ **PENDING** | 2025-12-28 |
| Dish | 5 | 14 | ✅ **100%** | ⏳ **PENDING** | 2025-12-28 |
| Menu | 6 | 9 | ✅ **100%** | ⏳ **PENDING** | 2025-12-28 |
| Quotation | 6 | 8 | ✅ **100%** | ⏳ **PENDING** | 2025-12-28 |
| Appointment | 6 | 12 | ✅ **100%** | ⏳ **PENDING** | 2025-12-28 |
| Scraper | 9 | 12 | ✅ **100%** | ⏳ **PENDING** | 2025-12-28 |
| Public | 6 | 15 | ✅ **100%** | ⏳ **PENDING** | 2025-12-28 |
| **Admin** | **11** | **16** | ✅ **100%** | ✅ **IMPLEMENTED** | 2025-12-28 |

**Total Implemented:** 60 endpoints | **Total Tests:** 110 (100% passing) | **Manually Validated:** 2/10 modules

---

## 📍 Endpoints Overview

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| **AUTH MODULE** ||||
| `POST` | `/auth/register` | 🌐 Public | Create new chef account |
| `POST` | `/auth/login` | 🌐 Public | Login and get token |
| `GET` | `/auth/me` | 🔒 Chef ⚡ | View my user information (cached via auth middleware) |
| **CHEF MODULE** ||||
| `POST` | `/chefs/profile` | 🔒 Chef | Create my chef profile (own) |
| `GET` | `/chefs/profile` | 🔒 Chef ⚡ | View my chef profile (service-level cache) |
| `PUT` | `/chefs/profile` | 🔒 Chef | Update my chef profile |
| **CLIENT MODULE** ||||
| `POST` | `/clients` | 🔒 Chef | Create client (assigned to me) |
| `GET` | `/clients` | 🔒 Chef | List my clients |
| `GET` | `/clients/:id` | 🔒 Chef | View one of my clients |
| `PUT` | `/clients/:id` | 🔒 Chef | Update one of my clients |
| `DELETE` | `/clients/:id` | 🔒 Chef | Delete one of my clients |
| **DISH MODULE** ||||
| `POST` | `/dishes` | 🔒 Chef | Create dish (assigned to me) |
| `GET` | `/dishes` | 🔒 Chef ⚡ | List my dishes (cached) |
| `GET` | `/dishes/:id` | 🔒 Chef ⚡ | View one of my dishes (cached) |
| `PUT` | `/dishes/:id` | 🔒 Chef | Update one of my dishes |
| `DELETE` | `/dishes/:id` | 🔒 Chef | Delete one of my dishes |
| **MENU MODULE** ||||
| `POST` | `/menus` | 🔒 Chef | Create menu (assigned to me) |
| `GET` | `/menus` | 🔒 Chef ⚡ | List my menus (cached) |
| `GET` | `/menus/:id` | 🔒 Chef ⚡ | View one of my menus (cached) |
| `PUT` | `/menus/:id` | 🔒 Chef | Update one of my menus |
| `PUT` | `/menus/:id/dishes` | 🔒 Chef | Assign dishes to my menu |
| `DELETE` | `/menus/:id` | 🔒 Chef | Delete one of my menus |
| **QUOTATION MODULE** ||||
| `POST` | `/quotations` | 🔒 Chef | Create quotation (assigned to me) |
| `GET` | `/quotations` | 🔒 Chef | List my quotations |
| `GET` | `/quotations/:id` | 🔒 Chef | View one of my quotations |
| `PUT` | `/quotations/:id` | 🔒 Chef | Update one of my quotations |
| `PATCH` | `/quotations/:id/status` | 🔒 Chef | Change my quotation status |
| `DELETE` | `/quotations/:id` | 🔒 Chef | Delete one of my quotations |
| **APPOINTMENT MODULE** ||||
| `POST` | `/appointments` | 🔒 Chef | Create appointment (assigned to me) |
| `GET` | `/appointments` | 🔒 Chef | List my appointments |
| `GET` | `/appointments/:id` | 🔒 Chef | View one of my appointments |
| `PUT` | `/appointments/:id` | 🔒 Chef | Update one of my appointments |
| `PATCH` | `/appointments/:id/status` | 🔒 Chef | Change my appointment status |
| `DELETE` | `/appointments/:id` | 🔒 Chef | Delete one of my appointments |
| **SCRAPER MODULE** ||||
| `POST` | `/scrapers/sources` | 🔒 Chef | Create price source |
| `GET` | `/scrapers/sources` | 🔒 Chef | List price sources |
| `GET` | `/scrapers/sources/:id` | 🔒 Chef | View a price source |
| `PUT` | `/scrapers/sources/:id` | 🔒 Chef | Update a price source |
| `DELETE` | `/scrapers/sources/:id` | 🔒 Chef | Delete a price source |
| `POST` | `/scrapers/scrape` | 🔒 Chef | Scrape ingredient prices |
| `GET` | `/scrapers/prices` | 🔒 Chef | View scraped prices |
| `GET` | `/scrapers/prices/compare` | 🔒 Chef | Compare prices between sources |
| `DELETE` | `/scrapers/prices/cleanup` | 🔒 Chef | Clean up old prices |
| **PUBLIC MODULE** ||||
| `GET` | `/public/chefs` | 🌐 Public ⚡ | List all active chefs with filters (cached, 5min) |
| `GET` | `/public/chefs/:id` | 🌐 Public ⚡ | View complete chef profile (cached, 10min) |
| `GET` | `/public/search` | 🌐 Public | General chef search |
| `GET` | `/public/filters` | 🌐 Public | Get available filters |
| `GET` | `/public/menus/:id` | 🌐 Public | View public menu |
| `GET` | `/public/dishes/:id` | 🌐 Public | View public dish |
| **ADMIN MODULE** ||||
| `GET` | `/admin/dashboard` | 👑 Admin | Dashboard with global statistics |
| `GET` | `/admin/chefs` | 👑 Admin | List ALL system chefs |
| `GET` | `/admin/chefs/:id` | 👑 Admin | View complete profile of any chef |
| `PATCH` | `/admin/chefs/:id/status` | 👑 Admin | Activate/deactivate chef |
| `GET` | `/admin/users` | 👑 Admin | List all users |
| `DELETE` | `/admin/users/:id` | 👑 Admin | Delete user (soft delete) |
| `GET` | `/admin/reports` | 👑 Admin | System reports and analysis |
| `GET` | `/admin/audit-logs` | 👑 Admin | Administrative action logs |
| `GET` | `/admin/audit-logs/statistics` | 👑 Admin | Audit logs statistics |
| `GET` | `/admin/cache/stats` | 👑 Admin | Redis cache statistics |
| `DELETE` | `/admin/cache/clear` | 👑 Admin | Clear Redis cache by pattern |

---

## 📍 API Endpoints Details

### 🔐 **Auth Module** (✅ VALIDATED)

> **Autenticación:** 2 endpoints públicos (🌐) + 1 protegido (🔒)

#### **1. Register User** 🌐 Public
```http
POST /auth/register
```

**Request Body:**
```json
{
  "username": "chef_john",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "role": "chef"  // Optional: "chef" or "admin" (defaults to "chef")
}
```

**Validation Rules:**
- `username`: 3-50 characters, alphanumeric + underscores only
- `email`: Valid email format, max 120 characters
- `password`: Minimum 8 characters
- `role`: Either "chef" or "admin"

**Success Response (201 Created):**
```json
{
  "data": {
    "id": 1,
    "username": "chef_john",
    "email": "john@example.com",
    "role": "chef",
    "is_active": true,
    "created_at": "2025-11-26T10:30:00",
    "updated_at": "2025-11-26T10:30:00"
  },
  "message": "User registered successfully"
}
```

**Error Responses:**

400 Bad Request - Validation errors:
```json
{
  "error": "Validation failed",
  "status_code": 400,
  "details": {
    "username": ["Username must be between 3 and 50 characters"],
    "password": ["Password must be between 8 and 128 characters"]
  }
}
```

400 Bad Request - Duplicate user:
```json
{
  "error": "Username 'chef_john' is already taken",
  "status_code": 400
}
```



---

#### **2. Login** 🌐 Public
```http
POST /auth/login
```

**Request Body:**
```json
{
  "username": "chef_john",
  "password": "SecurePass123!"
}
```

**Success Response (200 OK):**
```json
{
  "data": {
    "user": {
      "id": 1,
      "username": "chef_john",
      "email": "john@example.com",
      "role": "chef",
      "is_active": true,
      "created_at": "2025-11-26T10:30:00",
      "updated_at": "2025-11-26T10:30:00"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer"
  },
  "message": "Login successful"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Invalid username or password",
  "status_code": 401
}
```



---

#### **3. Get Current User** 🔒 Chef
```http
GET /auth/me
```

**Headers:**
```http
Authorization: Bearer <your_jwt_token>
```

**Success Response (200 OK):**
```json
{
  "data": {
    "id": 1,
    "username": "chef_john",
    "email": "john@example.com",
    "role": "chef",
    "is_active": true,
    "created_at": "2025-11-26T10:30:00",
    "updated_at": "2025-11-26T10:30:00"
  }
}
```

**Error Responses:**

401 Unauthorized - Missing token:
```json
{
  "error": "Missing authorization header",
  "status_code": 401
}
```

401 Unauthorized - Invalid token:
```json
{
  "error": "Invalid or expired token",
  "status_code": 401
}
```

---

### 👨‍🍳 **Chef Module** (✅ VALIDATED)

> **Module Structure:** 3 endpoints total (all protected 🔒)
> - Manage own chef profile (requires authentication)
> - Each chef can only manage their own profile
> 
> **Cache:** 1 endpoint uses caching (⚡)
> 
> **Important note:** For public listing and viewing of chef profiles, use the `/public/chefs` endpoints instead. This module focuses exclusively on authenticated profile management.

#### **1. Create Chef Profile** 🔒 Chef
```http
POST /chefs/profile
Authorization: Bearer {token}

Body:
{
  "bio": "Passionate chef with 10 years of experience in Italian cuisine",
  "specialty": "Italian Cuisine",
  "phone": "+1-555-0100",
  "location": "Miami, FL"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "bio": "Passionate chef with 10 years...",
    "specialty": "Italian Cuisine",
    "phone": "+1-555-0100",
    "location": "Miami, FL",
    "is_active": true,
    "created_at": "2025-12-13T10:00:00Z",
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com"
    }
  },
  "message": "Chef profile created successfully"
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Chef profile already exists for this user"
}
```

---

#### **2. Get My Profile** 🔒 Chef ⚡
```http
GET /chefs/profile
Authorization: Bearer {token}
```

**Cache:** This endpoint uses caching for improved performance. First request fetches from database, subsequent requests serve from Redis cache.

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "bio": "Passionate chef...",
    "specialty": "Italian Cuisine",
    "phone": "+1-555-0100",
    "location": "Miami, FL",
    "is_active": true,
    "created_at": "2025-12-13T10:00:00Z",
    "updated_at": "2025-12-13T10:00:00Z",
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com"
    }
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Chef profile not found"
}
```

---

#### **3. Update My Profile** 🔒 Chef
```http
PUT /chefs/profile
Authorization: Bearer {token}

Body:
{
  "bio": "Updated bio text",
  "specialty": "French Cuisine",
  "phone": "+1-555-0199",
  "location": "Los Angeles, CA"
}
```

**Note:** All fields are optional. Only provided fields will be updated.

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "bio": "Updated bio text",
    "specialty": "French Cuisine",
    "phone": "+1-555-0199",
    "location": "Los Angeles, CA",
    "is_active": true,
    "updated_at": "2025-12-13T11:00:00Z",
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com"
    }
  },
  "message": "Chef profile updated successfully"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Chef profile not found"
}
```

---

### 🧑‍💼 **Client Module** (✅ VALIDATED)

> **Authentication:** All endpoints require Chef authentication (🔒)
> 
> **Note:** You can only manage your own clients. Each client is automatically assigned to the authenticated chef.

#### **1. Create Client** 🔒 Chef
```http
POST /clients
Authorization: Bearer {token}

Body:
{
  "name": "John Client",
  "email": "client@example.com",
  "phone": "+1-555-0200",
  "company": "ABC Corp",
  "notes": "Prefers vegetarian options"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "chef_id": 1,
    "name": "John Client",
    "email": "client@example.com",
    "phone": "+1-555-0200",
    "company": "ABC Corp",
    "notes": "Prefers vegetarian options",
    "created_at": "2025-12-13T10:00:00Z"
  },
  "message": "Client created successfully"
}
```

---

#### **2. List Clients** 🔒 Chef
```http
GET /clients
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "chef_id": 1,
      "name": "John Client",
      "email": "client@example.com",
      "phone": "+1-555-0200",
      "company": "ABC Corp",
      "notes": "Prefers vegetarian options",
      "created_at": "2025-12-13T10:00:00Z"
    }
  ],
  "message": "Retrieved 2 clients"
}
```

---

#### **3. Get Client by ID** 🔒 Chef
```http
GET /clients/{id}
Authorization: Bearer {token}
```

**URL Parameters:**
- `id` (integer, required): Client ID

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "chef_id": 1,
    "name": "John Client",
    "email": "client@example.com",
    "phone": "+1-555-0200",
    "company": "ABC Corp",
    "notes": "Prefers vegetarian options",
    "created_at": "2025-12-13T10:00:00Z",
    "updated_at": "2025-12-13T10:00:00Z"
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Client not found"
}
```

---

#### **4. Update Client** 🔒
```http
PUT /clients/{id}
Authorization: Bearer {token}

Body:
{
  "name": "Updated Client Name",
  "phone": "+1-555-0299",
  "notes": "Updated preferences"
}
```

**Note:** All fields are optional. Only provided fields will be updated.

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "chef_id": 1,
    "name": "Updated Client Name",
    "email": "client@example.com",
    "phone": "+1-555-0299",
    "company": "ABC Corp",
    "notes": "Updated preferences",
    "updated_at": "2025-12-13T11:00:00Z"
  },
  "message": "Client updated successfully"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Client not found"
}
```

---

#### **5. Delete Client** 🔒
```http
DELETE /clients/{id}
Authorization: Bearer {token}
```

**URL Parameters:**
- `id` (integer, required): Client ID

**Success Response (200):**
```json
{
  "success": true,
  "message": "Client deleted successfully"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Client not found"
}
```

---

### 🍽️ **Dish Module** (✅ VALIDATED)

> **Authentication:** All endpoints require Chef authentication (🔒)
> **Cache:** 2 endpoints use caching (⚡)
> 
> **Note:** You can only manage your own dishes. Each dish is automatically assigned to the authenticated chef.

#### **1. Create Dish with Ingredients** 🔒 Chef
```http
POST /dishes
Authorization: Bearer {token}

Body:
{
  "name": "Pasta Carbonara",
  "description": "Classic Italian pasta dish",
  "price": 18.99,
  "category": "Main Course",
  "preparation_steps": "1. Boil pasta...",
  "prep_time": 30,
  "servings": 4,
  "photo_url": "https://res.cloudinary.com/...",
  "ingredients": [
    {
      "name": "Spaghetti",
      "quantity": 400,
      "unit": "g",
      "is_optional": false
    }
  ]
}
```

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "chef_id": 1,
    "name": "Pasta Carbonara",
    "price": 18.99,
    "ingredients": [
      {
        "id": 1,
        "name": "Spaghetti",
        "quantity": 400,
        "unit": "g",
        "is_optional": false
      }
    ]
  },
  "message": "Dish created successfully"
}
```

**Note:** Ingredients cascade delete when dish is deleted.

---

#### **2. List Dishes** 🔒 Chef ⚡
```http
GET /dishes?active_only=true
Authorization: Bearer {token}
```

**Cache:** This endpoint uses service-level caching. Results are cached for 5 minutes and automatically invalidate on dish updates.

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Pasta Carbonara",
      "price": 18.99,
      "category": "Main Course",
      "is_active": 1,
      "ingredients": [...]
    }
  ],
  "message": "Retrieved 1 dishes"
}
```

---

#### **3. Get Dish** 🔒 Chef ⚡
```http
GET /dishes/{id}
Authorization: Bearer {token}
```

**Cache:** This endpoint uses service-level caching. Results are cached for 10 minutes and automatically invalidate on dish updates.

---

#### **4. Update Dish** 🔒 Chef
```http
PUT /dishes/{id}
Authorization: Bearer {token}

Body:
{
  "price": 25.99
}
```

---

#### **5. Delete Dish** 🔒 Chef
```http
DELETE /dishes/{id}
Authorization: Bearer {token}
```

---

### 📋 **Menu Module** (⏳ PENDING)

> **Authentication:** All endpoints require Chef authentication (🔒)
> **Cache:** 2 endpoints use caching (⚡)
> 
> **Note:** You can only manage your own menus. Each menu is automatically assigned to the authenticated chef.

#### **1. Create Menu** 🔒 Chef
```http
POST /menus
Authorization: Bearer {token}

Body:
{
  "name": "Summer Menu 2025",
  "description": "Fresh seasonal dishes",
  "status": "draft",
  "dish_ids": [1, 2, 3]
}
```

**Status Values:**
- `draft` - Menu under construction, not visible (default)
- `published` - Publicly available, active menu
- `archived` - Historical, no longer active
- `seasonal` - Available only during specific dates/seasons

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "chef_id": 1,
    "name": "Summer Menu 2025",
    "description": "Fresh seasonal dishes",
    "status": "draft",
    "created_at": "2025-12-13T10:00:00Z"
  },
  "message": "Menu created successfully"
}
```

---

#### **2. List Menus** 🔒 Chef ⚡
```http
GET /menus?active_only=true
Authorization: Bearer {token}
```

**Query Parameters:**
- `active_only` (boolean): If true, only returns menus with status 'published' or 'seasonal'

**Cache:** This endpoint uses service-level caching. Results are cached for 5 minutes and automatically invalidate on menu updates.

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "chef_id": 1,
      "name": "Summer Menu 2025",
      "description": "Fresh seasonal dishes",
      "status": "published",
      "created_at": "2025-12-13T10:00:00Z",
      "updated_at": "2025-12-13T10:00:00Z",
      "dishes": [
        {
          "dish_id": 1,
          "order_position": 1,
          "dish": {
            "id": 1,
            "name": "Pasta Carbonara",
            "price": "18.99",
            "category": "Main Course",
            "photo_url": "https://example.com/pasta.jpg",
            "is_active": true
          }
        },
        {
          "dish_id": 2,
          "order_position": 2,
          "dish": {
            "id": 2,
            "name": "Tiramisu",
            "price": "8.99",
            "category": "Dessert",
            "photo_url": "https://example.com/tiramisu.jpg",
            "is_active": true
          }
        }
      ],
      "dish_count": 2,
      "total_price": "27.98"
    }
  ],
  "message": "Retrieved 1 menus"
}
```

**Note:** The response now includes:
- `dishes`: Structured array with `dish_id`, `order_position` and complete dish data
- `dish_count`: Total number of dishes in the menu
- `total_price`: Calculated sum of all dish prices

---

#### **3. Get Menu** 🔒 Chef ⚡
```http
GET /menus/{id}
Authorization: Bearer {token}
```

**Cache:** This endpoint uses service-level caching. Results are cached for 10 minutes and automatically invalidate on menu updates.

---

#### **4. Update Menu** 🔒 Chef
```http
PUT /menus/{id}
Authorization: Bearer {token}

Body:published"
}
```

**Note:** All fields are optional. Valid status values: `draft`, `published`, `archived`, `seasonal"name": "Updated Menu Name",
  "status": "inactive"
}
```

---

#### **5. Assign/Reorder Dishes** 🔒 Chef
```http
PUT /menus/{id}/dishes
Authorization: Bearer {token}

Body:
{
  "dishes": [
    {"dish_id": 1, "order_position": 1},
    {"dish_id": 2, "order_position": 2}
  ]
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "dishes": [...]
  },
  "message": "Dishes assigned to menu successfully"
}
```
### 💰 **Quotation Module** (⏳ PENDING)

> **Authentication:** All endpoints require Chef authentication (🔒)
> 
> **Note:** You can only manage your own quotations. Each quotation is automatically assigned to the authenticated chef.

#### **1. Create Quotation** 🔒 Chef
```http
POST /quotations
Authorization: Bearer {token}

Body:
{
  "client_id": 1,
  "menu_id": 1,
  "event_date": "2025-12-25",
  "number_of_people": 50,
  "notes": "Wedding reception",
  "items": [
    {
      "dish_id": 1,
      "item_name": "Pasta Carbonara",
      "description": "Classic Italian pasta",
      "quantity": 50,
      "unit_price": 18.99
    }
  ]
}
```

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "quotation_number": "QT-20251213-001",
    "total_price": 949.50,
    "status": "draft"
  },
  "message": "Quotation created successfully"
}
```

**Auto-generated:** `quotation_number` (format: QT-{date}-{seq})  
**Auto-calculated:** `total_price` from items

---

#### **2. List Quotations** 🔒 Chef
```http
GET /quotations?status=draft
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "chef_id": 1,
      "client_id": 1,
      "menu_id": 1,
      "quotation_number": "QT-1-20251213-001",
      "event_date": "2025-12-25",
      "number_of_people": 50,
      "total_price": "949.50",
      "status": "draft",
      "notes": "Wedding reception",
      "terms_and_conditions": null,
      "created_at": "2025-12-13T10:00:00Z",
      "updated_at": "2025-12-13T10:00:00Z",
      "sent_at": null,
      "responded_at": null,
      "client": {
        "id": 1,
        "name": "John Client",
        "email": "client@example.com",
        "phone": "+1-555-0200",
        "company": "ABC Corp"
      },
      "menu": {
        "id": 1,
        "name": "Summer Menu 2025",
        "description": "Fresh seasonal dishes"
      },
      "items": [
        {
          "id": 1,
          "dish_id": 1,
          "item_name": "Pasta Carbonara",
          "description": "Classic Italian pasta",
          "quantity": 50,
          "unit_price": "18.99",
          "subtotal": "949.50"
        }
      ]
    }
  ],
  "message": "Retrieved 1 quotations"
}
```

**Note:** The response now includes:
- `client`: Complete client data (name, email, phone, company)
- `menu`: Associated menu information
- `items`: Structured array with all fields including calculated `subtotal`

---

#### **3. Get Quotation** 🔒 Chef
```http
GET /quotations/{id}
Authorization: Bearer {token}
```

---

### 📅 **Appointment Module** (⏳ PENDIENTE)

#### **1. Create Appointment** 🔒
```http
POST /appointments
Authorization: Bearer {token}

Body:
{
  "client_id": 1,
  "title": "Menu Consultation",
  "description": "Discuss wedding menu options",
  "scheduled_at": "2025-12-20T14:00:00Z",
  "duration_minutes": 60,
  "location": "Chef Office",
  "notes": "Client prefers vegetarian"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "chef_id": 1,
    "client_id": 1,
    "title": "Menu Consultation",
    "scheduled_at": "2025-12-20T14:00:00Z",
    "duration_minutes": 60,
    "status": "scheduled",
    "created_at": "2025-12-13T10:00:00Z"
  },
  "message": "Appointment created successfully"
}
```

---

#### **2. List Appointments** 🔒 Chef
```http
GET /appointments?status=scheduled&start_date=2025-12-01T00:00:00Z&end_date=2025-12-31T23:59:59Z
Authorization: Bearer {token}
```

**Query Parameters (all optional):**
- `status` (string): Filter by status
  - Values: `scheduled`, `confirmed`, `cancelled`, `completed`
- `start_date` (ISO datetime): Filter appointments after this date
- `end_date` (ISO datetime): Filter appointments before this date
- `upcoming` (boolean): If `true`, returns only future appointments
  - Default: `false`
- `days` (integer): When `upcoming=true`, number of days to look ahead
  - Default: `7`
  - Example: `upcoming=true&days=30` → Next 30 days

**Examples:**
- `GET /appointments` → All your appointments
- `GET /appointments?status=scheduled` → Only scheduled appointments
- `GET /appointments?upcoming=true` → Upcoming 7 days
- `GET /appointments?upcoming=true&days=30` → Upcoming 30 days
- `GET /appointments?start_date=2025-12-01T00:00:00Z&end_date=2025-12-31T23:59:59Z` → December 2025

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "chef_id": 1,
      "client_id": 1,
      "title": "Menu Consultation",
      "description": "Discuss wedding menu options",
      "scheduled_at": "2025-12-20T14:00:00Z",
      "duration_minutes": 60,
      "location": "Chef Office",
      "external_calendar_id": null,
      "external_calendar_provider": null,
      "meeting_url": null,
      "status": "scheduled",
      "notes": "Client prefers vegetarian",
      "cancellation_reason": null,
      "created_at": "2025-12-13T10:00:00Z",
      "updated_at": "2025-12-13T10:00:00Z",
      "cancelled_at": null,
      "completed_at": null,
      "client": {
        "id": 1,
        "name": "John Client",
        "email": "client@example.com",
        "phone": "+1-555-0200",
        "company": "ABC Corp"
      },
      "end_time": "2025-12-20T15:00:00Z"
    }
  ],
  "message": "Retrieved 1 appointments"
}
```

**Note:** The response now includes:
- `client`: Complete client data (name, email, phone, company)
- `end_time`: Automatically calculated as `scheduled_at + duration_minutes`

---

#### **3. Get Appointment** 🔒 Chef
```http
GET /appointments/{id}
Authorization: Bearer {token}
```

---

#### **4. Update Appointment** 🔒 Chef
```http
PUT /appointments/{id}
Authorization: Bearer {token}

Body:
{
  "duration_minutes": 90,
  "notes": "Extended consultation"
}
```

---

#### **5. Update Status** 🔒 Chef
```http
PATCH /appointments/{id}/status
Authorization: Bearer {token}

Body:
{
  "status": "confirmed"
}
```

**Valid statuses:**
- scheduled
- confirmed
- cancelled
- completed

---

#### **6. Delete Appointment** 🔒 Chef
```http
DELETE /appointments/{id}
Authorization: Bearer {token}
```
```

**Note:** Only `draft` quotations can be updated/deleted.

#### **5. Update Status** 🔒
```http
PATCH /quotations/{id}/status
Authorization: Bearer {token}

Body:
{
  "status": "sent"
}
```

**Valid transitions:**
- draft → sent, expired
- sent → accepted, rejected, expired
- accepted → expired

#### **6. Delete Quotation** 🔒 Chef
```http
DELETE /quotations/{id}
Authorization: Bearer {token}
```

---

### 📅 **Appointment Module** (⏳ PENDIENTE)

> **Autenticación:** Todos los endpoints requieren autenticación como Chef (🔒)
> 
> **Nota:** Solo puedes gestionar tus propias citas. Cada cita se asigna automáticamente al chef autenticado.

#### **1. Create Appointment** 🔒 Chef
```http
POST /appointments
Authorization: Bearer {token}

Body:
{
  "client_id": 1,
  "title": "Menu Tasting Session",
  "description": "Discuss wedding menu",
  "scheduled_at": "2025-12-15T14:00:00",
  "duration_minutes": 90,
  "location": "Chef's Kitchen",
  "meeting_url": "https://zoom.us/j/123",
### 🛒 **Scraper Module** (⏳ PENDING)

> **Authentication:** All endpoints require Chef authentication (🔒)
> 
> **Note:** This module allows you to configure price sources (supermarkets) and perform web scraping to obtain ingredient prices.

#### **1. List Price Sources** 🔒 Chef
```http
GET /scrapers/sources?active_only=true
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Walmart",
      "base_url": "https://walmart.com",
      "search_url_template": "https://walmart.com/search?q={ingredient}",
      "is_active": true,
      "created_at": "2025-12-13T10:00:00Z"
    }
  ]
}
```

---

#### **2. Get Price Source** 🔒 Chef
```http
GET /scrapers/sources/{id}
Authorization: Bearer {token}
```

---

#### **3. Create Price Source** 🔒 Chef
```http
POST /scrapers/sources
Authorization: Bearer {token}

Body:
{
  "name": "Walmart",
  "base_url": "https://walmart.com",
  "search_url_template": "https://walmart.com/search?q={ingredient}",
  "product_name_selector": ".product-title",
  "price_selector": ".price",
  "image_selector": ".product-img",
  "is_active": true,
  "notes": "Main grocery store"
}
```

---

#### **4. Update Price Source** 🔒 Chef
```http
PUT /scrapers/sources/{id}
Authorization: Bearer {token}

Body:
{
  "name": "Updated Store Name",
  "is_active": false
}
```

---

#### **5. Delete Price Source** 🔒 Chef
```http
DELETE /scrapers/sources/{id}
Authorization: Bearer {token}
```

---

#### **6. Scrape Ingredient Prices** 🔒 Chef
```http
POST /scrapers/scrape
Authorization: Bearer {token}

Body:
{
  "ingredient": "tomatoes",
  "source_id": 1
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "ingredient": "tomatoes",
    "prices": [
      {
        "product_name": "Fresh Tomatoes",
        "price": 3.99,
        "url": "https://walmart.com/product/123",
        "image_url": "https://walmart.com/image.jpg"
      }
    ]
  }
}
```

---

#### **7. Get Scraped Prices** 🔒 Chef
```http
GET /scrapers/prices?ingredient=tomatoes&source_id=1&days=7
Authorization: Bearer {token}
```

**Query params:**
- `ingredient` (string): Filtrar por ingrediente
- `source_id` (int): Filtrar por fuente
- `days` (int): Últimos N días

---

#### **8. Compare Prices** 🔒 Chef
```http
GET /scrapers/prices/compare?ingredient=tomatoes
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "ingredient": "tomatoes",
    "comparison": [
      {
        "source": "Walmart",
        "price": 3.99,
        "url": "https://walmart.com/..."
      },
      {
        "source": "Target",
        "price": 4.29,
        "url": "https://target.com/..."
      }
    ],
    "best_price": {
      "source": "Walmart",
      "price": 3.99
    }
  }
}
```

---

#### **9. Cleanup Old Prices** 🔒 Chef
```http
DELETE /scrapers/prices/cleanup?days_old=30
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "deleted_count": 150
  },
  "message": "Old prices cleaned up successfully"
}
```
      "id": 1,
      "price_source_id": 1,
      "ingredient_name": "rice",
      "product_name": "White Rice 5lb",
      "price": "8.99",
      "currency": "USD",
      "product_url": "https://...",
      "image_url": "https://...",
      "unit": "5lb bag",
      "scraped_at": "2025-11-27T10:00:00"
    }
  ],
  "message": "Found 2 price(s) for 'rice'"
}
```

---

#### **7. Get Scraped Prices History** 🔒
```http
GET /scrapers/prices?ingredient_name=rice&max_age_hours=48
Authorization: Bearer {token}
```

**Query params:**
- `ingredient_name` (string): Filtrar por ingrediente
- `price_source_id` (int): Filtrar por fuente
## 🌍 Public Module (⏳ PENDING)

> **Authentication:** None of these endpoints require authentication (🌐 Public)
> **Cache:** 2 endpoints use caching (⚡)
> 
> **Note:** These endpoints are designed so anonymous visitors can explore available chefs, menus, and dishes.

#### **1. List Chefs** 🌐 Public
```http
GET /public/chefs?page=1&per_page=10&specialty=Italian&location=Miami&search=pasta
```

**Query Parameters:**
- `page`: Número de página (default: 1)
- `per_page`: Items por página (default: 10)
- `specialty`: Filtrar por especialidad
- `location`: Filtrar por ubicación
- `search`: Búsqueda por texto

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "chefs": [
      {
        "id": 1,
        "bio": "Passionate chef...",
        "specialty": "Italian Cuisine",
        "location": "Miami, FL",
        "dish_count": 15,
        "menu_count": 3
      }
    ],
    "pagination": {
      "total": 25,
      "page": 1,
      "per_page": 10,
      "pages": 3
    }
  }
}
```

---

#### **2. Get Chef Profile** 🌐 Public ⚡
```http
GET /public/chefs/{id}
```

**Cache:** This endpoint uses route-level caching. Results are cached for 10 minutes.

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "chef": {
      "id": 1,
      "bio": "Passionate chef...",
      "specialty": "Italian Cuisine",
      "location": "Miami, FL"
    },
    "dishes": [...],
    "menus": [...],
    "stats": {
      "total_dishes": 15,
      "total_menus": 3
    }
  }
}
```

---

#### **3. Search Chefs** 🌐 Public
```http
GET /public/search?q=pasta&page=1&per_page=10
```

**Query Parameters:**
- `q`: Search query (minimum 3 characters)
- `page`: Page number
- `per_page`: Items per page

---

#### **4. Get Filters** 🌐 Public
```http
GET /public/filters
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "specialties": [
      "Italian Cuisine",
      "French Cuisine",
      "Mexican Cuisine"
    ],
    "locations": [ Use these endpoints instead of the deprecated `/chefs` routes.

#### **1. List Chefs** 🌐 Public ⚡
```http
GET /public/chefs?page=1&per_page=10&specialty=Italian&location=Miami&search=pasta
```

**Cache:** This endpoint uses route-level caching. Results are cached for 5 minutes.
}
```

---

#### **5. Get Menu Details** 🌐 Public
```http
GET /public/menus/{id}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "menu": {
      "id": 1,
      "name": "Summer Menu 2025",
      "description": "Fresh seasonal dishes"
    },
    "chef": {
      "id": 1,
      "specialty": "Italian Cuisine"
    },
    "dishes": [...]
  }
}
```

---

#### **6. Get Dish Details** 🌐 Public
```http
GET /public/dishes/{id}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "dish": {
      "id": 1,
      "name": "Pasta Carbonara",
      "description": "Classic Italian pasta",
      "price": 18.99,
      "ingredients": [...]
    },
    "chef": {
      "id": 1,
      "specialty": "Italian Cuisine"
    }
  }
}
```
        "description": "Traditional Italian dessert",
        "price": 8.99,
        "order_position": 2
      }
    ]
  },
  "message": "Menu retrieved successfully"
}
```

**Note:** Los platos vienen ordenados según `order_position`.

---

#### **6. Get Dish Details**
```http
GET /public/dishes/{dish_id}
```

**Response:**
```json
{
  "data": {
    "dish": {
      "id": 1,
      "name": "Spaghetti Carbonara",
      "description": "Classic Roman pasta with eggs, cheese, and guanciale",
      "category": "Main Course",
      "price": 18.99,
      "preparation_time": 20,
      "serves": 2,
      "is_available": true,
      "ingredients": [
        {
          "name": "Spaghetti",
          "quantity": 200,
          "unit": "g"
        },
        {
          "name": "Eggs",
          "quantity": 3,
          "unit": "units"
        }
      ]
    },
    "chef": {
      "id": 1,
      "name": "Mario Rossi",
      "specialty": "Italian Cuisine",
      "location": "Miami, FL"
    }
  },
  "message": "Dish retrieved successfully"
}
```

**Note:** Incluye información completa del plato y del chef que lo prepara.

---

## 👑 Admin Module (✅ IMPLEMENTED)

> **Authentication:** All endpoints require Admin authentication (👑)
> 
> **Note:** Administrators have full system access for supervision, management, and moderation of all resources. Complete implementation documentation: [ADMIN_PHASE3_COMPLETED.md](../backend/docs/ADMIN_PHASE3_COMPLETED.md)

### 🎯 Admin Module Purpose

Admin endpoints are designed for:
- **Supervision**: Centralized monitoring of all chefs and activities
- **Moderation**: Activate/deactivate problematic accounts
- **Analytics**: System-wide metrics and statistics
- **Support**: User assistance without compromising security
- **Audit**: Tracking of all administrative actions

---

#### **1. Admin Dashboard** 👑 Admin
```http
GET /admin/dashboard
Authorization: Bearer {admin_token}
```

**Purpose:** Overview with key system metrics

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "statistics": {
      "total_chefs": 150,
      "active_chefs": 142,
      "inactive_chefs": 8,
      "total_clients": 856,
      "total_dishes": 1243,
      "total_menus": 387,
      "total_quotations": 524,
      "total_appointments": 892
    },
    "recent_activity": {
      "new_chefs_last_7_days": 5,
      "new_clients_last_7_days": 23,
      "quotations_last_7_days": 18
    },
    "top_chefs": [
      {
        "chef_id": 1,
        "username": "chef_mario",
        "total_clients": 45,
        "total_dishes": 32,
        "total_quotations": 67
      }
    ]
  },
  "message": "Dashboard data retrieved successfully"
}
```

**Cache:** 5 minutes

---

#### **2. List All Chefs (Admin View)** 👑 Admin
```http
GET /admin/chefs?page=1&per_page=20&status=all&search=mario&sort=created_at&order=desc
Authorization: Bearer {admin_token}
```

**Purpose:** View ALL chefs with advanced filters (unlike GET /chefs which is public)

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20, max: 100)
- `status` (string): "active" | "inactive" | "all" (default: "all")
- `search` (string): Search by username, email, specialty
- `sort` (string): "created_at" | "username" | "total_clients" (default: "created_at")
- `order` (string): "asc" | "desc" (default: "desc")

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "chefs": [
      {
        "id": 1,
        "bio": "Passionate Italian chef with 10+ years experience",
        "specialty": "Italian Cuisine",
        "phone": "+1-555-0100",
        "location": "Miami, FL",
        "is_active": true,
        "created_at": "2025-10-01T10:00:00Z",
        "user": {
          "id": 1,
          "username": "chef_mario",
          "email": "mario@example.com",
          "role": "chef"
        },
        "stats": {
          "total_clients": 45,
          "total_dishes": 32,
          "total_menus": 8,
          "total_quotations": 67
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "pages": 8
    }
  },
  "message": "Retrieved 150 chefs"
}
```

---

#### **3. Get Chef Details (Admin View)** 👑 Admin
```http
GET /admin/chefs/{id}
Authorization: Bearer {admin_token}
```

**Purpose:** View complete profile of any chef with all statistics

**URL Parameters:**
- `id` (integer, required): Chef ID

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "chef": {
      "id": 1,
      "bio": "Passionate Italian chef...",
      "specialty": "Italian Cuisine",
      "phone": "+1-555-0100",
      "location": "Miami, FL",
      "is_active": true,
      "created_at": "2025-10-01T10:00:00Z",
      "updated_at": "2025-12-10T15:30:00Z",
      "user": {
        "id": 1,
        "username": "chef_mario",
        "email": "mario@example.com",
        "role": "chef"
      }
    },
    "statistics": {
      "total_clients": 45,
      "total_dishes": 32,
      "active_dishes": 30,
      "total_menus": 8,
      "active_menus": 6,
      "total_quotations": 67,
      "quotations_by_status": {
        "draft": 5,
        "sent": 12,
        "accepted": 38,
        "rejected": 10,
        "expired": 2
      },
      "total_appointments": 89,
      "appointments_by_status": {
        "scheduled": 8,
        "confirmed": 15,
        "completed": 62,
        "cancelled": 4
      }
    },
    "recent_activity": {
      "last_login": "2025-12-13T08:30:00Z",
      "last_dish_created": "2025-12-12T14:20:00Z",
      "last_quotation_sent": "2025-12-11T10:15:00Z"
    }
  },
  "message": "Chef details retrieved successfully"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Chef not found"
}
```

---

#### **4. Update Chef Status** 👑 Admin
```http
PATCH /admin/chefs/{id}/status
Authorization: Bearer {admin_token}

Body:
{
  "is_active": false,
  "reason": "Terms of service violation"
}
```

**Purpose:** Activate/deactivate chef account

**Request Body:**
- `is_active` (boolean, required): true to activate, false to deactivate
- `reason` (string, optional): Reason for status change

**Business Rules:**
- Deactivating chef does NOT delete their data
- Deactivated chef CANNOT login
- Chef's public data remains visible but marked as "inactive"
- Action is logged in audit logs

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "chef_id": 1,
    "is_active": false,
    "updated_at": "2025-12-13T10:30:00Z"
  },
  "message": "Chef account deactivated successfully"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Chef not found"
}
```

---

#### **5. List All Users** 👑 Admin
```http
GET /admin/users?page=1&per_page=20&role=all&status=active
Authorization: Bearer {admin_token}
```

**Purpose:** Complete user management system

**Query Parameters:**
- `page` (int): Número de página (default: 1)
- `per_page` (int): Items por página (default: 20, max: 100)
- `role` (string): "chef" | "admin" | "all" (default: "all")
- `status` (string): "active" | "inactive" | "all" (default: "all")
- `search` (string): Búsqueda por username o email

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "username": "chef_mario",
        "email": "mario@example.com",
        "role": "chef",
        "is_active": true,
        "has_chef_profile": true,
        "created_at": "2025-10-01T10:00:00Z",
        "last_login": "2025-12-13T08:30:00Z"
      },
      {
        "id": 2,
        "username": "admin_user",
        "email": "admin@lyftercook.com",
        "role": "admin",
        "is_active": true,
        "has_chef_profile": false,
        "created_at": "2025-09-01T09:00:00Z",
        "last_login": "2025-12-13T09:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 151,
      "pages": 8
    }
  },
  "message": "Retrieved 151 users"
}
```

---

#### **6. Delete User** 👑 Admin
```http
DELETE /admin/users/{id}
Authorization: Bearer {admin_token}

Body:
{
  "confirm": true,
  "reason": "Account deletion requested by user"
}
```

**Purpose:** Delete user from system (soft delete)

**⚠️ Business Rules:**
- SOFT DELETE: Mark as deleted, do not physically delete
- Admin CANNOT delete themselves
- Must have at least 1 active admin in the system
- Cascade: delete associated chef profile if exists

**Request Body:**
- `confirm` (boolean, required): Must be true to confirm
- `reason` (string, optional): Reason for deletion

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "deleted_at": "2025-12-13T10:30:00Z"
  },
  "message": "User deleted successfully"
}

**Note:** This endpoint returns `user_id` instead of the complete object as it's a deletion operation.
```

**Error Responses:**

403 Forbidden - Intento de auto-eliminación:
```json
{
  "success": false,
  "error": "Cannot delete your own account"
}
```

403 Forbidden - Último admin:
```json
{
  "success": false,
  "error": "Cannot delete the last active admin"
}
```

400 Bad Request - Confirmación faltante:
```json
{
  "success": false,
  "error": "Confirmation required. Set 'confirm' to true"
}
```

---

#### **7. System Reports** 👑 Admin
```http
GET /admin/reports?report_type=activity&start_date=2025-11-01T00:00:00Z&end_date=2025-11-30T23:59:59Z&format=json
Authorization: Bearer {admin_token}
```

**Purpose:** System reports and analysis

**Query Parameters:**
- `report_type` (string, required): "chefs" | "activity" | "revenue" | "quotations"
- `start_date` (ISO datetime, required): Fecha inicio del periodo
- `end_date` (ISO datetime, required): Fecha fin del periodo
- `format` (string): "json" | "csv" (default: "json")

**Success Response (200) - Activity Report:**
```json
{
  "success": true,
  "data": {
    "report_type": "activity",
    "period": {
      "start": "2025-11-01T00:00:00Z",
      "end": "2025-11-30T23:59:59Z"
    },
    "metrics": {
      "new_users": 12,
      "new_chefs": 10,
      "new_clients": 89,
      "dishes_created": 156,
      "menus_created": 34,
      "quotations_sent": 78,
      "quotations_accepted": 45,
      "appointments_scheduled": 123,
      "appointments_completed": 98
    },
    "trends": {
      "user_growth_rate": "+8.5%",
      "quotation_acceptance_rate": "57.7%",
      "appointment_completion_rate": "79.7%"
    }
  },
  "message": "Activity report generated successfully"
}
```

---

#### **8. Audit Logs** 👑 Admin
```http
GET /admin/audit-logs?page=1&per_page=50&admin_id=2&action_type=deactivate_chef
Authorization: Bearer {admin_token}
```

**Purpose:** Tracking of all administrative actions

**Query Parameters:**
- `page` (int): Número de página (default: 1)
- `per_page` (int): Items por página (default: 50, max: 200)
- `admin_id` (int): Filtrar por admin específico
- `action_type` (string): Tipo de acción ("deactivate_chef", "delete_user", etc.)
- `start_date` (ISO datetime): Fecha inicio
- `end_date` (ISO datetime): Fecha fin

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": 1,
        "admin_id": 2,
        "admin_username": "admin_user",
        "action": "deactivate_chef",
        "target_type": "chef",
        "target_id": 5,
        "reason": "Terms of service violation",
        "ip_address": "192.168.1.100",
        "created_at": "2025-12-13T10:30:00Z"
      },
      {
        "id": 2,
        "admin_id": 2,
        "admin_username": "admin_user",
        "action": "delete_user",
        "target_type": "user",
        "target_id": 23,
        "reason": "User request",
        "ip_address": "192.168.1.100",
        "created_at": "2025-12-12T15:20:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 50,
      "total": 234,
      "pages": 5
    }
  },
  "message": "Retrieved 234 audit logs"
}
```

**Logged Actions:**
- `deactivate_chef` / `activate_chef`
- `delete_user`
- `view_chef_details` (para compliance)
- `generate_report`
- `view_audit_logs`
- `view_audit_statistics`
- Cualquier acción admin se registra automáticamente

---

#### **9. Audit Statistics** 👑 Admin
```http
GET /admin/audit-logs/statistics
Authorization: Bearer {admin_token}
```

**Purpose:** Aggregated audit log statistics

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "total_logs": 1247,
    "recent_logs_7_days": 156,
    "logs_by_action": {
      "view_dashboard": 423,
      "view_all_chefs": 287,
      "view_chef_details": 189,
      "deactivate_chef": 12,
      "activate_chef": 8,
      "view_all_users": 145,
      "delete_user": 5,
      "generate_report": 89,
      "view_audit_logs": 67,
      "view_audit_statistics": 22
    },
    "top_admins": [
      {
        "admin_id": 2,
        "username": "admin_user",
        "action_count": 834
      },
      {
        "admin_id": 3,
        "username": "admin_supervisor",
        "action_count": 413
      }
    ]
  },
  "message": "Audit statistics retrieved successfully"
}
```

**Metrics Included:**
- Total logs count
- Recent activity (last 7 days)
- Actions grouped by type
- TOP 5 most active admins

---

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "message": "Detailed error description"
}
```

### Validation Error
```json
{
  "success": false,
  "error": "Validation failed",
  "details": {
    "email": ["Invalid email format"],
    "password": ["Password too short"]
  }
}
```

---

## 🔑 Token Authentication Summary

**To get the token:**

1. Register: `POST /auth/register` → Creates account with `chef` role by default
2. Login: `POST /auth/login` → Returns JWT token
3. Use the token: Include in header `Authorization: Bearer {token}` for all 🔒 endpoints

**Icon legend:**
- 🌐 **Public**: No authentication required, anyone can access
- 🔒 **Chef**: Requires chef authentication (valid JWT token)
- 👑 **Admin**: Requires admin authentication (JWT token + admin role)
- ⚡ **Cached**: Endpoint uses caching for improved performance

**Important notes:**
- Token expires in 24 hours
- Each chef only sees/manages their own resources (clients, dishes, menus, etc.)
- Admins can view/manage resources from ALL chefs
- To create content, an admin must have a separate chef profile
- All admin actions are logged in audit logs
- Cached endpoints (⚡) provide faster responses after the first request

---

**Last Updated:** December 28, 2025  
**API Version:** 1.0.0  
**Total Endpoints:** 60 (9 public + 40 chef + 11 admin)  
**Cached Endpoints:** 8 (marked with ⚡)  
**Status:** 60 endpoints implemented and tested ✅ (110 tests passing)