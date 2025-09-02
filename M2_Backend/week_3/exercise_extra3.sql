-- SQLite

UPDATE bills
    set phone_number = '+506-88888888', cashier_code = 'EMP001' WHERE bill_number = '1001';
UPDATE bills
    set phone_number = '+506-77778888', cashier_code = 'EMP002' WHERE bill_number = '1002';
UPDATE bills
    set phone_number = '+506-66667777', cashier_code = 'EMP003' WHERE bill_number = '1003';
UPDATE bills
    set phone_number = '+506-44445555', cashier_code = 'EMP002' WHERE bill_number = '1005';

SELECT * FROM bills
    WHERE phone_number LIKE '%unknown%';

SELECT * FROM bills
    WHERE id = 3;