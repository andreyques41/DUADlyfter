# 🧪 Chef Endpoints Testing Guide

Guía completa para probar los endpoints del módulo Chef en Postman.

## 📋 Prerequisites

1. **Servidor ejecutándose**: `python run.py` en `backend/`
2. **Base de datos inicializada**: `python scripts/init_db.py`
3. **Usuario registrado**: Necesitas un token JWT

---

## 🔐 Step 1: Get JWT Token

### Register a new user
```
POST http://localhost:5000/auth/register

Headers:
Content-Type: application/json

Body (JSON):
{
  "username": "john_chef",
  "email": "john@example.com",
  "password": "SecurePass123!"
}

Expected Response (201):
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "username": "john_chef",
    "email": "john@example.com",
    "role": "chef"
  }
}
```

### Login
```
POST http://localhost:5000/auth/login

Headers:
Content-Type: application/json

Body (JSON):
{
  "username": "john_chef",
  "password": "SecurePass123!"
}

Expected Response (200):
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "user": {
      "id": 1,
      "username": "john_chef",
      "email": "john@example.com",
      "role": "chef"
    }
  }
}
```

**💾 Save the `access_token` - lo necesitarás para los siguientes requests!**

---

## 👨‍🍳 Step 2: Create Chef Profile

```
POST http://localhost:5000/chefs/profile

Headers:
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Body (JSON):
{
  "bio": "Passionate chef with 10 years of experience in Italian cuisine. Specialized in traditional pasta and contemporary fusion dishes.",
  "specialty": "Italian Cuisine",
  "phone": "+1-555-0123",
  "location": "New York, NY"
}

Expected Response (201):
{
  "success": true,
  "message": "Chef profile created successfully",
  "data": {
    "id": 1,
    "user_id": 1,
    "bio": "Passionate chef with 10 years of experience...",
    "specialty": "Italian Cuisine",
    "phone": "+1-555-0123",
    "location": "New York, NY",
    "is_active": true,
    "created_at": "2025-11-27T08:30:00",
    "updated_at": "2025-11-27T08:30:00",
    "user": {
      "id": 1,
      "username": "john_chef",
      "email": "john@example.com"
    }
  }
}
```

**Error Cases:**
- **400**: Profile already exists (if you try to create twice)
- **401**: Missing or invalid token
- **400**: Invalid phone format

---

## 📖 Step 3: Get My Profile

```
GET http://localhost:5000/chefs/profile

Headers:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Expected Response (200):
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 1,
    "bio": "Passionate chef with 10 years of experience...",
    "specialty": "Italian Cuisine",
    "phone": "+1-555-0123",
    "location": "New York, NY",
    "is_active": true,
    "created_at": "2025-11-27T08:30:00",
    "updated_at": "2025-11-27T08:30:00",
    "user": {
      "id": 1,
      "username": "john_chef",
      "email": "john@example.com"
    }
  }
}
```

**Error Cases:**
- **404**: Profile not found (if you haven't created one yet)
- **401**: Missing or invalid token

---

## ✏️ Step 4: Update My Profile

```
PUT http://localhost:5000/chefs/profile

Headers:
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Body (JSON) - All fields optional:
{
  "bio": "Award-winning chef specializing in modern Italian fusion. 15+ years experience.",
  "specialty": "Italian Fusion",
  "phone": "+1-555-9999",
  "location": "Brooklyn, NY",
  "is_active": true
}

Expected Response (200):
{
  "success": true,
  "message": "Chef profile updated successfully",
  "data": {
    "id": 1,
    "user_id": 1,
    "bio": "Award-winning chef specializing in modern Italian fusion...",
    "specialty": "Italian Fusion",
    "phone": "+1-555-9999",
    "location": "Brooklyn, NY",
    "is_active": true,
    "created_at": "2025-11-27T08:30:00",
    "updated_at": "2025-11-27T08:35:00",
    "user": {
      "id": 1,
      "username": "john_chef",
      "email": "john@example.com"
    }
  }
}
```

**Partial Update Example:**
```json
{
  "phone": "+1-555-7777"
}
```
Only updates the phone, other fields remain unchanged.

**Error Cases:**
- **404**: Profile not found
- **401**: Missing or invalid token
- **400**: Invalid data (e.g., phone format)

---

## 🌍 Step 5: Public Endpoints (No Auth Required)

### Get All Chefs
```
GET http://localhost:5000/chefs

No headers required (public endpoint)

Expected Response (200):
{
  "success": true,
  "message": "Retrieved 3 chef profiles",
  "data": [
    {
      "id": 1,
      "bio": "Award-winning chef specializing in modern Italian fusion...",
      "specialty": "Italian Fusion",
      "location": "Brooklyn, NY",
      "user": {
        "id": 1,
        "username": "john_chef"
      }
    },
    {
      "id": 2,
      "bio": "French pastry expert with Michelin star experience...",
      "specialty": "French Pastry",
      "location": "Paris, France",
      "user": {
        "id": 2,
        "username": "marie_pastry"
      }
    }
  ]
}
```

**Query Parameters:**
- `include_inactive=true` - Include inactive chef profiles

Example:
```
GET http://localhost:5000/chefs?include_inactive=true
```

### Get Specific Chef by ID
```
GET http://localhost:5000/chefs/1

No headers required (public endpoint)

Expected Response (200):
{
  "success": true,
  "data": {
    "id": 1,
    "bio": "Award-winning chef specializing in modern Italian fusion...",
    "specialty": "Italian Fusion",
    "location": "Brooklyn, NY",
    "user": {
      "id": 1,
      "username": "john_chef"
    }
  }
}
```

**Error Cases:**
- **404**: Chef not found or inactive

---

## 🔄 Complete Testing Flow

### Scenario 1: New User Journey
1. ✅ Register user → Get user data
2. ✅ Login → Get JWT token
3. ✅ Create chef profile → Get profile data
4. ✅ Get my profile → Verify data
5. ✅ Update profile → Verify changes
6. ✅ View public list → See your profile in list
7. ✅ View public detail → See your full public profile

### Scenario 2: Multiple Chefs
1. ✅ Register 2-3 different users
2. ✅ Create chef profiles for each
3. ✅ Get all chefs → Verify all appear
4. ✅ Get specific chef by ID → Verify individual profiles

### Scenario 3: Error Handling
1. ❌ Try to create profile twice → Should get 400 (already exists)
2. ❌ Try to get profile without token → Should get 401
3. ❌ Try to update non-existent profile → Should get 404
4. ❌ Try invalid phone format → Should get 400

---

## 📝 Postman Environment Variables

Create a Postman environment with:

```
BASE_URL = http://localhost:5000
TOKEN = (will be set after login)
```

Then use:
- `{{BASE_URL}}/chefs/profile`
- `{{TOKEN}}` in Authorization header

---

## 🐛 Common Issues

### 401 Unauthorized
- Token expired (JWT has 24h expiration)
- Token not included in Authorization header
- Wrong format (must be `Bearer <token>`)

### 404 Not Found
- Chef profile not created yet (create it first)
- Wrong chef ID in URL
- Chef is inactive (for public endpoints)

### 400 Bad Request
- Invalid JSON format
- Phone validation failed
- Profile already exists (for POST)
- Missing required fields

### 500 Internal Server Error
- Database connection issue
- Check server logs for details

---

## ✅ Expected Cache Behavior

After successful operations, check server logs for:
```
[CACHE MISS] auth:token:user:<token>
[CACHE HIT] auth:token:user:<token>
```

Cache should work after first request with same token.

---

## 🎯 Next Steps After Testing

Once all endpoints work:
1. ✅ Auth module → Working
2. ✅ Chef module → Working
3. 🔜 Clients module → Next
4. 🔜 Dishes module → After clients
5. 🔜 Menus module → After dishes

Happy testing! 🚀
