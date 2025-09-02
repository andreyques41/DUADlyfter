-- SQLite

SELECT * FROM bill_detail;
    
UPDATE bill_detail
    SET quantity = 0 WHERE line_total <= 0;

UPDATE bill_detail
    SET line_total = line_total + 100 WHERE quantity < 10;

UPDATE bill_detail
    SET quantity = quantity - 1 WHERE product_id = 9;

SELECT * FROM bill_detail ORDER BY id ASC LIMIT 10;