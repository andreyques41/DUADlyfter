DO $$
DECLARE
    v_invoice_id INTEGER := 1; -- Example: returning invoice with id 1
    v_product_id INTEGER;
    v_quantity INTEGER;
BEGIN
    -- 1. Validate that the invoice exists
    IF NOT EXISTS (
        SELECT 1 FROM invoices WHERE id = v_invoice_id
    ) THEN
        RAISE EXCEPTION 'Invoice does not exist';
    END IF;

    -- 2. For each product in the invoice, increase stock by the quantity purchased
    FOR v_product_id, v_quantity IN
        SELECT product_id, quantity FROM invoice_details WHERE invoice_id = v_invoice_id
    LOOP
        UPDATE products
        SET stock = stock + v_quantity
        WHERE id = v_product_id;
    END LOOP;

    -- 3. Update the invoice to mark as returned
    UPDATE invoices
    SET state = 'Returned'
    WHERE id = v_invoice_id;

    -- Commit transaction
    COMMIT;
END $$;
