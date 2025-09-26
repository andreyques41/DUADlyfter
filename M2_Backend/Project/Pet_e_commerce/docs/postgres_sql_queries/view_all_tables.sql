-- =================================================
-- VIEW ALL TABLES DATA - PET E-COMMERCE DATABASE
-- Schema: lyfter_backend_project
-- =================================================

-- Set schema for all operations
SET search_path TO lyfter_backend_project;

-- =================================================
-- 1. CORE REFERENCE TABLES
-- =================================================

-- View all roles
SELECT * FROM roles;

-- View all product categories
SELECT * FROM product_categories;

-- View all pet types
SELECT * FROM pet_types;

-- View all order statuses
SELECT * FROM order_status;

-- View all return statuses
SELECT * FROM return_status;

-- View all invoice statuses
SELECT * FROM invoice_status;

-- =================================================
-- 2. USERS AND AUTHENTICATION
-- =================================================

-- View all users
SELECT * FROM users;

-- View all role-user relationships
SELECT * FROM role_user;

-- =================================================
-- 3. PRODUCTS
-- =================================================

-- View all products
SELECT * FROM products;

-- =================================================
-- 4. SHOPPING CARTS
-- =================================================

-- View all carts
SELECT * FROM carts;

-- View all cart items
SELECT * FROM cart_item;

-- =================================================
-- 5. ORDERS
-- =================================================

-- View all orders
SELECT * FROM orders;

-- View all order items
SELECT * FROM order_item;

-- =================================================
-- 6. RETURNS
-- =================================================

-- View all returns
SELECT * FROM returns;

-- View all return items
SELECT * FROM return_item;

-- =================================================
-- 7. INVOICES
-- =================================================

-- View all invoices
SELECT * FROM invoices;