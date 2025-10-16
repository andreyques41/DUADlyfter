# Pet E-commerce API - Quick Reference

## � About This API

A comprehensive REST API for a pet products e-commerce platform built with Flask. This API provides complete functionality for browsing products, managing shopping carts, processing orders, handling payments, and managing returns.

**What This API Does**:
- 🛍️ **Product Catalog**: Browse pet products with advanced filtering (category, pet type, price, stock)
- 👤 **User Management**: Secure registration, login, and profile management with JWT authentication
- 🛒 **Shopping Cart**: Add/remove items, update quantities, and manage cart contents
- 📦 **Order Processing**: Create orders, track status, and cancel when needed
- 💳 **Billing**: Invoice generation and payment tracking
- 🔄 **Returns**: Handle return requests with approval workflows and refunds
- 🔒 **Admin Controls**: Full administrative access for managing products, orders, and users

**Technology Stack**:
- Flask REST API with SQLAlchemy ORM
- PostgreSQL database
- JWT authentication with database role verification
- Marshmallow schema validation
- Role-based access control (Admin/Customer)

**API Characteristics**:
- 42 total endpoints across 6 resource categories
- RESTful design with standard HTTP methods
- JSON request/response format
- Comprehensive error handling with detailed messages
- Real-time role verification from database (not just JWT payload)

---

## �🚦 How to Run the App Locally

1. **Open a terminal in the project root folder**  
   (where `run.py` and `.venv` are located).

2. **Activate the virtual environment:**

   On Windows:

   ```sh
   .\.venv\Scripts\activate
   ```

   On macOS/Linux:

   ```sh
   source .venv/bin/activate
   ```

3. **Install dependencies (if not already installed):**

   ```sh
   pip install -r config/requirements.txt
   ```

4. **Run the Flask app:**

   ```sh
   python run.py
   ```

5. **Access the API:**  
   Open your browser or Postman and go to:  
   [http://localhost:8000](http://localhost:8000)

---

## 🔐 Access Levels

The API uses JWT-based authentication with role-based access control. User roles are verified in real-time from the database (not just from the JWT token), ensuring that role changes take effect immediately.

**Access Levels:**
- **🌐 PUBLIC**: No authentication required - Anyone can access
- **👤 USER**: JWT token required - Users can access only their own data
- **👥 USER/ADMIN**: JWT token required - Users access own data, admins access any data
- **🔒 ADMIN**: JWT token + admin role required - Admin-only operations

**Authentication Header Format:**
```
Authorization: Bearer <your_jwt_token>
```

**How It Works:**
1. Register or login to receive a JWT token
2. Include the token in the `Authorization` header for protected endpoints
3. The API verifies the token and checks your role in the database
4. Access is granted or denied based on your current role (even if the JWT says otherwise)

**Security Features:**
- Tokens expire after 24 hours (configurable)
- Roles are verified from database on every request
- Password hashing with bcrypt (12 rounds)
- Role changes take effect immediately without token refresh

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
  "password": "pass1234",
  "first_name": "Jane",
  "last_name": "Doe",
  "user": "admin/user"
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
  "first_name": "Updated Name",
  "email": "new@example.com"
}
```

**Change Password**

```bash
PUT /auth/users/1
Authorization: Bearer <token>
{
  "current_password": "password123",
  "new_password": "new_password1234",
  "confirm_password": "new_password1234"
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
  "name": "Dog Toys",
  "price": 29.99,
  "category": "toys",
  "pet_type": "dog",
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
POST /sales/cart
Authorization: Bearer <token>
{
  "user_id": 1,
  "items": [
    {
      "product_id": 5,
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
      "quantity": 2
    }
  ]
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
  "order_id": 101,
  "amount": 31.98,
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
  "due_date": "2025-09-20"
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
  "order_id": 101,
  "bill_id": 201,
  "items": [
    {
      "product_id": 5,
      "quantity": 1,
      "reason": "Damaged item received"
    }
  ]
}
```

> **Note**: `user_id` is automatically derived from the authenticated user context. `product_name` and `refund_amount` are automatically populated from the product database. If `refund_amount` is not provided, it defaults to `product.price × quantity`.

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
  "items": [
    {
      "product_id": 5,
      "quantity": 1,
      "reason": "Updated reason - partial refund approved",
      "refund_amount": 12.99
    }
  ]
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

`requested` → `approved`/`rejected` → `processed`

---

## 🔄 E-commerce Flow

### Typical Customer Journey

1. **Browse Products** → `GET /products` (Public - no auth needed)
   - Filter by category, pet type, price range
   - Check product availability and details

2. **Create Account** → `POST /auth/register`
   - Provide username, email, password, and user details
   - Automatically assigned 'customer' role

3. **Login** → `POST /auth/login`
   - Receive JWT token valid for 24 hours
   - Use token for all subsequent authenticated requests

4. **Build Cart** → `POST /sales/cart`
   - Add products with quantities
   - Update cart as needed with `PUT /sales/cart/{user_id}`

5. **Place Order** → `POST /sales/orders`
   - Order created from cart items
   - Inventory automatically decremented
   - Initial status: 'pending'

6. **Track Order** → `GET /sales/orders/{id}` or `GET /sales/orders/user/{user_id}`
   - Monitor order status progression
   - Check shipping and delivery updates

7. **Receive Invoice** (Admin creates) → Admin: `POST /sales/bills`
   - Invoice linked to order
   - Payment tracking

8. **Request Return** (if needed) → `POST /sales/returns`
   - Submit return request with reason
   - Wait for admin approval
   - Track refund status

### Admin Workflow

1. **Login as Admin** → `POST /auth/login` (with admin credentials)

2. **Manage Products** → 
   - Create: `POST /products`
   - Update: `PUT /products/{id}`
   - Delete: `DELETE /products/{id}`

3. **Process Orders** → 
   - View all: `GET /sales/admin/orders`
   - Update status: `PATCH /sales/orders/{id}/status`
   - Manage inventory and shipping

4. **Handle Billing** → 
   - Create invoices: `POST /sales/bills`
   - Update payment status: `PATCH /sales/bills/{id}/status`
   - Track payments: `GET /sales/admin/bills`

5. **Process Returns** → 
   - Review requests: `GET /sales/admin/returns`
   - Approve/reject: `PATCH /sales/returns/{id}/status`
   - Issue refunds: `PUT /sales/returns/{id}`

---

## 📈 Statistics & Capabilities

### API Overview
- **Total Endpoints**: 42
- **Access Distribution**: 
  - Public: 4 endpoints (product browsing)
  - User: 2 endpoints (own data only)
  - User/Admin: 20 endpoints (conditional access)
  - Admin: 16 endpoints (admin-only)
- **HTTP Methods**: 
  - GET: 16 (retrieve data)
  - POST: 10 (create resources)
  - PUT: 8 (full updates)
  - PATCH: 4 (partial updates)
  - DELETE: 6 (remove resources)

### Performance & Scalability
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with 24-hour expiration
- **Validation**: Marshmallow schemas for all inputs
- **Logging**: Centralized logging with configurable levels
- **Error Handling**: Comprehensive error responses with details

### Supported Operations
- ✅ User registration and authentication
- ✅ Role-based access control with database verification
- ✅ Product catalog with advanced filtering
- ✅ Shopping cart management
- ✅ Order creation and tracking
- ✅ Invoice generation and payment tracking
- ✅ Return request processing
- ✅ Admin dashboard capabilities
- ✅ Real-time inventory updates
- ✅ Status workflow management (orders, invoices, returns)

---

## 🎓 Additional Resources

### Documentation
- **README.md**: Complete project overview, architecture, and setup instructions
- **DECORATOR_OPTIMIZATION.md**: Details on authentication decorator improvements
- **Database Schema**: See `docs/postgres_sql_queries/` for table definitions and sample data

### Development
- **Clean Architecture**: Routes → Services → Repositories → Models
- **Modular Design**: Separate modules for auth, products, and sales
- **Code Standards**: PEP 8 compliant with comprehensive docstrings
- **Testing**: Pytest-ready structure (tests/ directory)

### Support
For questions, issues, or contributions, please refer to the project repository.
