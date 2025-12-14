# 🍳 LyfterCook API Documentation

## 📋 Base URL

```
Development: http://localhost:5000
Production: https://api.lyftercook.com (TBD)
```

---

## 🔐 Authentication

All protected endpoints require a JWT token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

**Token expiration:** 24 hours

---

## 📊 Testing Status

| Módulo | Endpoints | Tests | Estado Tests | Validación Usuario | Última Actualización |
|--------|-----------|-------|--------------|-------------------|----------------------|
| Auth | 3 | 16 | ✅ **100%** | ✅ **VALIDADO** | 2025-12-13 |
| Chef | 5 | 3 | ✅ **100%** | ⏳ **PENDIENTE** | 2025-12-13 |
| Client | 5 | 8 | ✅ **100%** | ⏳ **PENDIENTE** | 2025-12-13 |
| Dish | 5 | 10 | ✅ **100%** | ⏳ **PENDIENTE** | 2025-12-13 |
| Menu | 6 | 9 | ✅ **100%** | ⏳ **PENDIENTE** | 2025-12-13 |
| Quotation | 6 | 6 | ✅ **100%** | ⏳ **PENDIENTE** | 2025-12-13 |
| Appointment | 6 | 12 | ✅ **100%** | ⏳ **PENDIENTE** | 2025-12-13 |
| Scraper | 9 | 14 | ✅ **100%** | ⏳ **PENDIENTE** | 2025-12-13 |
| Public | 6 | 15 | ✅ **100%** | ⏳ **PENDIENTE** | 2025-12-13 |

**Total Implementado:** 51 endpoints | **Total Tests:** 93 (100% passing) | **Validados Manualmente:** 1/9 módulos

---

## 📍 Endpoints Overview

| Method | Endpoint | Auth | Status |
|--------|----------|------|--------|
| **AUTH MODULE** |||
| `POST` | `/auth/register` | Public | ✅ Implemented & Tested |
| `POST` | `/auth/login` | Public | ✅ Implemented & Tested |
| `GET` | `/auth/me` | 🔒 Protected | ✅ Implemented & Tested |
| **CHEF MODULE** |||
| `POST` | `/chefs/profile` | 🔒 Protected | ✅ Implemented |
| `GET` | `/chefs/profile` | 🔒 Protected | ✅ Implemented |
| `PUT` | `/chefs/profile` | 🔒 Protected | ✅ Implemented |
| `GET` | `/chefs` | Public | ✅ Implemented |
| `GET` | `/chefs/:id` | Public | ✅ Implemented |
| **CLIENT MODULE** |||
| `POST` | `/clients` | 🔒 Protected | ✅ Implemented |
| `GET` | `/clients` | 🔒 Protected | ✅ Implemented |
| `GET` | `/clients/:id` | 🔒 Protected | ✅ Implemented |
| `PUT` | `/clients/:id` | 🔒 Protected | ✅ Implemented |
| `DELETE` | `/clients/:id` | 🔒 Protected | ✅ Implemented |
| **DISH MODULE** |||
| `POST` | `/dishes` | 🔒 Protected | ✅ Implemented |
| `GET` | `/dishes` | 🔒 Protected | ✅ Implemented |
| `GET` | `/dishes/:id` | 🔒 Protected | ✅ Implemented |
| `PUT` | `/dishes/:id` | 🔒 Protected | ✅ Implemented |
| `DELETE` | `/dishes/:id` | 🔒 Protected | ✅ Implemented |
| **MENU MODULE** |||
| `POST` | `/menus` | 🔒 Protected | ✅ Implemented |
| `GET` | `/menus` | 🔒 Protected | ✅ Implemented |
| `GET` | `/menus/:id` | 🔒 Protected | ✅ Implemented |
| `PUT` | `/menus/:id` | 🔒 Protected | ✅ Implemented |
| `PUT` | `/menus/:id/dishes` | 🔒 Protected | ✅ Implemented |
| `DELETE` | `/menus/:id` | 🔒 Protected | ✅ Implemented |
| **QUOTATION MODULE** |||
| `POST` | `/quotations` | 🔒 Protected | ✅ Implemented |
| `GET` | `/quotations` | 🔒 Protected | ✅ Implemented |
| `GET` | `/quotations/:id` | 🔒 Protected | ✅ Implemented |
| `PUT` | `/quotations/:id` | 🔒 Protected | ✅ Implemented |
| `PATCH` | `/quotations/:id/status` | 🔒 Protected | ✅ Implemented |
| `DELETE` | `/quotations/:id` | 🔒 Protected | ✅ Implemented |
| **APPOINTMENT MODULE** |||
| `POST` | `/appointments` | 🔒 Protected | ✅ Implemented |
| `GET` | `/appointments` | 🔒 Protected | ✅ Implemented |
| `GET` | `/appointments/:id` | 🔒 Protected | ✅ Implemented |
| `PUT` | `/appointments/:id` | 🔒 Protected | ✅ Implemented |
| `PATCH` | `/appointments/:id/status` | 🔒 Protected | ✅ Implemented |
| `DELETE` | `/appointments/:id` | 🔒 Protected | ✅ Implemented |
| **SCRAPER MODULE** |||
| `POST` | `/scrapers/sources` | 🔒 Protected | ✅ Implemented |
| `GET` | `/scrapers/sources` | 🔒 Protected | ✅ Implemented |
| `GET` | `/scrapers/sources/:id` | 🔒 Protected | ✅ Implemented |
| `PUT` | `/scrapers/sources/:id` | 🔒 Protected | ✅ Implemented |
| `DELETE` | `/scrapers/sources/:id` | 🔒 Protected | ✅ Implemented |
| `POST` | `/scrapers/scrape` | 🔒 Protected | ✅ Implemented |
| `GET` | `/scrapers/prices` | 🔒 Protected | ✅ Implemented |
| `GET` | `/scrapers/prices/compare` | 🔒 Protected | ✅ Implemented |
| `DELETE` | `/scrapers/prices/cleanup` | 🔒 Protected | ✅ Implemented |
| **PUBLIC MODULE** |||
| `GET` | `/public/chefs` | Public | ✅ Implemented |
| `GET` | `/public/chefs/:id` | Public | ✅ Implemented |
| `GET` | `/public/search` | Public | ✅ Implemented |
| `GET` | `/public/filters` | Public | ✅ Implemented |
| `GET` | `/public/menus/:id` | Public | ✅ Implemented |
| `GET` | `/public/dishes/:id` | Public | ✅ Implemented |

---

## 📍 API Endpoints Details

### 🔐 **Auth Module** (✅ VALIDADO)

#### **1. Register User**
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

#### **2. Login**
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

#### **3. Get Current User** 🔒 Protected
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

### 👨‍🍳 **Chef Module** (⏳ PENDIENTE)

#### **1. Create Chef Profile** 🔒
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
    "user_id": 1,
    "bio": "Passionate chef with 10 years...",
    "specialty": "Italian Cuisine",
    "phone": "+1-555-0100",
    "location": "Miami, FL",
    "is_active": true,
    "created_at": "2025-12-13T10:00:00Z"
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

#### **2. Get My Profile** 🔒
```http
GET /chefs/profile
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 1,
    "bio": "Passionate chef...",
    "specialty": "Italian Cuisine",
    "phone": "+1-555-0100",
    "location": "Miami, FL",
    "is_active": true,
    "created_at": "2025-12-13T10:00:00Z",
    "updated_at": "2025-12-13T10:00:00Z"
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

#### **3. Update My Profile** 🔒
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
    "user_id": 1,
    "bio": "Updated bio text",
    "specialty": "French Cuisine",
    "phone": "+1-555-0199",
    "location": "Los Angeles, CA",
    "is_active": true
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

#### **4. List All Chefs** (Public)
```http
GET /chefs?include_inactive=false
```

**Query Parameters:**
- `include_inactive` (boolean, optional): If `true`, returns both active and inactive chefs. Default: `false` (only active)

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "bio": "Passionate chef...",
      "specialty": "Italian Cuisine",
      "phone": "+1-555-0100",
      "location": "Miami, FL",
      "is_active": true
    },
    {
      "id": 2,
      "user_id": 2,
      "bio": "French cuisine expert",
      "specialty": "French Cuisine",
      "phone": "+1-555-0101",
      "location": "New York, NY",
      "is_active": true
    }
  ],
  "message": "Retrieved 2 chef profiles"
}
```

**Examples:**
- `GET /chefs` → Returns only active chefs
- `GET /chefs?include_inactive=false` → Returns only active chefs
- `GET /chefs?include_inactive=true` → Returns all chefs (active + inactive)

---

#### **5. Get Chef by ID** (Public)
```http
GET /chefs/{id}
```

**URL Parameters:**
- `id` (integer, required): Chef profile ID

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 1,
    "bio": "Passionate chef...",
    "specialty": "Italian Cuisine",
    "phone": "+1-555-0100",
    "location": "Miami, FL",
    "is_active": true,
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com"
    },
    "created_at": "2025-12-13T10:00:00Z",
    "updated_at": "2025-12-13T10:00:00Z"
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

### 🧑‍💼 **Client Module** (⏳ PENDIENTE)

#### **1. Create Client** 🔒
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

#### **2. List Clients** 🔒
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

#### **3. Get Client by ID** 🔒
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

### 🍽️ **Dish Module** (⏳ PENDIENTE)

#### **1. Create Dish with Ingredients** 🔒
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

#### **2. List Dishes** 🔒
```http
GET /dishes?active_only=true
Authorization: Bearer {token}
```

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

#### **3. Get Dish** 🔒
```http
GET /dishes/{id}
Authorization: Bearer {token}
```

---

#### **4. Update Dish** 🔒
```http
PUT /dishes/{id}
Authorization: Bearer {token}

Body:
{
  "price": 25.99,
  "is_active": 1
}
```

---

#### **5. Delete Dish** 🔒
```http
DELETE /dishes/{id}
Authorization: Bearer {token}
### 📋 **Menu Module** (⏳ PENDIENTE)

#### **1. Create Menu** 🔒
```http
POST /menus
Authorization: Bearer {token}

Body:
{
  "name": "Summer Menu 2025",
  "description": "Fresh seasonal dishes",
  "status": "active",
  "dish_ids": [1, 2, 3]
}
```

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "chef_id": 1,
    "name": "Summer Menu 2025",
    "description": "Fresh seasonal dishes",
    "status": "active",
    "created_at": "2025-12-13T10:00:00Z"
  },
  "message": "Menu created successfully"
}
```

---

#### **2. List Menus** 🔒
```http
GET /menus?active_only=true
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Summer Menu 2025",
      "status": "active",
      "dishes": [
        {
          "id": 1,
          "name": "Pasta Carbonara",
          "price": 18.99,
          "order_position": 1
        }
      ]
    }
  ],
  "message": "Retrieved 1 menus"
}
```

---

#### **3. Get Menu** 🔒
```http
GET /menus/{id}
Authorization: Bearer {token}
```

---

#### **4. Update Menu** 🔒
```http
PUT /menus/{id}
Authorization: Bearer {token}

Body:
{
  "name": "Updated Menu Name",
  "status": "inactive"
}
```

---

#### **5. Assign/Reorder Dishes** 🔒
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
### 💰 **Quotation Module** (⏳ PENDIENTE)

#### **1. Create Quotation** 🔒
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

#### **2. List Quotations** 🔒
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
      "quotation_number": "QT-20251213-001",
      "total_price": 550.00,
      "status": "draft",
      "event_date": "2025-12-25",
      "number_of_people": 50
    }
  ]
}
```

---

#### **3. Get Quotation** 🔒
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

#### **2. List Appointments** 🔒
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
      "status": "scheduled",
      "notes": "Client prefers vegetarian",
      "created_at": "2025-12-13T10:00:00Z"
    }
  ],
  "message": "Retrieved 1 appointments"
}
```

---

#### **3. Get Appointment** 🔒
```http
GET /appointments/{id}
Authorization: Bearer {token}
```

---

#### **4. Update Appointment** 🔒
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

#### **5. Update Status** 🔒
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

#### **6. Delete Appointment** 🔒
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

#### **6. Delete Quotation** 🔒
```http
DELETE /quotations/{id}
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
  "title": "Menu Tasting Session",
  "description": "Discuss wedding menu",
  "scheduled_at": "2025-12-15T14:00:00",
  "duration_minutes": 90,
  "location": "Chef's Kitchen",
  "meeting_url": "https://zoom.us/j/123",
### 🛒 **Scraper Module** (⏳ PENDIENTE)

Este módulo permite configurar fuentes de precios (supermercados) y realizar web scraping para obtener precios de ingredientes.

#### **1. List Price Sources** 🔒
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

#### **2. Get Price Source** 🔒
```http
GET /scrapers/sources/{id}
Authorization: Bearer {token}
```

---

#### **3. Create Price Source** 🔒
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

#### **4. Update Price Source** 🔒
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

#### **5. Delete Price Source** 🔒
```http
DELETE /scrapers/sources/{id}
Authorization: Bearer {token}
```

---

#### **6. Scrape Ingredient Prices** 🔒
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

#### **7. Get Scraped Prices** 🔒
```http
GET /scrapers/prices?ingredient=tomatoes&source_id=1&days=7
Authorization: Bearer {token}
```

**Query params:**
- `ingredient` (string): Filtrar por ingrediente
- `source_id` (int): Filtrar por fuente
- `days` (int): Últimos N días

---

#### **8. Compare Prices** 🔒
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

#### **9. Cleanup Old Prices** 🔒
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
## 🌍 Public Module (⏳ PENDIENTE)

Endpoints públicos sin autenticación requerida.

#### **1. List Chefs**
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

#### **2. Get Chef Profile**
```http
GET /public/chefs/{id}
```

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

#### **3. Search Chefs**
```http
GET /public/search?q=pasta&page=1&per_page=10
```

**Query Parameters:**
- `q`: Query de búsqueda (mínimo 3 caracteres)
- `page`: Número de página
- `per_page`: Items por página

---

#### **4. Get Filters**
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
    "locations": [
      "Miami, FL",
      "New York, NY",
      "Los Angeles, CA"
    ]
  }
}
```

---

#### **5. Get Menu Details**
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

#### **6. Get Dish Details**
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

**Last Updated:** December 13, 2025  
**API Version:** 1.0.0  
**Total Endpoints:** 51  
**Status:** All modules tested ✅ (93 tests passing)
---

## 🔑 Authentication

Todos los endpoints protegidos requieren un header de autenticación:

```
Authorization: Bearer <token>
```

El token se obtiene del endpoint `POST /auth/login`.

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

**Last Updated:** December 13, 2025  
**API Version:** 1.0.0  
**Total Endpoints:** 53  
**Status:** All modules tested ✅ (93 tests passing)