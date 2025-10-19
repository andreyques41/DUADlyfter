# 🚀 Pet E-commerce API - Guía de Rutas

**Base URL:** `http://localhost:8000`  
**Formato:** JSON  
**Autenticación:** JWT Bearer Token

---

## 📑 Tabla de Contenidos

- [🔐 Autenticación](#-autenticación)
- [👤 Usuarios](#-usuarios)
- [🛍️ Productos](#️-productos)
- [🛒 Carrito de Compras](#-carrito-de-compras)
- [📦 Órdenes](#-órdenes)
- [💳 Facturas](#-facturas)
- [🔄 Devoluciones](#-devoluciones)

---

## 🔐 Autenticación

### 1. Registro de Usuario
**POST** `/auth/register`

**Acceso:** Público (sin autenticación)

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "roles": ["user"]
}
```

**Campos:**
- `username` (string, requerido): 3-50 caracteres
- `email` (string, requerido): Email válido
- `password` (string, requerido): Mínimo 8 caracteres
- `first_name` (string, opcional): Máximo 50 caracteres
- `last_name` (string, opcional): Máximo 50 caracteres
- `phone` (string, opcional): Máximo 20 caracteres
- `role` (string, opcional): "user" o "admin" (default: "user")

**Response 201 Created:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "roles": ["user"],
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
  }
}
```

---

### 2. Login
**POST** `/auth/login`

**Acceso:** Público (sin autenticación)

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securepass123"
}
```

**Response 200 OK:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "roles": ["user"]
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Nota:** Guarda el `token` para usarlo en requests autenticados.

---

## 👤 Usuarios

### 3. Listar Todos los Usuarios
**GET** `/auth/users`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
[
  {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "roles": ["user"],
    "first_name": "John",
    "last_name": "Doe"
  },
  {
    "id": 2,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "first_name": "Admin",
    "last_name": "User"
  }
]
```

---

### 4. Ver Perfil de Usuario
**GET** `/auth/users/{user_id}`

**Acceso:** 🔒 Usuario autenticado (solo su propio perfil) o Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "roles": ["user"],
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

---

### 5. Actualizar Perfil
**PUT** `/auth/users/{user_id}`

**Acceso:** 🔒 Usuario autenticado (solo su propio perfil) o Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "first_name": "Jonathan",
  "last_name": "Doe Updated",
  "phone": "+9876543210",
  "email": "newemail@example.com"
}
```

**Response 200 OK:**
```json
{
  "message": "User updated successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "newemail@example.com",
    "roles": ["user"],
    "first_name": "Jonathan",
    "last_name": "Doe Updated",
    "phone": "+9876543210"
  }
}
```

---

### 6. Ver Roles de Usuario
**GET** `/auth/users/{user_id}/roles`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "user_id": 1,
  "username": "johndoe",
  "roles": ["user"]
}
```

**Nota:** Los usuarios pueden tener múltiples roles (ej: `["user", "admin"]`).

---

### 7. Asignar Rol a Usuario
**POST** `/auth/users/{user_id}/roles`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "role": "admin"
}
```

**Roles disponibles:**
- `user` - Usuario regular
- `admin` - Administrador

**Response 200 OK:**
```json
{
  "message": "Role 'admin' assigned successfully",
  "user_id": 1,
  "username": "johndoe",
  "roles": ["user", "admin"]
}
```

**Errores posibles:**
- **404**: Usuario no encontrado
- **400**: Rol inválido
- **409**: Usuario ya tiene ese rol

---

### 8. Remover Rol de Usuario
**DELETE** `/auth/users/{user_id}/roles`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "role": "admin"
}
```

**Response 200 OK:**
```json
{
  "message": "Role 'admin' removed successfully",
  "user_id": 1,
  "username": "johndoe",
  "roles": ["user"]
}
```

**Errores posibles:**
- **404**: Usuario no encontrado o no tiene ese rol
- **400**: No se puede remover el último rol (usuarios deben tener al menos un rol)

---

### 9. Cambiar Contraseña
**PUT** `/auth/users/{user_id}`

**Acceso:** 🔒 Usuario autenticado (solo su propia contraseña)

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456",
  "confirm_password": "newpassword456"
}
```

**Response 200 OK:**
```json
{
  "message": "Password updated successfully"
}
```

---

### 10. Eliminar Usuario
**DELETE** `/auth/users/{user_id}`

**Acceso:** 🔒 Usuario autenticado (solo su propia cuenta) o Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "message": "User deleted successfully"
}
```

---

## 🛍️ Productos

### 11. Listar Todos los Productos
**GET** `/products`

**Acceso:** Público (sin autenticación)

**Query Parameters (opcionales):**
- `category` (string): "food", "toys", "accessories", "health", "grooming"
- `pet_type` (string): "dog", "cat", "bird", "fish", "reptile", "other"
- `min_price` (float): Precio mínimo
- `max_price` (float): Precio máximo

**Ejemplos:**
```
GET /products
GET /products?category=food
GET /products?pet_type=dog
GET /products?category=toys&pet_type=cat
GET /products?min_price=10&max_price=50
```

**Response 200 OK:**
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
    "weight": 15.0,
    "is_active": true
  },
  {
    "id": 2,
    "sku": "CAT02",
    "description": "Interactive Cat Toy",
    "category": "toys",
    "pet_type": "cat",
    "stock_quantity": 100,
    "price": 12.50,
    "brand": "FunPets",
    "is_active": true
  }
]
```

---

### 12. Ver Detalle de Producto
**GET** `/products/{product_id}`

**Acceso:** Público (sin autenticación)

**Response 200 OK:**
```json
{
  "id": 1,
  "sku": "DOG01",
  "description": "Premium Dog Food 15kg",
  "category": "food",
  "pet_type": "dog",
  "stock_quantity": 50,
  "price": 45.99,
  "cost": 30.00,
  "brand": "PetNutrition",
  "weight": 15.0,
  "supplier": "Pet Distributors Inc",
  "is_active": true
}
```

---

### 13. Crear Producto
**POST** `/products`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "sku": "DOG03",
  "description": "Organic Dog Treats",
  "category": "food",
  "pet_type": "dog",
  "stock_quantity": 200,
  "price": 15.99,
  "cost": 8.50,
  "brand": "OrganicPets",
  "weight": 0.5,
  "supplier": "Organic Foods Co",
  "is_active": true
}
```

**Campos requeridos:**
- `sku`: Código único de 5 caracteres
- `description`: Descripción del producto
- `category`: Categoría del producto
- `pet_type`: Tipo de mascota
- `stock_quantity`: Cantidad en inventario
- `price`: Precio de venta

**Response 201 Created:**
```json
{
  "message": "Product created successfully",
  "product": {
    "id": 3,
    "sku": "DOG03",
    "description": "Organic Dog Treats",
    "category": "food",
    "pet_type": "dog",
    "price": 15.99
  }
}
```

---

### 14. Actualizar Producto
**PUT** `/products/{product_id}`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "price": 17.99,
  "stock_quantity": 250,
  "is_active": true
}
```

**Response 200 OK:**
```json
{
  "message": "Product updated successfully",
  "product": {
    "id": 3,
    "sku": "DOG03",
    "price": 17.99,
    "stock_quantity": 250
  }
}
```

---

### 15. Eliminar Producto
**DELETE** `/products/{product_id}`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "message": "Product deleted successfully"
}
```

---

## 🛒 Carrito de Compras

### 16. Listar Carritos
**GET** `/sales/carts`

**Acceso:** 🔒 Usuario autenticado

**Comportamiento basado en rol (REST standard):**
- **Usuario regular:** Ve solo su propio carrito
- **Admin:** Ve todos los carritos del sistema

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK (Admin):**
```json
{
  "total_carts": 2,
  "carts": [
    {
      "id": 1,
      "user_id": 1,
      "username": "johndoe",
      "items_count": 3,
      "total": 104.48,
      "created_at": "2025-10-16T20:00:00"
    },
    {
      "id": 2,
      "user_id": 2,
      "username": "janedoe",
      "items_count": 1,
      "total": 45.99,
      "created_at": "2025-10-16T21:00:00"
    }
  ]
}
```

**Response 200 OK (Usuario):**
```json
{
  "id": 1,
  "user_id": 1,
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "Premium Dog Food 15kg",
      "quantity": 2,
      "unit_price": 45.99,
      "amount": 91.98
    }
  ],
  "total": 104.48,
  "created_at": "2025-10-16T20:00:00"
}
```

---

### 17. Crear Carrito
**POST** `/sales/carts`

**Acceso:** 🔒 Usuario autenticado

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "user_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

**Campos Requeridos:**
- `user_id` (integer, min=1): ID del usuario propietario
- `items` (array, min=1, max=100): Lista de ítems del carrito
  - `product_id` (integer, min=1): ID del producto
  - `quantity` (integer, min=1, max=50): Cantidad del producto

**Response 201 Created:**
```json
{
  "message": "Cart created successfully",
  "cart": {
    "id": 1,
    "user_id": 1,
    "items": [
      {
        "id": 1,
        "product_id": 1,
        "product_name": "Premium Dog Food 15kg",
        "quantity": 2,
        "unit_price": 45.99,
        "amount": 91.98
      }
    ],
    "total": 91.98,
    "item_count": 2,
    "created_at": "2025-10-16T20:00:00"
  }
}
```

---

### 18. Ver Carrito Específico
**GET** `/sales/carts/{user_id}`

**Acceso:** 🔒 Usuario autenticado (solo su propio carrito) o Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "id": 1,
  "user_id": 1,
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "Premium Dog Food 15kg",
      "quantity": 2,
      "unit_price": 45.99,
      "amount": 91.98
    },
    {
      "id": 2,
      "product_id": 2,
      "product_name": "Interactive Cat Toy",
      "quantity": 1,
      "unit_price": 12.50,
      "amount": 12.50
    }
  ],
  "total": 104.48,
  "created_at": "2025-10-16T20:00:00"
}
```

---

### 19. Actualizar Carrito
**PUT** `/sales/carts/{user_id}`

**Acceso:** 🔒 Usuario autenticado (solo su propio carrito) o Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 3
    },
    {
      "product_id": 2,
      "quantity": 1
    }
  ]
}
```

**Response 200 OK:**
```json
{
  "message": "Cart updated successfully",
  "cart": {
    "id": 1,
    "user_id": 1,
    "items": [...],
    "total": 150.97
  }
}
```

---

### 20. Vaciar Carrito
**DELETE** `/sales/carts/{user_id}`

**Acceso:** 🔒 Usuario autenticado (solo su propio carrito) o Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "message": "Cart cleared successfully"
}
```

---

### 21. Agregar Item al Carrito
**POST** `/sales/carts/{user_id}/items/{product_id}`

**Acceso:** 🔒 Usuario autenticado (solo su propio carrito) o Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "quantity": 2
}
```

**Response 201 Created:**
```json
{
  "message": "Item added to cart",
  "cart_item": {
    "id": 3,
    "product_id": 3,
    "quantity": 2,
    "unit_price": 17.99
  }
}
```

---

### 22. Actualizar Cantidad en Carrito
**PUT** `/sales/carts/{user_id}/items/{product_id}`

**Acceso:** 🔒 Usuario autenticado (solo su propio carrito) o Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "quantity": 5
}
```

**Response 200 OK:**
```json
{
  "message": "Cart item updated",
  "cart_item": {
    "id": 3,
    "product_id": 3,
    "quantity": 5,
    "unit_price": 17.99
  }
}
```

---

### 23. Eliminar Item del Carrito
**DELETE** `/sales/carts/{user_id}/items/{product_id}`

**Acceso:** 🔒 Usuario autenticado (solo su propio carrito) o Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "message": "Item removed from cart"
}
```

---

## 📦 Órdenes

### 24. Listar Órdenes
**GET** `/sales/orders`

**Acceso:** 🔒 Usuario autenticado

**Comportamiento basado en rol (REST standard):**
- **Usuario regular:** Ve solo sus propias órdenes
- **Admin:** Ve todas las órdenes del sistema

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters (opcionales):**
- `status` (string): "pending", "confirmed", "processing", "shipped", "delivered", "cancelled"

**Ejemplo:**
```
GET /sales/orders
GET /sales/orders?status=pending
```

**Response 200 OK:**
```json
{
  "total_orders": 5,
  "orders": [
    {
      "id": 1,
      "user_id": 1,
      "username": "johndoe",
      "cart_id": 1,
      "status": "confirmed",
      "total_price": 104.48,
      "items": [
        {
          "product_id": 1,
          "product_name": "Premium Dog Food 15kg",
          "quantity": 2,
          "unit_price": 45.99
        }
      ],
      "created_at": "2025-10-16T20:30:00",
      "updated_at": "2025-10-16T20:35:00"
    }
  ]
}
```

---

### 25. Ver Detalle de Orden
**GET** `/sales/orders/{order_id}`

**Acceso:** 🔒 Usuario autenticado (solo su propia orden) o Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "id": 1,
  "user_id": 1,
  "username": "johndoe",
  "cart_id": 1,
  "status": "confirmed",
  "total_price": 104.48,
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "Premium Dog Food 15kg",
      "quantity": 2,
      "unit_price": 45.99,
      "amount": 91.98
    },
    {
      "id": 2,
      "product_id": 2,
      "product_name": "Interactive Cat Toy",
      "quantity": 1,
      "unit_price": 12.50,
      "amount": 12.50
    }
  ],
  "created_at": "2025-10-16T20:30:00",
  "updated_at": "2025-10-16T20:35:00"
}
```

---

### 26. Crear Orden (Checkout)
**POST** `/sales/orders`

**Acceso:** 🔒 Usuario autenticado

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "user_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 3,
      "quantity": 1
    }
  ],
  "shipping_address": "Calle Principal #123, Colonia Centro"
}
```

**Campos Requeridos:**
- `user_id` (integer, min=1): ID del usuario
- `items` (array, min=1, max=50): Lista de productos
  - `product_id` (integer, min=1): ID del producto
  - `quantity` (integer, min=1, max=100): Cantidad

**Campos Opcionales:**
- `status` (string, default="pending"): Estado inicial de la orden
- `shipping_address` (string, min=5, max=500): Dirección de envío

**Nota:** Los productos no pueden duplicarse en una sola orden. El backend calcula automáticamente precios y totales.

**Response 201 Created:**
```json
{
  "message": "Order created successfully",
  "order": {
    "id": 1,
    "user_id": 1,
    "status": "pending",
    "total": 104.48,
    "shipping_address": "Calle Principal #123, Colonia Centro",
    "items": [
      {
        "id": 1,
        "product_id": 1,
        "product_name": "Premium Dog Food 15kg",
        "quantity": 2,
        "price": 45.99,
        "amount": 91.98
      },
      {
        "id": 2,
        "product_id": 3,
        "product_name": "Cat Litter 10kg",
        "quantity": 1,
        "price": 12.50,
        "amount": 12.50
      }
    ],
    "created_at": "2025-10-16T20:30:00"
  },
  "invoice": {
    "id": 1,
    "order_id": 1,
    "amount": 104.48,
    "status": "pending",
    "due_date": "2025-11-15T20:30:00"
  }
}
```

**Nota:** Al crear una orden, automáticamente se crea una factura asociada con vencimiento de 30 días.

---

### 27. Actualizar Orden
**PUT** `/sales/orders/{order_id}`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "status": "processing"
}
```

**Response 200 OK:**
```json
{
  "message": "Order updated successfully",
  "order": {
    "id": 1,
    "status": "processing",
    "updated_at": "2025-10-16T21:00:00"
  }
}
```

---

### 28. Actualizar Estado de Orden
**PATCH** `/sales/orders/{order_id}/status`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "status": "shipped"
}
```

**Estados válidos:**
- `pending` → `confirmed`
- `confirmed` → `processing`
- `processing` → `shipped`
- `shipped` → `delivered`
- Cualquier estado → `cancelled`

**Response 200 OK:**
```json
{
  "message": "Order status updated successfully",
  "order": {
    "id": 1,
    "status": "shipped",
    "updated_at": "2025-10-16T22:00:00"
  }
}
```

---

### 29. Cancelar Orden
**POST** `/sales/orders/{order_id}/cancel`

**Acceso:** 🔒 Usuario autenticado (solo su propia orden) o Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "message": "Order cancelled successfully",
  "order": {
    "id": 1,
    "status": "cancelled",
    "updated_at": "2025-10-16T22:00:00"
  }
}
```

---

### 30. Eliminar Orden
**DELETE** `/sales/orders/{order_id}`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "message": "Order deleted successfully"
}
```

---

## 💳 Facturas

### 31. Listar Facturas
**GET** `/sales/invoices`

**Acceso:** 🔒 Usuario autenticado

**Comportamiento basado en rol (REST standard):**
- **Usuario regular:** Ve solo sus propias facturas
- **Admin:** Ve todas las facturas del sistema

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters (opcionales):**
- `status` (string): "paid", "pending", "overdue", "refunded"

**Response 200 OK:**
```json
{
  "total_invoices": 3,
  "invoices": [
    {
      "id": 1,
      "order_id": 1,
      "user_id": 1,
      "amount": 104.48,
      "status": "paid",
      "created_at": "2025-10-16T20:30:00",
      "paid_at": "2025-10-16T20:35:00"
    }
  ]
}
```

---

### 32. Ver Detalle de Factura
**GET** `/sales/invoices/{invoice_id}`

**Acceso:** 🔒 Usuario autenticado (solo su propia factura) o Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "id": 1,
  "order_id": 1,
  "user_id": 1,
  "username": "johndoe",
  "amount": 104.48,
  "status": "paid",
  "order_details": {
    "id": 1,
    "items_count": 2,
    "total": 104.48
  },
  "created_at": "2025-10-16T20:30:00",
  "paid_at": "2025-10-16T20:35:00"
}
```

---

### 33. Crear Factura
**POST** `/sales/invoices`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "user_id": 1,
  "order_id": 1,
  "due_date": "2025-11-15T23:59:59",
  "status": "pending"
}
```

**Campos Requeridos:**
- `user_id` (integer, min=1): ID del usuario
- `order_id` (integer, min=1): ID de la orden asociada

**Campos Opcionales:**
- `due_date` (datetime): Fecha de vencimiento (default: +30 días desde creación)
- `status` (string, default="pending"): Estado inicial de la factura

**Nota:** El monto se calcula automáticamente desde la orden. El backend valida que el total de la factura coincida con el de la orden.

**Response 201 Created:**
```json
{
  "message": "Invoice created successfully",
  "invoice": {
    "id": 1,
    "order_id": 1,
    "user_id": 1,
    "amount": 104.48,
    "status": "pending",
    "due_date": "2025-11-15T23:59:59",
    "created_at": "2025-10-16T20:30:00"
  }
}
```

**Nota:** Normalmente las facturas se crean automáticamente al crear una orden.

---

### 34. Actualizar Factura
**PUT** `/sales/invoices/{invoice_id}`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "status": "paid",
  "amount": 104.48
}
```

**Response 200 OK:**
```json
{
  "message": "Invoice updated successfully",
  "invoice": {
    "id": 1,
    "status": "paid",
    "amount": 104.48
  }
}
```

---

### 35. Actualizar Estado de Factura
**PATCH** `/sales/invoices/{invoice_id}/status`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "status": "paid"
}
```

**Estados válidos:**
- `pending`
- `paid`
- `overdue`
- `refunded`

**Response 200 OK:**
```json
{
  "message": "Invoice status updated successfully",
  "invoice": {
    "id": 1,
    "status": "paid",
    "paid_at": "2025-10-16T20:35:00"
  }
}
```

---

### 36. Eliminar Factura
**DELETE** `/sales/invoices/{invoice_id}`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "message": "Invoice deleted successfully"
}
```

---

## 🔄 Devoluciones

### 37. Listar Devoluciones
**GET** `/sales/returns`

**Acceso:** 🔒 Usuario autenticado

**Comportamiento basado en rol (REST standard):**
- **Usuario regular:** Ve solo sus propias devoluciones
- **Admin:** Ve todas las devoluciones del sistema

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters (opcionales):**
- `status` (string): "requested", "approved", "rejected", "processed"

**Response 200 OK:**
```json
{
  "total_returns": 2,
  "returns": [
    {
      "id": 1,
      "order_id": 1,
      "user_id": 1,
      "reason": "Product arrived damaged",
      "status": "requested",
      "items": [
        {
          "product_id": 1,
          "product_name": "Premium Dog Food 15kg",
          "quantity": 1
        }
      ],
      "created_at": "2025-10-16T21:00:00"
    }
  ]
}
```

---

### 38. Ver Detalle de Devolución
**GET** `/sales/returns/{return_id}`

**Acceso:** 🔒 Usuario autenticado (solo su propia devolución) o Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "id": 1,
  "order_id": 1,
  "user_id": 1,
  "username": "johndoe",
  "reason": "Product arrived damaged",
  "status": "requested",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "Premium Dog Food 15kg",
      "quantity": 1,
      "unit_price": 45.99
    }
  ],
  "total_refund": 45.99,
  "created_at": "2025-10-16T21:00:00",
  "updated_at": "2025-10-16T21:00:00"
}
```

---

### 39. Crear Solicitud de Devolución
**POST** `/sales/returns`

**Acceso:** 🔒 Usuario autenticado

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "order_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 1,
      "reason": "Producto llegó dañado",
      "refund_amount": 45.99
    },
    {
      "product_id": 3,
      "quantity": 1,
      "reason": "Producto equivocado"
    }
  ],
  "status": "requested"
}
```

**Campos Requeridos:**
- `order_id` (integer, min=1): ID de la orden a devolver
- `items` (array, min=1, max=50): Lista de productos a devolver
  - `product_id` (integer, min=1): ID del producto
  - `quantity` (integer, min=1, max=100): Cantidad a devolver
  - `reason` (string, min=1, max=500): Razón de la devolución

**Campos Opcionales (por item):**
- `refund_amount` (float, min=0.01): Monto a reembolsar (default: precio × cantidad)

**Campos Opcionales (generales):**
- `status` (string, default="requested"): Estado inicial de la devolución

**Nota:** El backend valida que los productos pertenezcan a la orden y calcula automáticamente el total del reembolso.

**Response 201 Created:**
```json
{
  "message": "Return request created successfully",
  "return": {
    "id": 1,
    "order_id": 1,
    "user_id": 1,
    "status": "requested",
    "items": [
      {
        "id": 1,
        "product_id": 1,
        "product_name": "Premium Dog Food 15kg",
        "quantity": 1,
        "reason": "Producto llegó dañado",
        "refund_amount": 45.99
      },
      {
        "id": 2,
        "product_id": 3,
        "product_name": "Cat Litter 10kg",
        "quantity": 1,
        "reason": "Producto equivocado",
        "refund_amount": 12.50
      }
    ],
    "total": 58.49,
    "created_at": "2025-10-16T21:00:00"
  }
}
```

---

### 40. Actualizar Devolución
**PUT** `/sales/returns/{return_id}`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "status": "approved",
  "admin_notes": "Refund approved, product will be restocked"
}
```

**Response 200 OK:**
```json
{
  "message": "Return updated successfully",
  "return": {
    "id": 1,
    "status": "approved",
    "admin_notes": "Refund approved, product will be restocked"
  }
}
```

---

### 41. Actualizar Estado de Devolución
**PATCH** `/sales/returns/{return_id}/status`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "status": "approved"
}
```

**Estados válidos:**
- `requested` → `approved` o `rejected`
- `approved` → `processed`

**Response 200 OK:**
```json
{
  "message": "Return status updated successfully",
  "return": {
    "id": 1,
    "status": "approved",
    "updated_at": "2025-10-16T21:30:00"
  }
}
```

---

### 42. Eliminar Devolución
**DELETE** `/sales/returns/{return_id}`

**Acceso:** 🔒 Admin

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200 OK:**
```json
{
  "message": "Return deleted successfully"
}
```

---

## 📝 Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Datos de entrada inválidos |
| 401 | Unauthorized - No autenticado o token inválido |
| 403 | Forbidden - No tienes permisos para esta acción |
| 404 | Not Found - Recurso no encontrado |
| 409 | Conflict - Conflicto (ej: username ya existe) |
| 500 | Internal Server Error - Error del servidor |

---

## 🔑 Autenticación con JWT

### Cómo usar el token:

1. **Hacer login** para obtener el token:
```bash
POST /auth/login
{
  "username": "johndoe",
  "password": "securepass123"
}
```

2. **Guardar el token** de la respuesta:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

3. **Incluir el token en las solicitudes** protegidas:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Ejemplo con cURL:
```bash
curl -X GET http://localhost:8000/auth/users \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Ejemplo con JavaScript (fetch):
```javascript
const token = localStorage.getItem('token');

fetch('http://localhost:8000/auth/users', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## 🎯 Ejemplos de Flujos Completos

### Flujo 1: Registro y Compra

```bash
# 1. Registrarse
POST /auth/register
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123"
}

# 2. Hacer login
POST /auth/login
{
  "username": "newuser",
  "password": "password123"
}
# Guardar el token de la respuesta

# 3. Ver productos
GET /products?category=food&pet_type=dog

# 4. Crear carrito
POST /sales/carts
{
  "user_id": 1
}

# 5. Agregar productos al carrito
POST /sales/carts/1/items/1
{
  "quantity": 2
}

# 6. Ver carrito
GET /sales/carts/1

# 7. Crear orden (checkout)
POST /sales/orders
{
  "cart_id": 1,
  "user_id": 1
}

# 8. Ver mis órdenes
GET /sales/orders

# 9. Ver factura
GET /sales/invoices
```

---

### Flujo 2: Admin - Gestión de Productos

```bash
# 1. Login como admin
POST /auth/login
{
  "username": "admin",
  "password": "adminpass123"
}

# 2. Ver todos los productos
GET /products

# 3. Crear nuevo producto
POST /products
{
  "sku": "NEW01",
  "description": "New Premium Product",
  "category": "toys",
  "pet_type": "dog",
  "stock_quantity": 100,
  "price": 25.99,
  "cost": 15.00
}

# 4. Actualizar producto
PUT /products/3
{
  "price": 29.99,
  "stock_quantity": 150
}

# 5. Ver todas las órdenes
GET /sales/orders

# 6. Actualizar estado de orden
PATCH /sales/orders/1/status
{
  "status": "shipped"
}
```

---

## 💡 Consejos y Buenas Prácticas

1. **Siempre incluye el token** en requests protegidos
2. **Valida los datos** antes de enviarlos
3. **Maneja los errores** apropiadamente en tu aplicación
4. **Renueva el token** cuando expire (24 horas por defecto)
5. **No expongas el token** en URLs o logs públicos
6. **Usa HTTPS** en producción para mayor seguridad

---

## 🚨 Errores Comunes

### Error 401 - Unauthorized
```json
{
  "error": "Authorization header missing"
}
```
**Solución:** Incluye el header `Authorization: Bearer {token}`

---

### Error 403 - Forbidden
```json
{
  "error": "Admin access required"
}
```
**Solución:** Necesitas permisos de administrador para esta acción

---

### Error 409 - Conflict
```json
{
  "error": "Username already exists"
}
```
**Solución:** El username o email ya está registrado

---

### Error 404 - Not Found
```json
{
  "error": "Resource not found"
}
```
**Solución:** El ID proporcionado no existe en la base de datos

---

**Última actualización:** Octubre 18, 2025  
**Versión de API:** 1.1  
**Autor:** Pet E-commerce Team

---

## 📢 Cambios Importantes (v1.1 - Octubre 18, 2025)

### 🔄 Rutas de Carritos Actualizadas (REST Compliant)

Las rutas de carritos han sido refactorizadas para seguir estándares REST:

| Ruta Antigua (v1.0) | Ruta Nueva (v1.1) | Método |
|---------------------|-------------------|--------|
| `GET /sales/admin/carts` | `GET /sales/carts` (con token admin) | GET |
| `POST /sales/cart` | `POST /sales/carts` | POST |
| `GET /sales/cart/{id}` | `GET /sales/carts/{id}` | GET |
| `PUT /sales/cart/{id}` | `PUT /sales/carts/{id}` | PUT |
| `DELETE /sales/cart/{id}` | `DELETE /sales/carts/{id}` | DELETE |
| `POST /sales/cart/{id}/items/{pid}` | `POST /sales/carts/{id}/items/{pid}` | POST |
| `PUT /sales/cart/{id}/items/{pid}` | `PUT /sales/carts/{id}/items/{pid}` | PUT |
| `DELETE /sales/cart/{id}/items/{pid}` | `DELETE /sales/carts/{id}/items/{pid}` | DELETE |

**Cambios clave:**
- ✅ Rutas pluralizadas: `/cart` → `/carts`
- ✅ Eliminada ruta `/admin/carts` - usar `GET /carts` con token de admin
- ✅ Comportamiento basado en rol automático
- ✅ Consistencia con otras rutas REST (orders, invoices, returns)

### 🎯 Comportamiento Basado en Rol

Todos los endpoints de listado ahora filtran automáticamente según el rol del usuario:

- **`GET /sales/carts`**: Admin ve todos, usuario ve solo el suyo
- **`GET /sales/orders`**: Admin ve todas, usuario ve solo las suyas
- **`GET /sales/invoices`**: Admin ve todas, usuario ve solo las suyas
- **`GET /sales/returns`**: Admin ve todas, usuario ve solo las suyas

### 📝 Métodos HTTP Actualizados

- **Status updates**: Cambiado de `PUT` a `PATCH` para mayor precisión semántica
  - `PATCH /sales/orders/{id}/status`
  - `PATCH /sales/invoices/{id}/status`
  - `PATCH /sales/returns/{id}/status`

### ⚠️ Migración desde v1.0

Si estás usando la API v1.0, actualiza tus llamadas:

```javascript
// ❌ v1.0 (deprecated)
GET /sales/admin/carts
GET /sales/cart/123

// ✅ v1.1 (current)
GET /sales/carts  // Usa mismo token de admin
GET /sales/carts/123
```

---






