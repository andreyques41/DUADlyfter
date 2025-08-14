# Pet E-commerce API - Quick Reference

## 🔐 Access Levels

- **🌐 PUBLIC**: No auth required
- **👤 USER**: JWT token, own data only
- **👥 USER/ADMIN**: JWT token, own data or admin access
- **🔒 ADMIN**: JWT token + admin role

**Auth Header**: `Authorization: Bearer <jwt_token>`

---

## 📋 All Endpoints (42 total)

### 🔐 Authentication (`/auth`) - 6 endpoints

| Method | Endpoint           | Access | Purpose                 |
| ------ | ------------------ | ------ | ----------------------- |
| POST   | `/auth/login`      | 🌐     | User login              |
| POST   | `/auth/register`   | 🌐     | User registration       |
| GET    | `/auth/users`      | 🔒     | List all users          |
| GET    | `/auth/users/{id}` | 👥     | Get user profile        |
| PUT    | `/auth/users/{id}` | 👥     | Update profile/password |
| DELETE | `/auth/users/{id}` | 👥     | Delete user             |

### 🛍️ Products (`/products`) - 5 endpoints

| Method | Endpoint         | Access | Purpose                        |
| ------ | ---------------- | ------ | ------------------------------ |
| GET    | `/products`      | 🌐     | Browse products (with filters) |
| GET    | `/products/{id}` | 🌐     | Get product details            |
| POST   | `/products`      | 🔒     | Create product                 |
| PUT    | `/products/{id}` | 🔒     | Update product                 |
| DELETE | `/products/{id}` | 🔒     | Delete product                 |

### 🛒 Cart (`/sales/cart`) - 6 endpoints

| Method | Endpoint                                   | Access | Purpose         |
| ------ | ------------------------------------------ | ------ | --------------- |
| GET    | `/sales/cart/{user_id}`                    | 👥     | Get user's cart |
| POST   | `/sales/cart/{user_id}`                    | 👥     | Create cart     |
| PUT    | `/sales/cart/{user_id}`                    | 👥     | Update cart     |
| DELETE | `/sales/cart/{user_id}`                    | 👥     | Clear cart      |
| DELETE | `/sales/cart/{user_id}/items/{product_id}` | 👥     | Remove item     |
| GET    | `/sales/admin/carts`                       | 🔒     | View all carts  |

### 📦 Orders (`/sales/orders`) - 8 endpoints

| Method | Endpoint                       | Access | Purpose           |
| ------ | ------------------------------ | ------ | ----------------- |
| POST   | `/sales/orders`                | 👥     | Create order      |
| GET    | `/sales/orders/{id}`           | 👥     | Get order details |
| GET    | `/sales/orders/user/{user_id}` | 👥     | Get user's orders |
| PUT    | `/sales/orders/{id}`           | 🔒     | Update order      |
| PATCH  | `/sales/orders/{id}/status`    | 🔒     | Update status     |
| POST   | `/sales/orders/{id}/cancel`    | 👥     | Cancel order      |
| DELETE | `/sales/orders/{id}`           | 🔒     | Delete order      |
| GET    | `/sales/admin/orders`          | 🔒     | View all orders   |

### 💳 Bills (`/sales/bills`) - 7 endpoints

| Method | Endpoint                      | Access | Purpose          |
| ------ | ----------------------------- | ------ | ---------------- |
| POST   | `/sales/bills`                | 🔒     | Create bill      |
| GET    | `/sales/bills/{id}`           | 👥     | Get bill details |
| GET    | `/sales/bills/user/{user_id}` | 👥     | Get user's bills |
| PUT    | `/sales/bills/{id}`           | 🔒     | Update bill      |
| PATCH  | `/sales/bills/{id}/status`    | 🔒     | Update status    |
| DELETE | `/sales/bills/{id}`           | 🔒     | Delete bill      |
| GET    | `/sales/admin/bills`          | 🔒     | View all bills   |

### 🔄 Returns (`/sales/returns`) - 7 endpoints

| Method | Endpoint                        | Access | Purpose               |
| ------ | ------------------------------- | ------ | --------------------- |
| POST   | `/sales/returns`                | 👤     | Create return request |
| GET    | `/sales/returns/{id}`           | 👥     | Get return details    |
| GET    | `/sales/returns/user/{user_id}` | 👥     | Get user's returns    |
| PUT    | `/sales/returns/{id}`           | 🔒     | Update return         |
| PATCH  | `/sales/returns/{id}/status`    | 🔒     | Update status         |
| DELETE | `/sales/returns/{id}`           | 🔒     | Delete return         |
| GET    | `/sales/admin/returns`          | 🔒     | View all returns      |

---

## 🚀 API Examples

### 🔐 Authentication

**Login**

```bash
POST /auth/login
{
  "username": "john_doe",
  "password": "password123"
}
```

**Register**

```bash
POST /auth/register
{
  "username": "jane",
  "email": "jane@example.com",
  "password": "pass123",
  "full_name": "Jane Doe"
}
```

**Get All Users (Admin)**

```bash
GET /auth/users
Authorization: Bearer <admin_token>
```

**Get User Profile**

```bash
GET /auth/users/1
Authorization: Bearer <token>
```

**Update Profile**

```bash
PUT /auth/users/1
Authorization: Bearer <token>
{
  "full_name": "Updated Name",
  "email": "new@example.com"
}
```

**Change Password**

```bash
PUT /auth/users/1
Authorization: Bearer <token>
{
  "current_password": "old123",
  "new_password": "new456"
}
```

**Delete User**

```bash
DELETE /auth/users/1
Authorization: Bearer <token>
```

### 🛍️ Products

**Browse Products**

```bash
GET /products?category=dog&min_price=10&max_price=50&in_stock=true
```

**Get Product Details**

```bash
GET /products/5
```

**Create Product (Admin)**

```bash
POST /products
Authorization: Bearer <admin_token>
{
  "name": "Dog Food",
  "price": 29.99,
  "category": "dog",
  "stock_quantity": 50,
  "description": "Premium dog food for all breeds"
}
```

**Update Product (Admin)**

```bash
PUT /products/5
Authorization: Bearer <admin_token>
{
  "price": 27.99,
  "stock_quantity": 45
}
```

**Delete Product (Admin)**

```bash
DELETE /products/5
Authorization: Bearer <admin_token>
```

### 🛒 Cart

**Get User's Cart**

```bash
GET /sales/cart/1
Authorization: Bearer <token>
```

**Create Cart**

```bash
POST /sales/cart/1
Authorization: Bearer <token>
{
  "user_id": 1,
  "items": [
    {
      "product_id": 5,
      "product_name": "Dog Leash",
      "price": 15.99,
      "quantity": 2
    }
  ]
}
```

**Update Cart**

```bash
PUT /sales/cart/1
Authorization: Bearer <token>
{
  "items": [
    {
      "product_id": 5,
      "product_name": "Dog Leash",
      "price": 15.99,
      "quantity": 3
    }
  ]
}
```

**Clear Cart**

```bash
DELETE /sales/cart/1
Authorization: Bearer <token>
```

**Remove Item from Cart**

```bash
DELETE /sales/cart/1/items/5
Authorization: Bearer <token>
```

**View All Carts (Admin)**

```bash
GET /sales/admin/carts
Authorization: Bearer <admin_token>
```

### 📦 Orders

**Create Order**

```bash
POST /sales/orders
Authorization: Bearer <token>
{
  "user_id": 1,
  "items": [
    {
      "product_id": 5,
      "product_name": "Dog Leash",
      "price": 15.99,
      "quantity": 2
    }
  ],
  "shipping_address": "123 Main St, City, State 12345",
  "payment_method": "credit_card"
}
```

**Get Order Details**

```bash
GET /sales/orders/101
Authorization: Bearer <token>
```

**Get User's Orders**

```bash
GET /sales/orders/user/1
Authorization: Bearer <token>
```

**Update Order (Admin)**

```bash
PUT /sales/orders/101
Authorization: Bearer <admin_token>
{
  "shipping_address": "456 New St, City, State 67890",
  "items": [
    {
      "product_id": 5,
      "product_name": "Dog Leash",
      "price": 15.99,
      "quantity": 1
    }
  ]
}
```

**Update Order Status (Admin)**

```bash
PATCH /sales/orders/101/status
Authorization: Bearer <admin_token>
{
  "status": "shipped"
}
```

**Cancel Order**

```bash
POST /sales/orders/101/cancel
Authorization: Bearer <token>
{
  "reason": "Changed mind"
}
```

**Delete Order (Admin)**

```bash
DELETE /sales/orders/101
Authorization: Bearer <admin_token>
```

**View All Orders (Admin)**

```bash
GET /sales/admin/orders
Authorization: Bearer <admin_token>
```

### 💳 Bills

**Create Bill (Admin)**

```bash
POST /sales/bills
Authorization: Bearer <admin_token>
{
  "user_id": 1,
  "amount": 31.98,
  "description": "Order #101",
  "due_date": "2025-09-13"
}
```

**Get Bill Details**

```bash
GET /sales/bills/201
Authorization: Bearer <token>
```

**Get User's Bills**

```bash
GET /sales/bills/user/1
Authorization: Bearer <token>
```

**Update Bill (Admin)**

```bash
PUT /sales/bills/201
Authorization: Bearer <admin_token>
{
  "amount": 29.99,
  "description": "Updated bill description"
}
```

**Update Bill Status (Admin)**

```bash
PATCH /sales/bills/201/status
Authorization: Bearer <admin_token>
{
  "status": "paid"
}
```

**Delete Bill (Admin)**

```bash
DELETE /sales/bills/201
Authorization: Bearer <admin_token>
```

**View All Bills (Admin)**

```bash
GET /sales/admin/bills
Authorization: Bearer <admin_token>
```

### 🔄 Returns

**Create Return Request**

```bash
POST /sales/returns
Authorization: Bearer <token>
{
  "user_id": 1,
  "order_id": 101,
  "product_id": 5,
  "quantity": 1,
  "reason": "Damaged item received",
  "refund_amount": 15.99
}
```

**Get Return Details**

```bash
GET /sales/returns/301
Authorization: Bearer <token>
```

**Get User's Returns**

```bash
GET /sales/returns/user/1
Authorization: Bearer <token>
```

**Update Return (Admin)**

```bash
PUT /sales/returns/301
Authorization: Bearer <admin_token>
{
  "refund_amount": 12.99,
  "reason": "Updated reason - partial refund approved"
}
```

**Update Return Status (Admin)**

```bash
PATCH /sales/returns/301/status
Authorization: Bearer <admin_token>
{
  "status": "approved"
}
```

**Delete Return (Admin)**

```bash
DELETE /sales/returns/301
Authorization: Bearer <admin_token>
```

**View All Returns (Admin)**

```bash
GET /sales/admin/returns
Authorization: Bearer <admin_token>
```

---

## 📊 Status Workflows

### Order Statuses

`pending` → `confirmed` → `processing` → `shipped` → `delivered`

- Can be `cancelled` at any stage before `delivered`

### Bill Statuses

`pending` → `paid` / `overdue` → `refunded`

### Return Statuses

`pending` → `approved`/`rejected` → `processed` → `refunded`

---

## 🔄 E-commerce Flow

1. **Browse** → `GET /products`
2. **Register** → `POST /auth/register`
3. **Login** → `POST /auth/login`
4. **Add to Cart** → `POST /sales/cart/{user_id}`
5. **Create Order** → `POST /sales/orders`
6. **Admin: Create Bill** → `POST /sales/bills`
7. **Admin: Ship Order** → `PATCH /sales/orders/{id}/status`
8. **Request Return** → `POST /sales/returns` (if needed)

---

## 📈 Statistics

- **Total Endpoints**: 42
- **Public**: 4 | **User**: 2 | **User/Admin**: 20 | **Admin**: 16
- **GET**: 16 | **POST**: 10 | **PUT**: 8 | **PATCH**: 4 | **DELETE**: 6

For detailed examples and request/response formats, see `API_ENDPOINTS_SUMMARY.md`
