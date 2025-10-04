-- Set schema for all operations
SET search_path TO backend_week6_transactions;

DO $$
DECLARE
    v_invoice_id INTEGER := 2; -- Example: cancel invoice with id 1
    v_product_id INTEGER;
    v_quantity INTEGER;
    v_state VARCHAR(20);
BEGIN
    -- 1. Check that the invoice is in 'Pending' state
    SELECT state INTO v_state FROM invoices WHERE id = v_invoice_id;
    IF v_state IS NULL THEN
        RAISE EXCEPTION 'Invoice does not exist';
    ELSIF v_state <> 'Pending' THEN
        RAISE EXCEPTION 'Invoice is not in Pending state';
    END IF;

    -- 2. For each product in the invoice that has NOT been delivered, return stock
    FOR v_product_id, v_quantity IN
        SELECT product_id, quantity FROM invoice_details WHERE invoice_id = v_invoice_id AND delivered = FALSE
    LOOP
        UPDATE products
        SET stock = stock + v_quantity
        WHERE id = v_product_id;
    END LOOP;

    -- 3. Update the invoice to mark as cancelled
    UPDATE invoices
    SET state = 'Cancelled'
    WHERE id = v_invoice_id;

    -- All statements in DO block are atomic in PostgreSQL
END $$;
