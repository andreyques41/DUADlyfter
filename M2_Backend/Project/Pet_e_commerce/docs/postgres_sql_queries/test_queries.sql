-- =================================================
-- ESSENTIAL PET E-COMMERCE QUERIES FOR POSTGRESQL
-- Schema: lyfter_backend_project
-- =================================================

-- Set schema for all operations
SET search_path TO lyfter_backend_project;

-- =================================================
-- 1. USER AUTHENTICATION & PROFILE
-- =================================================

-- Login - Get user by email/username 
SELECT id, username, email, password_hash, first_name, last_name
FROM users 
WHERE email = 'john.doe@email.com' OR username = 'john_doe';

-- Get user profile (user_id = 1)
SELECT id, username, email, first_name, last_name, phone
FROM users 
WHERE id = 1;

-- =================================================
-- 2. PRODUCT CATALOG (Customer View)
-- =================================================

-- Get all active products
SELECT 
    p.id, p.sku, p.description, p.brand, p.stock_quantity,
    pc.category, pt.type as pet_type
FROM products p
INNER JOIN product_categories pc ON p.product_category_id = pc.id
INNER JOIN pet_types pt ON p.pet_type_id = pt.id
WHERE p.is_active = true;

-- Get single product details (product_id = 1)
SELECT 
    p.id, p.sku, p.description, p.brand, p.stock_quantity, p.weight,
    pc.category, pt.type as pet_type
FROM products p
INNER JOIN product_categories pc ON p.product_category_id = pc.id
INNER JOIN pet_types pt ON p.pet_type_id = pt.id
WHERE p.id = 1 AND p.is_active = true;

-- Search products (search for 'Dog' in the product description)
SELECT 
    p.id, p.sku, p.description, p.brand, p.stock_quantity,
    pc.category, pt.type as pet_type
FROM products p
INNER JOIN product_categories pc ON p.product_category_id = pc.id
INNER JOIN pet_types pt ON p.pet_type_id = pt.id
WHERE p.description LIKE '%Dog%' AND p.is_active = true;

-- =================================================
-- 3. SHOPPING CART
-- =================================================

-- Get user's active cart (user_id = 1)
SELECT 
    c.id as cart_id,
    ci.id as item_id, ci.quantity, ci.amount,
    p.id as product_id, p.sku, p.description, p.brand
FROM carts c
LEFT JOIN cart_item ci ON c.id = ci.cart_id
LEFT JOIN products p ON ci.product_id = p.id
WHERE c.user_id = 1 AND c.finalized = false;

-- Check if user has active cart (user_id = 1)
SELECT id FROM carts WHERE user_id = 1 AND finalized = false;

-- Add item to cart (product_id=1, cart_id=1, amount=15.50, quantity=2)
INSERT INTO cart_item (product_id, cart_id, amount, quantity) 
VALUES (1, 1, 15.50, 2);

-- Remove item from cart (item_id = 1)
DELETE FROM cart_item WHERE id = 1;

-- Get cart total (user_id = 1)
SELECT SUM(quantity * amount) as total
FROM cart_item ci
INNER JOIN carts c ON ci.cart_id = c.id
WHERE c.user_id = 1 AND c.finalized = false;

-- =================================================
-- 4. ORDERS (Basic)
-- =================================================

-- Create order (finalize cart_id = 1)
UPDATE carts SET finalized = true WHERE id = 1;

-- Get user's orders (user_id = 1)
SELECT 
    o.id, o.created_at, o.total_amount,
    os.status
FROM orders o
INNER JOIN order_status os ON o.order_status_id = os.id
WHERE o.user_id = 2
ORDER BY o.created_at DESC;

-- Get order details (order_id = 1)
SELECT 
    o.id as order_id, o.created_at, o.total_amount, o.shipping_address,
    os.status,
    oi.quantity, oi.amount,
    p.sku, p.description, p.brand
FROM orders o
INNER JOIN order_status os ON o.order_status_id = os.id
LEFT JOIN order_item oi ON o.id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.id
WHERE o.id = 1;

-- =================================================
-- 5. BASIC ADMIN QUERIES
-- =================================================

-- Get all orders (admin view)
SELECT 
    o.id, o.created_at, o.total_amount,
    os.status,
    u.username, u.email
FROM orders o
INNER JOIN order_status os ON o.order_status_id = os.id
INNER JOIN users u ON o.user_id = u.id
ORDER BY o.created_at DESC;

-- Update order status (set order_id=1 to 'processing')
UPDATE orders 
SET order_status_id = (SELECT id FROM order_status WHERE status = 'processing')
WHERE id = 1;

-- Get low stock products
SELECT id, sku, description, stock_quantity
FROM products 
WHERE stock_quantity <= 25 AND is_active = true
ORDER BY stock_quantity ASC;

-- Update product stock (set product_id=1 to 45 units)
UPDATE products SET stock_quantity = 45 WHERE id = 1;

-- =================================================
-- 6. REFERENCE DATA
-- =================================================

-- Get categories
SELECT id, category FROM product_categories ORDER BY category;

-- Get pet types  
SELECT id, type FROM pet_types ORDER BY type;

-- Get order statuses
SELECT id, status FROM order_status ORDER BY id;

-- =================================================
-- 7. RETURNS (Basic)
-- =================================================

-- Get user's returns (user_id = 1)
SELECT 
    r.id, r.created_at, r.total_amount,
    rs.status,
    o.id as order_id
FROM returns r
INNER JOIN return_status rs ON r.return_status_id = rs.id
INNER JOIN orders o ON r.order_id = o.id
WHERE r.user_id = 1
ORDER BY r.created_at DESC;

-- Get return details (return_id = 1)
SELECT 
    r.id as return_id, r.created_at, r.total_amount,
    rs.status,
    o.id as order_id,
    ri.quantity, ri.amount, ri.reason,
    p.sku, p.description, p.brand
FROM returns r
INNER JOIN return_status rs ON r.return_status_id = rs.id
INNER JOIN orders o ON r.order_id = o.id
LEFT JOIN return_item ri ON r.id = ri.return_id
LEFT JOIN products p ON ri.product_id = p.id
WHERE r.id = 1;

-- Create return for order (order_id = 1, user_id = 1)
INSERT INTO returns (order_id, user_id, return_status_id, total_amount, created_at)
VALUES (1, 1, 1, 16.50, NOW());

-- =================================================
-- 8. INVOICES (Basic)
-- =================================================

-- Get user's invoices (user_id = 1)
SELECT 
    i.id, i.created_at, i.due_date, i.total_amount,
    ist.name as invoice_status,
    o.id as order_id
FROM invoices i
INNER JOIN invoice_status ist ON i.invoice_status_id = ist.id
INNER JOIN orders o ON i.order_id = o.id
WHERE i.user_id = 1
ORDER BY i.created_at DESC;

-- Get invoice details (invoice_id = 1)
SELECT 
    i.id as invoice_id, i.created_at, i.due_date, i.total_amount,
    ist.name as invoice_status,
    o.id as order_id,
    u.username, u.email, u.first_name, u.last_name,
    oi.quantity, oi.amount,
    p.sku, p.description, p.brand
FROM invoices i
INNER JOIN invoice_status ist ON i.invoice_status_id = ist.id
INNER JOIN orders o ON i.order_id = o.id
INNER JOIN users u ON i.user_id = u.id
LEFT JOIN order_item oi ON o.id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.id
WHERE i.id = 1;

-- Create invoice for order (order_id = 1, user_id = 1)
INSERT INTO invoices (order_id, total_amount, invoice_status_id, user_id, created_at, due_date)
VALUES (1, 31.00, 1, 1, NOW(), NOW() + INTERVAL '30 days');

-- Update invoice status (set invoice_id=1 to 'paid')
UPDATE invoices 
SET invoice_status_id = (SELECT id FROM invoice_status WHERE name = 'paid')
WHERE id = 1;

