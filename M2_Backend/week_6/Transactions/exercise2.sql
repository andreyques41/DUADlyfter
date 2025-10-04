-- Set schema for all operations
SET search_path TO backend_week6_transactions;

DO $$
DECLARE
    v_product_id INTEGER;
    v_price DECIMAL(10,2);
    v_user_id INTEGER;
    v_invoice_id INTEGER;
BEGIN
    -- 1. Validate product stock and get id/price
    SELECT id, price INTO v_product_id, v_price
    FROM products
    WHERE sku = 'P001' AND stock > 0;

    IF v_product_id IS NULL THEN
        RAISE EXCEPTION 'No stock or product not found';
    END IF;

    -- 2. Validate user
    SELECT id INTO v_user_id
    FROM users
    WHERE name = 'Bob Johnson';

    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'User not found';
    END IF;

    -- 3. Create invoice
    INSERT INTO invoices (user_id, date, state)
    VALUES (v_user_id, CURRENT_TIMESTAMP, 'Pending')
    RETURNING id INTO v_invoice_id;

    -- 4. Create invoice detail
    INSERT INTO invoice_details (invoice_id, product_id, quantity, price)
    VALUES (v_invoice_id, v_product_id, 1, v_price);

    -- 5. Reduce stock
    UPDATE products
    SET stock = stock - 1
    WHERE id = v_product_id;

    -- All statements in DO block are atomic in PostgreSQL
END $$;