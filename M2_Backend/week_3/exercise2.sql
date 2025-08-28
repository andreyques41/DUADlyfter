
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