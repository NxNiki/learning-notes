USE sql_store;

SELECT *
FROM customers
-- WHERE customer_id=1
ORDER BY first_name
;

SELECT 
	first_name, 
    last_name, 
    points, 
	points * 10 + 100 AS point2
FROM customers
;

SELECT DISTINCT state
FROM customers
;

SELECT name, unit_price, unit_price*1.1 as new_price
FROM products
;

SELECT *
FROM Customers
WHERE points > 3000
;

SELECT *
FROM Customers
-- WHERE state != 'va'
WHERE birth_date > '1990-01-01'
;

SELECT *
FROM Customers
WHERE state IN ('VA', 'FL', 'GA')
;

SELECT *
FROM Customers
WHERE birth_date BETWEEN '1980-1-1' AND '1990-1-1'
;

SELECT *
FROM Customers
-- WHERE last_name LIKE 'b%'
WHERE last_name LIKE '_____y' 
-- % any number of character
-- _ single character
;

SELECT *
FROM Customers
-- WHERE last_name REGEXP 'field'
-- WHERE last_name REGEXP '^field'
-- WHERE last_name REGEXP 'field$'
-- WHERE last_name REGEXP 'field|mac|rose'
-- WHERE last_name REGEXP '[gim]e'
WHERE last_name REGEXP '[a-h]e'
;

SELECT *
FROM customers
-- WHERE phone IS NOT NULL
WHERE phone IS NULL
;

SELECT *
FROM customers
-- ORDER BY first_name
ORDER BY state DESC, first_name DESC
;
-- can use order on columns not selected, or by aliens

SELECT *
FROM customers
ORDER BY points
-- LIMIT 5
LIMIT 6,3 -- skip first 6 and show next 3 rows. 
-- limit clause always comes last.
;

# select data from multiple columns
SELECT order_id, orders.customer_id, first_name, last_name 
FROM orders
JOIN customers 
	ON orders.customer_id = customers.customer_id
;

SELECT order_id, o.customer_id, first_name, last_name 
FROM orders o
JOIN customers c 
	ON o.customer_id = c.customer_id
;

SELECT *
FROM order_items oi
JOIN sql_inventory.products p
	ON oi.product_id = p.product_id
;

-- self join
USE sql_hr;
SELECT 
	e.employee_id,
	e.first_name,
    m.first_name AS manager
FROM employees e
JOIN employees m
	ON e.reports_to = m.employee_id
;

USE sql_store;

SELECT 
	o.order_id,
    o.order_date,
    c.first_name,
    c.last_name,
    os.name AS status
FROM orders o
JOIN customers c
	ON o.customer_id = c.customer_id
JOIN order_statuses os
	ON o.status = os.order_status_id
;

SELECT *
FROM order_items oi
JOIN order_item_notes oin
	ON oi.order_id = oin.order_id
    AND oi.product_id = oin.product_id
;


-- implicit join syntax
SELECT *
FROM orders o, customers c
WHERE o.customer_id = c.customer_id
;
-- cross join is where clause is missing

-- outer join
SELECT 
	c.customer_id,
    c.first_name,
    o.order_id
FROM customers c
LEFT JOIN orders o
	ON c.customer_id = o.customer_id
;

-- avoid right joins, using left joins for simplicity.


-- Using clause
SELECT
	o.order_id,
    c.first_name,
    sh.name AS shipper
FROM orders o
JOIN customers c
	USING (customer_id)
LEFT JOIN shippers sh
	USING (shipper_id)
;


SELECT *
FROM order_items oi
JOIN order_item_notes oin
	USING (order_id, product_id)
;

USE sql_invoicing;

SELECT 
	p.date,
    c.name AS client,
    p.amount,
    pm.name AS payment_method
FROM payments p
JOIN clients c USING (client_id)
JOIN payment_methods pm
	ON p.payment_method = pm.payment_method_id
;

-- natural joins:
SELECT
	o.order_id,
    c.first_name
FROM orders o
NATURAL JOIN customers c
;

-- cross joins:

SELECT
	c.first_name AS customer,
    p.name AS product
FROM customers c
CROSS JOIN products p
ORDER BY c.first_name
;

# implicit syntax:
SELECT
	c.first_name AS customer,
    p.name AS product
FROM customers c, products p -- this will use cross join
ORDER BY c.first_name
;

-- Uions: combine rows of tables:
SELECT 
	order_id,
    order_date,
    'Active' AS status
FROM orders
WHERE order_date >= '2019-01-01'
UNION
SELECT 
	order_id,
    order_date,
    'Archived' AS status
FROM orders
WHERE order_date < '2019-01-01'
;


