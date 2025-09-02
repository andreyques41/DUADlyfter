
-- SQLite

-- Products
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
	product_code CHAR(10) NOT NULL UNIQUE, --Assuming a 10-character code
    name VARCHAR(25) NOT NULL,
    price DECIMAL(8, 2) CHECK (price BETWEEN 1000 AND 250000) NOT NULL,
	input_date DATE DEFAULT (DATE('now')) NOT NULL,
    brand VARCHAR(25) NOT NULL
);

-- Bills (invoices)
CREATE TABLE bills (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	bill_number INTEGER NOT NULL UNIQUE,
	purchase_date DATE DEFAULT (DATE('now')) NOT NULL,
	total_amount DECIMAL(12, 2) NOT NULL,
	user_id INTEGER NOT NULL REFERENCES users(id) ON UPDATE CASCADE ON DELETE RESTRICT,
	payment_method_id INTEGER NOT NULL REFERENCES payment_methods(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE bill_detail (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	quantity INTEGER NOT NULL CHECK (quantity > 0),
	line_total DECIMAL(10, 2) NOT NULL,
	product_id INTEGER NOT NULL REFERENCES products(id) ON UPDATE CASCADE ON DELETE RESTRICT,
	bill_id INTEGER NOT NULL REFERENCES bills(id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Users
CREATE TABLE users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	full_name VARCHAR(25) NOT NULL,
	email VARCHAR(30) NOT NULL UNIQUE,
	register_date DATE DEFAULT (DATE('now')) NOT NULL
);

CREATE TABLE carts (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE cart_product (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	product_id INTEGER NOT NULL REFERENCES products(id) ON UPDATE CASCADE ON DELETE CASCADE,
	cart_id INTEGER NOT NULL REFERENCES carts(id) ON UPDATE CASCADE ON DELETE CASCADE,
	UNIQUE (product_id, cart_id) --There cannot be two rows in the cart_product table with the same pair of product_id and cart_id
);

-- Payment methods
CREATE TABLE payment_methods (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	type VARCHAR(20) NOT NULL,
	bank_name VARCHAR(25)
);

CREATE TABLE reviews (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	product_code CHAR(10) NOT NULL REFERENCES products(product_code) ON UPDATE CASCADE ON DELETE CASCADE,
	comment TEXT NOT NULL,
	score SMALLINT NOT NULL CHECK (score BETWEEN 1 AND 5),
	date DATE DEFAULT (DATE('now')) NOT NULL,
	user_id INTEGER NOT NULL REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
	UNIQUE (product_code, user_id) --There cannot be two rows in the reviews table with the same pair of product_code and user_id
);


-- Adding valid data to all tables
INSERT INTO products (product_code, name, price, brand)
    VALUES ('A23B', 'brush', 1050, 'DIOR');
INSERT INTO products (product_code, name, price, brand)
    VALUES ('B12C', 'shampoo', 1200, 'PANTENE');
INSERT INTO products (product_code, name, price, brand)
    VALUES ('C34D', 'perfume', 20000, 'CHANEL');
INSERT INTO products (product_code, name, price, brand)
    VALUES ('D56E', 'lotion', 3500, 'NIVEA');
INSERT INTO products (product_code, name, price, brand)
    VALUES ('E78F', 'soap', 1500, 'DOVE');

-- Users
INSERT INTO users (full_name, email)
    VALUES ('Ana Torres', 'ana.torres@email.com');
INSERT INTO users (full_name, email)
    VALUES ('Luis Perez', 'luis.perez@email.com');
INSERT INTO users (full_name, email)
    VALUES ('Maria Lopez', 'maria.lopez@email.com');
INSERT INTO users (full_name, email)
    VALUES ('Carlos Ruiz', 'carlos.ruiz@email.com');
INSERT INTO users (full_name, email)
    VALUES ('Sofia Gomez', 'sofia.gomez@email.com');

-- Payment methods
INSERT INTO payment_methods (type, bank_name)
    VALUES ('Credit Card', 'BBVA');
INSERT INTO payment_methods (type, bank_name)
    VALUES ('Debit Card', 'Santander');
INSERT INTO payment_methods (type, bank_name)
    VALUES ('Cash', NULL);
INSERT INTO payment_methods (type, bank_name)
    VALUES ('Transfer', 'HSBC');
INSERT INTO payment_methods (type, bank_name)
    VALUES ('Digital Wallet', NULL);

-- Bills
INSERT INTO bills (bill_number, total_amount, user_id, payment_method_id)
    VALUES (1001, 1200, 1, 1);
INSERT INTO bills (bill_number, total_amount, user_id, payment_method_id)
    VALUES (1002, 20000, 2, 2);
INSERT INTO bills (bill_number, total_amount, user_id, payment_method_id)
    VALUES (1003, 3500, 3, 3);
INSERT INTO bills (bill_number, total_amount, user_id, payment_method_id)
    VALUES (1004, 1500, 4, 4);
INSERT INTO bills (bill_number, total_amount, user_id, payment_method_id)
    VALUES (1005, 1050, 5, 5);

-- Bill detail
INSERT INTO bill_detail (quantity, line_total, product_id, bill_id)
    VALUES (1, 1200, 2, 1);
INSERT INTO bill_detail (quantity, line_total, product_id, bill_id)
    VALUES (1, 20000, 3, 2);
INSERT INTO bill_detail (quantity, line_total, product_id, bill_id)
    VALUES (2, 7000, 4, 3);
INSERT INTO bill_detail (quantity, line_total, product_id, bill_id)
    VALUES (1, 1500, 5, 4);
INSERT INTO bill_detail (quantity, line_total, product_id, bill_id)
    VALUES (5, 6000, 2, 5);

-- Carts
INSERT INTO carts (user_id) VALUES (1);
INSERT INTO carts (user_id) VALUES (2);
INSERT INTO carts (user_id) VALUES (3);
INSERT INTO carts (user_id) VALUES (4);
INSERT INTO carts (user_id) VALUES (5);

-- Cart product
INSERT INTO cart_product (product_id, cart_id) VALUES (1, 1);
INSERT INTO cart_product (product_id, cart_id) VALUES (2, 2);
INSERT INTO cart_product (product_id, cart_id) VALUES (3, 3);
INSERT INTO cart_product (product_id, cart_id) VALUES (4, 4);
INSERT INTO cart_product (product_id, cart_id) VALUES (5, 5);

-- Reviews
INSERT INTO reviews (product_code, comment, score, user_id)
    VALUES ('A23B', 'Great brush!', 5, 1);
INSERT INTO reviews (product_code, comment, score, user_id)
    VALUES ('B12C', 'Good shampoo', 4, 2);
INSERT INTO reviews (product_code, comment, score, user_id)
    VALUES ('C34D', 'Amazing scent', 5, 3);
INSERT INTO reviews (product_code, comment, score, user_id)
    VALUES ('D56E', 'Nice lotion', 4, 4);
INSERT INTO reviews (product_code, comment, score, user_id)
    VALUES ('E78F', 'Mild soap', 3, 5);