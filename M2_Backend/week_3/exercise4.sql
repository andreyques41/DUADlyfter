-- SQLite
SELECT * 
    FROM products;
    
SELECT * 
    FROM products
    WHERE price > 5000;

SELECT * FROM bill_detail
    ORDER BY product_id;

SELECT product_id, SUM(quantity) AS total_quantity
    FROM bill_detail
    GROUP BY product_id
    ORDER BY total_quantity ASC;

SELECT * FROM bills
    WHERE user_id = 2;

SELECT * FROM bills
    ORDER BY total_amount DESC;

SELECT * FROM bills
    WHERE bill_number = 1004;