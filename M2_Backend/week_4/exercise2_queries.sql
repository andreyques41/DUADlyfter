-- SQLite

--1
SELECT books.name AS book_name, authors.name AS author_name
    FROM books LEFT JOIN authors
    ON books.author = authors.id;

--2
SELECT * FROM books WHERE author IS NULL;

--3
SELECT books.name AS book_name, authors.name AS author_name
    FROM authors LEFT JOIN books
    ON books.author = authors.id 
    WHERE book_name IS NULL;

--4
SELECT books.name AS book_name
    FROM books INNER JOIN rents
    ON books.id = rents.book_id 
    GROUP by book_name;

--5
SELECT books.name AS book_name
    FROM books LEFT JOIN rents
    ON books.id = rents.book_id 
    WHERE rents.book_id IS NULL
    GROUP by book_name;

--6
SELECT customers.name AS customers_name
    FROM customers LEFT JOIN rents
    ON customers.id = rents.customer_id 
    WHERE rents.customer_id IS NULL
    GROUP by customers_name;

--7
SELECT books.name AS book_name
    FROM books INNER JOIN rents
    ON books.id = rents.book_id 
    WHERE rents.state = 'Overdue'
    GROUP by book_name;