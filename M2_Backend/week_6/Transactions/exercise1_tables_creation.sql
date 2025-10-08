-- Set schema for all operations
SET search_path TO backend_week6_transactions;
-- Simple database for products, users, and invoices (facturas)

-- 1. Create tables in dependency order
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL
);

CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  sku VARCHAR(10) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  stock INTEGER NOT NULL
);

CREATE TABLE invoices (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  state VARCHAR(20) NOT NULL DEFAULT 'Pending',
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE invoice_details (
  id SERIAL PRIMARY KEY,
  invoice_id INTEGER REFERENCES invoices(id) ON DELETE RESTRICT NOT NULL,
  product_id INTEGER REFERENCES products(id) ON DELETE RESTRICT NOT NULL,
  quantity INTEGER NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  delivered BOOLEAN NOT NULL DEFAULT FALSE
);

-- 2. Insert data in the same order
INSERT INTO users (name, email) VALUES
  ('Alice Smith', 'alice@example.com'),
  ('Bob Johnson', 'bob@example.com'),
  ('Charlie Lee', 'charlie@example.com');

INSERT INTO products (sku, name, price, stock) VALUES
  ('P001', 'Laptop', 1200.00, 10),
  ('P002', 'Smartphone', 800.00, 20),
  ('P003', 'Headphones', 150.00, 30);

INSERT INTO invoices (user_id, date, state) VALUES
  (1, '2025-10-01 10:00:00', 'Pending'),
  (2, '2025-10-01 11:00:00', 'Pending');

INSERT INTO invoice_details (invoice_id, product_id, quantity, price) VALUES
  (1, 1, 1, 1200.00),
  (1, 3, 2, 150.00),
  (2, 2, 1, 800.00);