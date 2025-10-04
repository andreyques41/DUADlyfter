-- Set schema for all operations
SET search_path TO backend_week6_transactions;

-- Example: user 1 wants to buy 2 units of product 1 and 1 unit of product 3 in a single invoice
-- You can adjust the arrays for other test cases
DO $$
DECLARE
    v_user_id INTEGER := 1;
    v_invoice_id INTEGER;
    v_product_ids INTEGER[] := ARRAY[1, 3];
    v_quantities INTEGER[] := ARRAY[5, 3];
    v_prices DECIMAL(10,2)[] := ARRAY[1200.00, 150.00];
    i INTEGER;
    v_stock INTEGER;
BEGIN
    -- 1. Validate stock for all requested products
    FOR i IN 1..array_length(v_product_ids, 1) LOOP
        SELECT stock INTO v_stock FROM products WHERE id = v_product_ids[i];
        IF v_stock IS NULL OR v_stock < v_quantities[i] THEN
            RAISE EXCEPTION 'Insufficient stock for product id %', v_product_ids[i];
        END IF;
    END LOOP;

    -- 2. Create invoice
    INSERT INTO invoices (user_id, date, state)
    VALUES (v_user_id, CURRENT_TIMESTAMP, 'Pending')
    RETURNING id INTO v_invoice_id;

    -- 3. Insert invoice details and reduce stock
    FOR i IN 1..array_length(v_product_ids, 1) LOOP
        INSERT INTO invoice_details (invoice_id, product_id, quantity, price)
        VALUES (v_invoice_id, v_product_ids[i], v_quantities[i], v_prices[i]);

        UPDATE products
        SET stock = stock - v_quantities[i]
        WHERE id = v_product_ids[i];
    END LOOP;

    -- All statements in DO block are atomic in PostgreSQL
END $$;
