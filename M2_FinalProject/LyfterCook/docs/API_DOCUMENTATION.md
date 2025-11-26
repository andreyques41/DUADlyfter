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

## 📍 Endpoints Overview

| Method | Endpoint | Auth | Status |
|--------|----------|------|--------|
| `POST` | `/auth/register` | Public | ✅ Implemented |
| `POST` | `/auth/login` | Public | ✅ Implemented |
| `GET` | `/auth/me` | 🔒 Protected | ✅ Implemented |
| `GET` | `/chefs` | Public | ⏳ Planned |
| `GET` | `/chefs/:id` | Public | ⏳ Planned |
| `PUT` | `/chefs/profile` | 🔒 Protected | ⏳ Planned |
| `GET` | `/clients` | 🔒 Protected | ⏳ Planned |
| `POST` | `/clients` | 🔒 Protected | ⏳ Planned |
| `PUT` | `/clients/:id` | 🔒 Protected | ⏳ Planned |
| `DELETE` | `/clients/:id` | 🔒 Protected | ⏳ Planned |
| `GET` | `/dishes` | 🔒 Protected | ⏳ Planned |
| `POST` | `/dishes` | 🔒 Protected | ⏳ Planned |
| `PUT` | `/dishes/:id` | 🔒 Protected | ⏳ Planned |
| `DELETE` | `/dishes/:id` | 🔒 Protected | ⏳ Planned |
| `GET` | `/menus` | 🔒 Protected | ⏳ Planned |
| `POST` | `/menus` | 🔒 Protected | ⏳ Planned |
| `GET` | `/quotations` | 🔒 Protected | ⏳ Planned |
| `POST` | `/quotations` | 🔒 Protected | ⏳ Planned |
| `GET` | `/appointments` | 🔒 Protected | ⏳ Planned |
| `POST` | `/appointments` | Public/Protected | ⏳ Planned |

---

## 📍 API Endpoints

### **Auth Module** ✅ IMPLEMENTED

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
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImNoZWZfam9obiIsInJvbGUiOiJjaGVmIiwiZXhwIjoxNzMyNjU2NDAwLCJpYXQiOjE3MzI1NzAwMDB9.xyz",
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
