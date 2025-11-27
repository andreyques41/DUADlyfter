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

| Módulo | Endpoints | Estado Testing | Última Validación |
|--------|-----------|----------------|-------------------|
| Auth | 3 | ✅ **VALIDADO** | 2025-11-27 |
| Chef | 7 | ⏳ **PENDIENTE** | - |
| Client | 5 | ⏳ **PENDIENTE** | - |
| Dish | 5 | ⏳ **PENDIENTE** | - |
| Menu | 6 | ⏳ **PENDIENTE** | - |
| Quotation | 6 | ⏳ **PENDIENTE** | - |
| Appointment | 6 | ⏳ **PENDIENTE** | - |

**Total Implementado:** 38 endpoints | **Validados:** 3 | **Pendientes de Testing:** 35

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
| `PATCH` | `/chefs/profile/activate` | 🔒 Protected | ✅ Implemented |
| `PATCH` | `/chefs/profile/deactivate` | 🔒 Protected | ✅ Implemented |
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

Ver documentación completa de testing en: **`backend/docs/CHEF_ENDPOINTS_TESTING.md`**

#### Endpoints Summary:
- `POST /chefs/profile` - Crear perfil de chef
- `GET /chefs/profile` - Ver mi perfil (privado)
- `PUT /chefs/profile` - Actualizar perfil
- `PATCH /chefs/profile/activate` - Activar perfil
- `PATCH /chefs/profile/deactivate` - Desactivar perfil
- `GET /chefs` - Listar chefs públicos
- `GET /chefs/:id` - Ver perfil público de chef

---

### 🧑‍💼 **Client Module** (⏳ PENDIENTE)

#### **1. Create Client** 🔒
```http
POST /clients
Authorization: Bearer {token}

Body:
{
  "name": "Maria Garcia",
  "email": "maria@example.com",
  "phone": "+1234567890",
  "company": "Tech Corp",
  "notes": "Prefers vegetarian options"
}
```

#### **2. List Clients** 🔒
```http
GET /clients
Authorization: Bearer {token}
```

#### **3. Get Client** 🔒
```http
GET /clients/{id}
Authorization: Bearer {token}
```

#### **4. Update Client** 🔒
```http
PUT /clients/{id}
Authorization: Bearer {token}

Body:
{
  "notes": "Updated preferences"
}
```

#### **5. Delete Client** 🔒
```http
DELETE /clients/{id}
Authorization: Bearer {token}
```

---

### 🍽️ **Dish Module** (⏳ PENDIENTE)

#### **1. Create Dish with Ingredients** 🔒
```http
POST /dishes
Authorization: Bearer {token}

Body:
{
  "name": "Paella Valenciana",
  "description": "Traditional Spanish rice dish",
  "price": 45.50,
  "category": "Main Course",
  "prep_time": 60,
  "servings": 4,
  "is_active": true,
  "ingredients": [
    {
      "name": "Rice",
      "quantity": "500",
      "unit": "g",
      "is_optional": false
    }
  ]
}
```

**Note:** Ingredients cascade delete when dish is deleted.

#### **2. List Dishes** 🔒
```http
GET /dishes?active_only=true
Authorization: Bearer {token}
```

#### **3. Get Dish** 🔒
```http
GET /dishes/{id}
Authorization: Bearer {token}
```

#### **4. Update Dish** 🔒
```http
PUT /dishes/{id}
Authorization: Bearer {token}

Body:
{
  "price": 48.00,
  "ingredients": [...]  // Replaces all ingredients
}
```

#### **5. Delete Dish** 🔒
```http
DELETE /dishes/{id}
Authorization: Bearer {token}
```

---

### 📋 **Menu Module** (⏳ PENDIENTE)

#### **1. Create Menu** 🔒
```http
POST /menus
Authorization: Bearer {token}

Body:
{
  "name": "Summer Wedding Menu 2025",
  "description": "Elegant menu for summer weddings",
  "status": "active",
  "dish_ids": [1, 2, 3]
}
```

#### **2. List Menus** 🔒
```http
GET /menus?active_only=true
Authorization: Bearer {token}
```

#### **3. Get Menu** 🔒
```http
GET /menus/{id}
Authorization: Bearer {token}
```

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

#### **5. Assign/Reorder Dishes** 🔒
```http
PUT /menus/{id}/dishes
Authorization: Bearer {token}

Body:
{
  "dishes": [
    {"dish_id": 3, "order_position": 0},
    {"dish_id": 1, "order_position": 1}
  ]
}
```

#### **6. Delete Menu** 🔒
```http
DELETE /menus/{id}
Authorization: Bearer {token}
```

---

### 💰 **Quotation Module** (⏳ PENDIENTE)

#### **1. Create Quotation** 🔒
```http
POST /quotations
Authorization: Bearer {token}

Body:
{
  "client_id": 1,
  "menu_id": 1,
  "event_date": "2025-12-15",
  "number_of_people": 50,
  "notes": "Wedding reception",
  "items": [
    {
      "dish_id": 1,
      "item_name": "Paella Valenciana",
      "quantity": 50,
      "unit_price": 45.50
    }
  ]
}
```

**Auto-generated:** `quotation_number` (format: QT-{chef_id}-{date}-{seq})  
**Auto-calculated:** `total_price` from items

#### **2. List Quotations** 🔒
```http
GET /quotations?status=draft
Authorization: Bearer {token}
```

#### **3. Get Quotation** 🔒
```http
GET /quotations/{id}
Authorization: Bearer {token}
```

#### **4. Update Quotation** 🔒
```http
PUT /quotations/{id}
Authorization: Bearer {token}

Body:
{
  "event_date": "2025-12-20",
  "items": [...]
}
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
  "notes": "Client prefers vegetarian"
}
```

#### **2. List Appointments** 🔒
```http
GET /appointments?upcoming=true&days=7
Authorization: Bearer {token}
```

**Query params:**
- `status`: scheduled|confirmed|cancelled|completed|no_show
- `start_date`: ISO datetime
- `end_date`: ISO datetime
- `upcoming`: true (next 7 days)
- `days`: number (with upcoming=true)

#### **3. Get Appointment** 🔒
```http
GET /appointments/{id}
Authorization: Bearer {token}
```

#### **4. Update Appointment** 🔒
```http
PUT /appointments/{id}
Authorization: Bearer {token}

Body:
{
  "scheduled_at": "2025-12-15T15:00:00",
  "duration_minutes": 120
}
```

**Note:** Cannot update completed/cancelled appointments.

#### **5. Update Status** 🔒
```http
PATCH /appointments/{id}/status
Authorization: Bearer {token}

Body:
{
  "status": "confirmed",
  "cancellation_reason": "Optional"
}
```

**Valid transitions:**
- scheduled → confirmed, cancelled
- confirmed → completed, cancelled, no_show

#### **6. Delete Appointment** 🔒
```http
DELETE /appointments/{id}
Authorization: Bearer {token}
```

**Note:** Cannot delete completed appointments.





---

## ⚠️ HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Successful GET/PUT request |
| 201 | Created - Successful POST (resource created) |
| 400 | Bad Request - Validation errors or invalid input |
| 401 | Unauthorized - Missing/invalid token or wrong credentials |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error - Check logs |

---

**Last Updated:** November 26, 2025  
**API Version:** 1.0.0  
**Status:** Phase 1 Complete ✅
