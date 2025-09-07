-- SQLite

SELECT customers.name, COUNT(*) AS rent_count
    FROM customers INNER JOIN rents
    ON customers.id = rents.customer_id
    GROUP BY customers.name
    ORDER BY rent_count DESC
    LIMIT 3;

SELECT
    customers.name AS customer_name,
    books.name AS book_name,
    authors.name AS author_name,
    rents.state AS rent_state
    FROM rents
    INNER JOIN customers ON customers.id = rents.customer_id
    INNER JOIN books ON books.id = rents.book_id
    LEFT JOIN authors ON books.author = authors.id;