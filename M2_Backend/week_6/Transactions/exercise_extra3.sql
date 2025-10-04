-- Set schema for all operations
SET search_path TO backend_week6_transactions;

-- Example: two users try to buy the last unit of product 1 (P001)
-- We'll simulate one user (user 1) trying to buy 1 unit of product 1
DO $$
DECLARE
    v_user_id INTEGER := 1;
    v_invoice_id INTEGER;
    v_product_id INTEGER := 1;
    v_quantity INTEGER := 1;
    v_price DECIMAL(10,2);
    v_stock INTEGER;
    v_stock_before INTEGER;
BEGIN
    -- 1. Read current stock and price
    SELECT stock, price INTO v_stock_before, v_price FROM products WHERE id = v_product_id;
    IF v_stock_before IS NULL OR v_stock_before < v_quantity THEN
        RAISE EXCEPTION 'Insufficient stock for product id %', v_product_id;
    END IF;

    -- 2. Create invoice
    INSERT INTO invoices (user_id, date, state)
    VALUES (v_user_id, CURRENT_TIMESTAMP, 'Pending')
    RETURNING id INTO v_invoice_id;

    -- 3. Try to update stock only if it hasn't changed
    UPDATE products
    SET stock = stock - v_quantity
    WHERE id = v_product_id AND stock = v_stock_before;

    -- 4. Check if the update succeeded
    GET DIAGNOSTICS v_stock = ROW_COUNT;
    IF v_stock = 0 THEN
        RAISE EXCEPTION 'Stock was modified by another transaction. Aborting purchase.';
    END IF;

    -- 5. Insert invoice detail
    INSERT INTO invoice_details (invoice_id, product_id, quantity, price)
    VALUES (v_invoice_id, v_product_id, v_quantity, v_price);

    -- All statements in DO block are atomic in PostgreSQL
END $$;
