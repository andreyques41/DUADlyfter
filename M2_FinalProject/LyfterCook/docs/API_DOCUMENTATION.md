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
| Scraper | 9 | ⏳ **PENDIENTE** | - |
| Public | 6 | ⏳ **PENDIENTE** | - |

**Total Implementado:** 53 endpoints | **Validados:** 3 | **Pendientes de Testing:** 50

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

### 🛒 **Scraper Module** (⏳ PENDIENTE)

Este módulo permite configurar fuentes de precios (supermercados, sitios web) y realizar web scraping automático para obtener precios de ingredientes.

#### **Características:**
- Configuración flexible de fuentes con CSS selectors personalizados
- Cache de precios (24 horas por defecto)
- Comparación de precios entre múltiples fuentes
- Extracción automática de precios, nombres de productos e imágenes
- Limpieza automática de datos antiguos

---

#### **1. Create Price Source** 🔒
```http
POST /scrapers/sources
Authorization: Bearer {token}

Body:
{
  "name": "Walmart",
  "base_url": "https://www.walmart.com",
  "search_url_template": "https://www.walmart.com/search?q={ingredient}",
  "product_name_selector": ".product-title",
  "price_selector": ".price-main .price-characteristic",
  "image_selector": ".product-image img",
  "is_active": true,
  "notes": "Main grocery source"
}
```

**Validation:**
- `search_url_template` debe contener `{ingredient}` o `{query}` como placeholder
- CSS selectors son requeridos para name y price

**Response (201):**
```json
{
  "data": {
    "id": 1,
    "name": "Walmart",
    "base_url": "https://www.walmart.com",
    "is_active": true,
    "created_at": "2025-11-27T10:00:00"
  },
  "message": "Price source created successfully"
}
```

---

#### **2. List Price Sources** 🔒
```http
GET /scrapers/sources?active_only=true
Authorization: Bearer {token}
```

**Query params:**
- `active_only` (boolean): Solo fuentes activas

---

#### **3. Get Price Source** 🔒
```http
GET /scrapers/sources/{id}
Authorization: Bearer {token}
```

---

#### **4. Update Price Source** 🔒
```http
PUT /scrapers/sources/{id}
Authorization: Bearer {token}

Body:
{
  "is_active": false,
  "notes": "Temporarily disabled"
}
```

---

#### **5. Delete Price Source** 🔒
```http
DELETE /scrapers/sources/{id}
Authorization: Bearer {token}
```

**Note:** Elimina en cascada todos los precios scrapeados de esta fuente.

---

#### **6. Scrape Ingredient Prices** 🔒
```http
POST /scrapers/scrape
Authorization: Bearer {token}

Body:
{
  "ingredient_name": "rice",
  "price_source_ids": [1, 2],  // Optional: specific sources
  "force_refresh": false       // Optional: bypass cache
}
```

**Behavior:**
- Sin `price_source_ids`: usa todas las fuentes activas
- `force_refresh: false`: usa cache si tiene menos de 24 horas
- `force_refresh: true`: scrapea datos frescos ignorando cache

**Response (200):**
```json
{
  "data": [
    {
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
- `max_age_hours` (int): Solo precios recientes (default: 24)

---

#### **8. Get Price Comparison** 🔒
```http
GET /scrapers/prices/compare?ingredient_name=rice
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "data": {
    "ingredient_name": "rice",
    "found": true,
    "total_sources": 3,
    "min_price": 8.99,
    "max_price": 12.50,
    "avg_price": 10.16,
    "prices": [
      {
        "source_id": 1,
        "product_name": "White Rice 5lb",
        "price": 8.99,
        "url": "https://...",
        "scraped_at": "2025-11-27T10:00:00"
      }
    ]
  }
}
```

**Use case:** Encontrar el mejor precio para un ingrediente.

---

#### **9. Cleanup Old Prices** 🔒
```http
DELETE /scrapers/prices/cleanup?days_old=30
Authorization: Bearer {token}
```

**Response:**
```json
{
  "data": {
    "deleted_count": 145
  },
  "message": "Deleted 145 old price records"
}
```

**Note:** Mantiene la base de datos limpia eliminando datos antiguos.

---

## 🔓 Public - Páginas Públicas

**Base URL:** `/public`

**Descripción:** Endpoints de acceso público para que los clientes descubran chefs, menús y platos sin necesidad de autenticación. Ideal para landing pages y búsqueda de servicios.

**Características:**
- ✅ Sin autenticación requerida
- ✅ Paginación automática
- ✅ Filtrado por especialidad y ubicación
- ✅ Búsqueda por texto
- ✅ Respuestas agregadas (chef + platos + menús)

---

#### **1. List Chefs**
```http
GET /public/chefs?page=1&per_page=10&specialty=Italian&location=Miami&search=pasta
```

**Query Parameters:**
- `page` (opcional): Número de página (default: 1)
- `per_page` (opcional): Items por página (1-100, default: 10)
- `specialty` (opcional): Filtrar por especialidad del chef
- `location` (opcional): Filtrar por ubicación
- `search` (opcional): Buscar en nombre, bio, especialidad

**Response:**
```json
{
  "data": {
    "chefs": [
      {
        "id": 1,
        "name": "Mario Rossi",
        "email": "mario@lyfter.com",
        "phone": "+1-555-0101",
        "location": "Miami, FL",
        "specialty": "Italian Cuisine",
        "bio": "Authentic Italian recipes from Tuscany",
        "is_active": true
      }
    ],
    "total": 25,
    "page": 1,
    "per_page": 10,
    "total_pages": 3
  },
  "message": "Chefs retrieved successfully"
}
```

---

#### **2. Get Chef Profile**
```http
GET /public/chefs/{chef_id}
```

**Response:**
```json
{
  "data": {
    "chef": {
      "id": 1,
      "name": "Mario Rossi",
      "email": "mario@lyfter.com",
      "phone": "+1-555-0101",
      "location": "Miami, FL",
      "specialty": "Italian Cuisine",
      "bio": "Authentic Italian recipes from Tuscany",
      "is_active": true
    },
    "dishes": [
      {
        "id": 1,
        "name": "Spaghetti Carbonara",
        "description": "Classic Roman pasta",
        "category": "Main Course",
        "price": 18.99,
        "preparation_time": 20,
        "serves": 2,
        "is_available": true
      }
    ],
    "menus": [
      {
        "id": 1,
        "name": "Italian Night Menu",
        "description": "3-course Italian dinner",
        "total_price": 55.00,
        "serves": 2,
        "status": "active"
      }
    ],
    "stats": {
      "total_dishes": 12,
      "total_menus": 3
    }
  },
  "message": "Chef profile retrieved successfully"
}
```

**Note:** Incluye perfil completo del chef con todos sus platos y menús activos.

---

#### **3. Search Chefs**
```http
GET /public/search?q=pasta
```

**Query Parameters:**
- `q` (requerido): Término de búsqueda (mínimo 2 caracteres)
- `page` (opcional): Número de página (default: 1)
- `per_page` (opcional): Items por página (default: 10)

**Response:**
```json
{
  "data": {
    "chefs": [
      {
        "id": 1,
        "name": "Mario Rossi",
        "specialty": "Italian Cuisine",
        "location": "Miami, FL"
      }
    ],
    "total": 5,
    "page": 1,
    "per_page": 10,
    "total_pages": 1
  },
  "message": "Search results retrieved"
}
```

**Note:** Busca en nombre del chef, bio y especialidad (case-insensitive).

---

#### **4. Get Available Filters**
```http
GET /public/filters
```

**Response:**
```json
{
  "data": {
    "specialties": [
      "Italian Cuisine",
      "French Cuisine",
      "Mexican Cuisine",
      "Asian Fusion"
    ],
    "locations": [
      "Miami, FL",
      "New York, NY",
      "Los Angeles, CA"
    ]
  },
  "message": "Filters retrieved successfully"
}
```

**Note:** Útil para poblar filtros dinámicos en el frontend.

---

#### **5. Get Menu Details**
```http
GET /public/menus/{menu_id}
```

**Response:**
```json
{
  "data": {
    "menu": {
      "id": 1,
      "name": "Italian Night Menu",
      "description": "3-course Italian dinner",
      "total_price": 55.00,
      "serves": 2,
      "status": "active"
    },
    "chef": {
      "id": 1,
      "name": "Mario Rossi",
      "specialty": "Italian Cuisine",
      "location": "Miami, FL"
    },
    "dishes": [
      {
        "id": 1,
        "name": "Spaghetti Carbonara",
        "description": "Classic Roman pasta",
        "price": 18.99,
        "order_position": 1
      },
      {
        "id": 2,
        "name": "Tiramisu",
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

**Last Updated:** November 27, 2025  
**API Version:** 1.0.0  
**Status:** Phase 1 Complete ✅
