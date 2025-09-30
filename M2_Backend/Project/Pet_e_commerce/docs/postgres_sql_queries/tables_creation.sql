-- =================================================
-- PET E-COMMERCE DATABASE SCHEMA
-- Schema: lyfter_backend_project
-- =================================================

-- Set schema for all operations
SET search_path TO lyfter_backend_project;

-- =================================================
-- 1. CORE REFERENCE TABLES (No dependencies)
-- =================================================

-- Roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255) NOT NULL
);

-- Product Categories
CREATE TABLE product_categories (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL UNIQUE
);

-- Pet Types
CREATE TABLE pet_types (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100) NOT NULL UNIQUE
);

-- Order Status
CREATE TABLE order_status (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) NOT NULL UNIQUE
);

-- Return Status
CREATE TABLE return_status (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) NOT NULL UNIQUE
);

-- Invoice Status
CREATE TABLE invoice_status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- =================================================
-- 2. USERS AND AUTHENTICATION
-- =================================================

-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100), -- optional
    last_name VARCHAR(100), -- optional
    phone VARCHAR(20) -- optional
);

-- Role_User (relation between users and roles)
CREATE TABLE role_user (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT
);

-- =================================================
-- 3. PRODUCTS
-- =================================================

-- Products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku CHAR(5) UNIQUE NOT NULL,
    description VARCHAR(255) NOT NULL,
    product_category_id INTEGER NOT NULL REFERENCES product_categories(id) ON DELETE RESTRICT,
    pet_type_id INTEGER NOT NULL REFERENCES pet_types(id) ON DELETE RESTRICT,
    stock_quantity INTEGER NOT NULL,
    brand VARCHAR(100), -- optional
    weight REAL, -- optional
    is_active BOOLEAN, -- optional
    internal_cost REAL, -- optional
    supplier_info VARCHAR(255), -- optional
    created_by VARCHAR(100), -- optional
    last_updated TIMESTAMP -- optional
);

-- =================================================
-- 4. SHOPPING CARTS
-- =================================================

-- Carts
CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP, -- optional
    finalized BOOLEAN NOT NULL
);

-- Cart Items (relation between carts and products)
CREATE TABLE cart_item (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE RESTRICT,
    amount REAL NOT NULL,
    quantity INTEGER NOT NULL,
    UNIQUE(product_id, cart_id)
);

-- =================================================
-- 5. ORDERS
-- =================================================

-- Orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER UNIQUE NOT NULL REFERENCES carts(id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    order_status_id INTEGER NOT NULL REFERENCES order_status(id) ON DELETE RESTRICT,
    total_amount REAL NOT NULL,
    created_at TIMESTAMP, -- optional
    shipping_address VARCHAR(255) -- optional
);

-- Order Items (relation between orders and products)
CREATE TABLE order_item (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE RESTRICT,
    amount REAL NOT NULL,
    quantity INTEGER NOT NULL,
    UNIQUE(product_id, order_id)
);

-- =================================================
-- 6. RETURNS
-- =================================================

-- Returns
CREATE TABLE returns (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    return_status_id INTEGER NOT NULL REFERENCES return_status(id) ON DELETE RESTRICT,
    total_amount REAL NOT NULL,
    created_at TIMESTAMP -- optional
);

-- Return Items (relation between returns and products)
CREATE TABLE return_item (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    return_id INTEGER NOT NULL REFERENCES returns(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL,
    reason VARCHAR(255) NOT NULL,
    amount REAL NOT NULL
);

-- =================================================
-- 7. INVOICES
-- =================================================

-- Invoices
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE NOT NULL REFERENCES orders(id) ON DELETE RESTRICT,
    total_amount REAL NOT NULL,
    invoice_status_id INTEGER NOT NULL REFERENCES invoice_status(id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP, -- optional
    due_date TIMESTAMP -- optional
);





