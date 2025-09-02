-- SQLite

-- Categories
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(25) UNIQUE NOT NULL,
    description TEXT
);

ALTER TABLE products
    ADD category_id INTEGER DEFAULT NULL REFERENCES categories(id) ON UPDATE CASCADE ON DELETE RESTRICT;

INSERT INTO categories (name, description)
    VALUES ('beauty', 'Various beauty items');
INSERT INTO categories (name, description)
    VALUES ('cleaning', 'Cleaning items');
INSERT INTO categories (name, description)
    VALUES ('toiletries', 'Toiletry items');

UPDATE products
    set category_id = 1 WHERE name = 'brush';
UPDATE products
    set category_id = 3 WHERE name = 'shampoo';
UPDATE products
    set category_id = 1 WHERE name = 'perfume';
UPDATE products
    set category_id = 3 WHERE name = 'lotion';
UPDATE products
    set category_id = 2 WHERE name = 'soap';

SELECT * FROM products;