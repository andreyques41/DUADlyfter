-- =================================================
-- PET E-COMMERCE SAMPLE DATA INSERTS
-- Schema: lyfter_backend_project
-- =================================================

-- Set schema for all operations
SET search_path TO lyfter_backend_project;

-- =================================================
-- 1. CORE REFERENCE TABLES
-- =================================================

-- Insert Roles
INSERT INTO roles (name, description) VALUES
('admin', 'System administrator with full access'),
('customer', 'Regular customer user'),
('employee', 'Store employee with limited access'),
('manager', 'Store manager with elevated permissions');

-- Insert Product Categories
INSERT INTO product_categories (category) VALUES
('Food'),
('Toys'),
('Accessories'),
('Health & Care'),
('Training');

-- Insert Pet Types
INSERT INTO pet_types (type) VALUES
('Dog'),
('Cat'),
('Bird'),
('Fish'),
('Small Animal');

-- Insert Order Status
INSERT INTO order_status (status) VALUES
('pending'),
('processing'),
('shipped'),
('delivered'),
('cancelled');

-- Insert Return Status
INSERT INTO return_status (status) VALUES
('requested'),
('approved'),
('rejected'),
('processing'),
('completed');

-- Insert Invoice Status
INSERT INTO invoice_status (name) VALUES
('draft'),
('sent'),
('paid'),
('overdue'),
('cancelled');

-- =================================================
-- 2. USERS AND AUTHENTICATION
-- =================================================

-- Insert Users
INSERT INTO users (username, email, password_hash, first_name, last_name, phone) VALUES
('john_doe', 'john.doe@email.com', 'hashed_password_123', 'John', 'Doe', '555-0101'),
('jane_smith', 'jane.smith@email.com', 'hashed_password_456', 'Jane', 'Smith', '555-0102'),
('mike_wilson', 'mike.wilson@email.com', 'hashed_password_789', 'Mike', 'Wilson', '555-0103'),
('sarah_johnson', 'sarah.johnson@email.com', 'hashed_password_321', 'Sarah', 'Johnson', '555-0104'),
('admin_user', 'admin@petstore.com', 'hashed_admin_pass', 'Admin', 'User', '555-0100'),
('employee1', 'emp1@petstore.com', 'hashed_emp_pass1', 'Tom', 'Brown', '555-0201'),
('manager1', 'mgr1@petstore.com', 'hashed_mgr_pass1', 'Lisa', 'Davis', '555-0301');

-- Insert Role_User relationships
INSERT INTO role_user (role_id, user_id) VALUES
(1, 5), -- admin_user -> admin
(2, 1), -- john_doe -> customer
(2, 2), -- jane_smith -> customer
(2, 3), -- mike_wilson -> customer
(2, 4), -- sarah_johnson -> customer
(3, 6), -- employee1 -> employee
(4, 7); -- manager1 -> manager

-- =================================================
-- 3. PRODUCTS
-- =================================================

-- Insert Products
INSERT INTO products (sku, description, product_category_id, pet_type_id, stock_quantity, price, brand, weight, is_active, internal_cost, supplier_info, created_by, last_updated) VALUES
('PF001', 'Premium Dog Food 5kg', 1, 1, 50, 20, 'PetNutrition', 5.0, true, 15.50, 'Supplier A', 'admin_user', '2024-09-01 10:00:00'),
('PF002', 'Cat Food Salmon Flavor 2kg', 1, 2, 75, 18, 'FelineChoice', 2.0, true, 8.25, 'Supplier B', 'admin_user', '2024-09-01 10:30:00'),
('PT001', 'Interactive Dog Toy Ball', 2, 1, 30, 8, 'PlayTime', 0.3, true, 5.00, 'Supplier C', 'admin_user', '2024-09-01 11:00:00'),
('PT002', 'Cat Laser Pointer', 2, 2, 40, 5, 'CatFun', 0.1, true, 3.50, 'Supplier C', 'admin_user', '2024-09-01 11:15:00'),
('PA001', 'Dog Collar Large', 3, 1, 25, 14, 'PetGear', 0.2, true, 7.00, 'Supplier D', 'admin_user', '2024-09-01 12:00:00'),
('PA002', 'Cat Carrier Medium', 3, 2, 15, 30, 'SafeTravel', 2.5, true, 25.00, 'Supplier D', 'admin_user', '2024-09-01 12:30:00'),
('PH001', 'Dog Vitamins 60 tablets', 4, 1, 60, 20, 'HealthyPet', 0.5, true, 12.00, 'Supplier E', 'admin_user', '2024-09-01 13:00:00'),
('PH002', 'Flea Shampoo for Cats', 4, 2, 35, 15, 'CleanCoat', 0.4, true, 9.75, 'Supplier E', 'admin_user', '2024-09-01 13:30:00');

-- =================================================
-- 4. SHOPPING CARTS
-- =================================================

-- Insert Carts
INSERT INTO carts (user_id, created_at, finalized) VALUES
(1, '2024-09-20 14:00:00', false), -- john_doe - active cart
(2, '2024-09-21 10:30:00', true), -- jane_smith - finalized cart
(3, '2024-09-22 16:45:00', true), -- mike_wilson - finalized cart
(4, '2024-09-23 09:15:00', false); -- sarah_johnson - active cart

-- Insert Cart Items
INSERT INTO cart_item (product_id, cart_id, amount, quantity) VALUES
-- john_doe's active cart
(1, 1, 31.00, 2), -- 2x Premium Dog Food
(3, 1, 12.50, 1), -- 1x Interactive Dog Toy Ball
-- jane_smith's finalized cart
(2, 2, 16.50, 2), -- 2x Cat Food Salmon
(4, 2, 7.00, 1),  -- 1x Cat Laser Pointer
-- mike_wilson's finalized cart
(5, 3, 14.00, 2), -- 2x Dog Collar Large
(7, 3, 24.00, 2), -- 2x Dog Vitamins
-- sarah_johnson's active cart
(6, 4, 50.00, 2), -- 2x Cat Carrier Medium
(8, 4, 19.50, 2); -- 2x Flea Shampoo for Cats

-- =================================================
-- 5. ORDERS
-- =================================================

-- Insert Orders
INSERT INTO orders (cart_id, user_id, order_status_id, total_amount, created_at, shipping_address) VALUES
(2, 2, 3, 23.50, '2024-09-21 11:00:00', '123 Main St, New York, NY 10001'),
(3, 3, 4, 38.00, '2024-09-22 17:00:00', '456 Oak Ave, Los Angeles, CA 90210');

-- Insert Order Items
INSERT INTO order_item (product_id, order_id, amount, quantity) VALUES
-- jane_smith's order
(2, 1, 16.50, 2), -- 2x Cat Food Salmon
(4, 1, 7.00, 1),  -- 1x Cat Laser Pointer
-- mike_wilson's order
(5, 2, 14.00, 2), -- 2x Dog Collar Large
(7, 2, 24.00, 2); -- 2x Dog Vitamins

-- =================================================
-- 6. RETURNS
-- =================================================

-- Insert Returns
INSERT INTO returns (order_id, user_id, return_status_id, total_amount, created_at) VALUES
(1, 2, 2, 16.50, '2024-09-23 14:30:00'), -- jane_smith returning cat food
(2, 3, 1, 14.00, '2024-09-24 09:00:00'); -- mike_wilson requesting return for collars

-- Insert Return Items
INSERT INTO return_item (product_id, return_id, quantity, reason, amount) VALUES
(2, 1, 2, 'Cat is allergic to salmon flavor', 16.50),
(5, 2, 2, 'Wrong size ordered', 14.00);

-- =================================================
-- 7. INVOICES
-- =================================================

-- Insert Invoices
INSERT INTO invoices (order_id, total_amount, invoice_status_id, user_id, created_at, due_date) VALUES
(1, 23.50, 3, 2, '2024-09-21 11:30:00', '2024-10-21 11:30:00'), -- jane_smith's paid invoice
(2, 38.00, 2, 3, '2024-09-22 17:30:00', '2024-10-22 17:30:00'); -- mike_wilson's sent invoice

-- =================================================
-- END OF SAMPLE DATA
-- =================================================