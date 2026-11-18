# SQL Learning Notes

- **Course notes**: Mosh SQL course topics (`topic_*.sql`), https://codewithmosh.com/courses
- **Practice problems**: [LeetCode SQL problems](./leetcode/) with solutions and notes
- **Concepts**: evaluation order, window functions, aliases, NULL handling, subqueries, stored functions (below)

Examples use MySQL 8 syntax unless noted.

---

## 1. Logical Processing Order

SQL clauses are evaluated in this order, which explains most "why can't I use X here" errors:

```
1. FROM / JOIN
2. WHERE         filter rows
3. GROUP BY      form groups
4. HAVING        filter groups (aggregates available)
5. SELECT        compute expressions, window functions, create aliases
6. DISTINCT      remove duplicates
7. ORDER BY      sort (aliases and window functions available)
8. LIMIT/OFFSET
```

Rule of thumb: anything created in step 5 only exists in steps 6-8. To filter on it, compute it in a CTE or subquery and filter in the outer query.

### Window functions

A window function has an `OVER (...)` clause. It computes a value per row **without collapsing rows**. Allowed only in `SELECT` and `ORDER BY`, never in `WHERE`, `GROUP BY`, or `HAVING`.

```sql
-- ❌ Error: window function in WHERE/HAVING
SELECT DISTINCT salary FROM Employee
HAVING DENSE_RANK() OVER (ORDER BY salary DESC) = 2;

-- ✅ Compute first, filter in the outer query
WITH ranked AS (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM Employee
)
SELECT salary FROM ranked WHERE rnk = 2;
```

> `rank` is a reserved word in MySQL 8, so use an alias like `rnk`.

**Window vs aggregate:** the same function can be either, depending on `OVER`.

| | Syntax | Rows in result |
|---|---|---|
| Aggregate | `MIN(salary)` | Collapses to 1 row (per group) |
| Window | `MIN(salary) OVER (...)` | Keeps every row, adds a column |

### Column aliases

Aliases are created in `SELECT` (step 5):

| Where | Alias usable? |
|---|---|
| `WHERE` | ❌ (not created yet) |
| Same `SELECT` list | ❌ (`salary*12 AS annual, annual*0.1` fails) |
| `GROUP BY` / `HAVING` | ❌ in standard SQL; MySQL allows both, PostgreSQL allows `GROUP BY` only |
| `ORDER BY` | ✅ |

```sql
-- ❌ Unknown column 'annual'
SELECT salary * 12 AS annual FROM Employee WHERE annual > 100000;

-- ✅ Repeat the expression, or wrap in a subquery
SELECT * FROM (SELECT salary * 12 AS annual FROM Employee) t
WHERE annual > 100000;
```

---

## 2. NULL vs Empty Result

When nothing matches, whether you get **one row containing NULL** or **zero rows** depends on the query shape:

| Query shape | No matching rows gives |
|---|---|
| Aggregate without `GROUP BY` (`MIN`, `MAX`, `SUM`, `AVG`) | 1 row, `NULL` |
| `COUNT(*)` without `GROUP BY` | 1 row, `0` |
| Plain `SELECT` / `SELECT DISTINCT` | 0 rows |
| Scalar subquery (see below) | `NULL` |

This matters for "Nth highest" problems, which expect `NULL` rather than an empty table. Three ways to get it:

```sql
-- 1. Aggregate: always returns exactly one row
WITH cte AS (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM Employee
)
SELECT MIN(salary) AS SecondHighestSalary FROM cte WHERE rnk = 2;

-- 2. Scalar subquery: the inner query returns 0 rows, the wrapper turns it into NULL
SELECT (
    SELECT DISTINCT salary FROM Employee
    ORDER BY salary DESC
    LIMIT 1 OFFSET 1
) AS SecondHighestSalary;

-- 3. RETURN in a stored function: also a scalar subquery (see section 4)
```

Without `MIN` or the wrapper, `SELECT salary FROM cte WHERE rnk = 2` returns an empty table.

`NULL` also affects comparisons: `x = NULL` and `x <> NULL` are `UNKNOWN`, never true. This is what breaks `NOT IN` (section 3).

`DISTINCT` matters in the `LIMIT/OFFSET` version: without it, duplicate top salaries (300, 300, 200) would make `OFFSET 1` return 300 again.

---

## 3. Subqueries

### Scalar subqueries

A scalar subquery returns **exactly 1 column and at most 1 row**, so it can be used anywhere a single value can: `SELECT`, `WHERE`, `HAVING`, `ORDER BY`, `CASE`, arithmetic.

| Inner query returns | Result |
|---|---|
| 1 row | that value |
| 0 rows | `NULL` |
| more than 1 row | error: *Subquery returns more than 1 row* |
| more than 1 column | error: *Operand should contain 1 column(s)* |

```sql
SELECT name, salary
FROM Employee
WHERE salary > (SELECT AVG(salary) FROM Employee);
```

Guarantee a single row with an aggregate or `LIMIT 1`. If you need several columns, use a derived table (`FROM (SELECT ...) t`) or several scalar subqueries.

| Subquery type | Columns | Rows | Example |
|---|---|---|---|
| Scalar | 1 | 0 or 1 | `(SELECT MAX(salary) FROM Employee)` |
| `IN` list | 1 | any | `WHERE id IN (SELECT id FROM ...)` |
| Derived table | any | any | `FROM (SELECT ...) t` |

### Correlated subqueries

A correlated subquery references the outer query, so logically it runs once per outer row:

```sql
SELECT e.name,
       (SELECT AVG(salary) FROM Employee e2 WHERE e2.dept_id = e.dept_id) AS dept_avg
FROM Employee e;
```

They are not automatically slow; modern optimizers often rewrite them as joins. Check with `EXPLAIN` rather than guessing.

- **Good fits**: `EXISTS` / `NOT EXISTS` (stops at the first match), small outer tables, an indexed correlation column, or when it is the most readable option.
- **Prefer alternatives** for large tables without indexes, several subqueries hitting the same table (use one `GROUP BY` join), or nested correlation. Per-group aggregates are usually cleaner as window functions: `AVG(salary) OVER (PARTITION BY dept_id)`.

### Anti-joins: `NOT IN` vs `NOT EXISTS`

An **anti-join** keeps rows of one table that have **no match** in another, e.g. customers who never ordered (LeetCode 183):

```sql
-- NOT IN: compares values against a list
SELECT name FROM Customers
WHERE id NOT IN (SELECT customerId FROM Orders);

-- NOT EXISTS: checks whether a matching row exists (correlated)
SELECT c.name FROM Customers c
WHERE NOT EXISTS (SELECT 1 FROM Orders o WHERE o.customerId = c.id);

-- LEFT JOIN: keep unmatched rows, then filter them
SELECT c.name FROM Customers c
LEFT JOIN Orders o ON o.customerId = c.id
WHERE o.customerId IS NULL;
```

**The `NULL` trap in `NOT IN`.** SQL comparisons with `NULL` are `UNKNOWN`, not true or false, and `WHERE` keeps only true rows. `NOT IN` expands to a chain of `<>`:

```sql
id NOT IN (1, 2, NULL)
-- = id <> 1 AND id <> 2 AND id <> NULL
-- = ... AND UNKNOWN  → never TRUE → query returns no rows
```

So a single `NULL` in `Orders.customerId` makes the whole query return nothing. `NOT EXISTS` only asks "is there a row where `o.customerId = c.id`?"; rows with `NULL` never match and are simply ignored. (Positive `IN` / `EXISTS` don't have this problem, because a missed match and `UNKNOWN` are both filtered out the same way.)

| | `NOT IN (subquery)` | `NOT EXISTS (subquery)` |
|---|---|---|
| What it checks | Value is not equal to any value in the list | No row satisfies the correlated condition |
| `NULL` in subquery result | Returns **no rows** | Ignored, correct result |
| `NULL` in outer column (`id`) | Row excluded (unless subquery is empty) | Row kept (nothing can match `NULL`) |
| Optimizer | MySQL 8.0.17+ anti-join only when both columns are `NOT NULL`; PostgreSQL never anti-joins it (hashed subplan, very slow if it exceeds `work_mem`) | Anti-join (hash or merge) in modern MySQL and PostgreSQL |

**Recommendations**

- Default to `NOT EXISTS` for anti-joins; `LEFT JOIN ... IS NULL` usually gets the same plan.
- If you use `NOT IN`, make sure the subquery can't return `NULL` (`NOT NULL` column or `WHERE customerId IS NOT NULL`).
- Index the matched column (`Orders(customerId)`) so each existence check is an index lookup.

---

## 4. Stored Functions

A stored function is saved **in the database** and called like a built-in function from any SQL query or client. It persists until dropped. (A Python function, by contrast, lives in your app and sends queries to the database.)

```sql
DELIMITER $$   -- so the ; inside the body doesn't end the statement
CREATE FUNCTION getNthHighestSalary(N INT) RETURNS INT
BEGIN
    DECLARE m INT;
    SET m = N - 1;            -- MySQL LIMIT accepts constants/variables, not N-1
    RETURN (
        SELECT DISTINCT salary FROM Employee
        ORDER BY salary DESC
        LIMIT m, 1            -- skip m rows, return 1
    );
END$$
DELIMITER ;

SELECT getNthHighestSalary(2);
SHOW CREATE FUNCTION getNthHighestSalary;
DROP FUNCTION IF EXISTS getNthHighestSalary;
```

**`RETURN (subquery)` is a scalar subquery**, so 0 rows becomes `NULL` automatically and no `MIN()` is needed. The window-function version works the same way:

```sql
CREATE FUNCTION getNthHighestSalary(N INT) RETURNS INT
BEGIN
    RETURN (
        WITH cte AS (
            SELECT DISTINCT salary,
                   DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
            FROM Employee
        )
        SELECT salary FROM cte WHERE rnk = N
    );
END
```

`DISTINCT` keeps the subquery to one row per rank (each distinct salary has a unique dense rank). Consider guarding `N < 1`, which would otherwise produce a negative offset.

Use stored functions for logic reused across many queries or applications; keep simple or frequently changing logic in plain SQL or application code.

---

## Key Takeaways

1. Window functions and aliases are created in `SELECT`; filter on them in an outer query.
2. `FUNC()` is an aggregate (collapses rows); `FUNC() OVER (...)` is a window function (keeps rows).
3. Aggregates without `GROUP BY` always return one row, so no match gives `NULL`; plain `SELECT` gives zero rows.
4. Scalar subqueries return 1 column and at most 1 row; zero rows becomes `NULL`. This includes `SELECT (subquery)` and `RETURN (subquery)` in functions.
5. Correlated subqueries are fine for `EXISTS` and small or indexed cases; otherwise prefer joins or window functions, and check `EXPLAIN`.
6. For anti-joins use `NOT EXISTS`: one `NULL` in a `NOT IN` list makes the query return no rows, and `NOT IN` optimizes worse.
