-- SQLite

INSERT INTO products (product_code, name, price, brand, category_id)
    VALUES ('F11G', 'toothpaste', 1100, 'COLGATE', 2);
INSERT INTO products (product_code, name, price, brand, category_id)
    VALUES ('G22H', 'face cream', 5000, 'NIVEA', 1);
INSERT INTO products (product_code, name, price, brand, category_id)
    VALUES ('H33I', 'body wash', 2500, 'DOVE', NULL);
INSERT INTO products (product_code, name, price, brand, category_id)
    VALUES ('I44J', 'deodorant', 1800, 'AXE', 1);
INSERT INTO products (product_code, name, price, brand, category_id)
    VALUES ('J55K', 'hand soap', 1300, 'PALMOLIVE', 2);
INSERT INTO products (product_code, name, price, brand, category_id)
    VALUES ('K66L', 'shaving gel', 3200, 'GILLETTE', NULL);
INSERT INTO products (product_code, name, price, brand, category_id)
    VALUES ('L77M', 'hair spray', 2100, 'TRESEMME', 1);
INSERT INTO products (product_code, name, price, brand, category_id)
    VALUES ('M88N', 'mouthwash', 1700, 'LISTERINE', 2);
INSERT INTO products (product_code, name, price, brand, category_id)
    VALUES ('N99O', 'cotton swabs', 1200, 'Q-TIPS', NULL);

SELECT * FROM products;

SELECT * 
    FROM products
    WHERE price > 3000;

SELECT * 
    FROM products
    WHERE name LIKE '%soap%';

SELECT * 
    FROM products
    ORDER BY price DESC LIMIT 5;

-- Bill detail for new products
INSERT INTO bill_detail (quantity, line_total, product_id, bill_id)
    VALUES (2, 2200, 6, 1); -- shaving gel
INSERT INTO bill_detail (quantity, line_total, product_id, bill_id)
    VALUES (1, 1100, 7, 2); -- hair spray
INSERT INTO bill_detail (quantity, line_total, product_id, bill_id)
    VALUES (3, 5100, 8, 3); -- mouthwash
INSERT INTO bill_detail (quantity, line_total, product_id, bill_id)
    VALUES (4, 4800, 9, 4); -- cotton swabs
INSERT INTO bill_detail (quantity, line_total, product_id, bill_id)
    VALUES (1, 5000, 3, 5); -- face cream
INSERT INTO bill_detail (quantity, line_total, product_id, bill_id)
    VALUES (2, 2600, 4, 1); -- body wash
INSERT INTO bill_detail (quantity, line_total, product_id, bill_id)
    VALUES (1, 1800, 5, 2); -- deodorant
INSERT INTO bill_detail (quantity, line_total, product_id, bill_id)
    VALUES (3, 3900, 10, 3); -- hand soap