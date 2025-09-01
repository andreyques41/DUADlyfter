-- SQLite

ALTER TABLE bills 
    ADD phone_number VARCHAR(20) NOT NULL DEFAULT 'unknown';

CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code CHAR(10) NOT NULL UNIQUE,
	full_name VARCHAR(25) NOT NULL
);

ALTER TABLE bills 
    ADD cashier_code CHAR(10) NOT NULL DEFAULT 'unknown' REFERENCES employees(code) ON UPDATE CASCADE ON DELETE RESTRICT;

-- Employees
INSERT INTO employees (code, full_name) VALUES ('EMP001', 'John Smith');
INSERT INTO employees (code, full_name) VALUES ('EMP002', 'Emily Johnson');
INSERT INTO employees (code, full_name) VALUES ('EMP003', 'Carlos Martinez');