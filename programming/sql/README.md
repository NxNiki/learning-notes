# SQL Learning Notes

## Overview

This folder contains all SQL learning materials:

- **Course Notes** - Mosh SQL course topics (`topic_*.sql` files)
  - Course: https://codewithmosh.com/courses
- **Practice Problems** - [LeetCode SQL problems](./leetcode/) with solutions and notes
- **Concepts & Reference** - SQL evaluation order, window functions, aliases, NULL handling (below)

---

## SQL Query Evaluation Order & Key Concepts

### SQL Logical Processing Order

Understanding the order in which SQL processes a query is crucial for knowing where you can use window functions, aliases, and why certain results behave the way they do:

```
1. FROM         ← Tables and joins
2. WHERE        ← Filter individual rows
3. GROUP BY     ← Group rows for aggregation
4. HAVING       ← Filter groups
5. SELECT       ← Compute expressions, window functions, create aliases
6. DISTINCT     ← Remove duplicate rows
7. ORDER BY     ← Sort results
8. LIMIT/OFFSET ← Limit number of rows returned
```

---

### Window Functions

**Window functions can ONLY be used in:**
- ✅ `SELECT` clause
- ✅ `ORDER BY` clause

**Window functions CANNOT be used in:**
- ❌ `WHERE` clause
- ❌ `HAVING` clause
- ❌ `GROUP BY` clause

**Why?** Window functions are evaluated during the SELECT phase (step 5), so they don't exist yet when WHERE, GROUP BY, or HAVING are processed.

**Example - This DOES NOT work:**
```sql
-- ❌ ERROR: Window functions cannot be used in WHERE or HAVING
SELECT salary
FROM Employee
WHERE DENSE_RANK() OVER (ORDER BY salary DESC) = 2
```

**Correct approach - Use CTE or subquery:**
```sql
-- ✅ Compute window function first, then filter
WITH ranked AS (
    SELECT salary, 
           DENSE_RANK() OVER (ORDER BY salary DESC) AS rank
    FROM Employee
)
SELECT salary
FROM ranked
WHERE rank = 2
```

---

### Column Aliases

**Aliases are created during SELECT (step 5), so they only exist in later steps:**

#### ✅ CAN use aliases in:
- **ORDER BY** - Always works (evaluated after SELECT)
```sql
SELECT salary * 12 AS annual_salary
FROM Employee
ORDER BY annual_salary DESC  -- ✅ Works!
```

#### ❌ CANNOT use aliases in:
- **WHERE** - Evaluated before SELECT
```sql
-- ❌ ERROR: Unknown column 'annual_salary'
SELECT salary * 12 AS annual_salary
FROM Employee
WHERE annual_salary > 100000
```

- **Same SELECT clause** - Can't reference alias being defined
```sql
-- ❌ ERROR: Unknown column 'annual_salary'
SELECT 
    salary * 12 AS annual_salary,
    annual_salary * 0.1 AS bonus  -- Can't use alias here!
FROM Employee
```

- **GROUP BY / HAVING** - Usually not allowed (standard SQL)
```sql
-- ❌ Standard SQL doesn't allow this (some databases extend this)
SELECT AVG(salary) AS avg_sal
FROM Employee
GROUP BY department
HAVING avg_sal > 50000
```

**Workaround:** Use subqueries or CTEs
```sql
-- ✅ Compute alias first, then filter
SELECT *
FROM (
    SELECT salary * 12 AS annual_salary
    FROM Employee
) subquery
WHERE annual_salary > 100000
```

---

### When NULL is Created in SQL Results

Understanding when you get NULL vs empty result set is important for query design:

#### Aggregate Functions → Always return 1 row (NULL if no data)

**Aggregate functions** (`MIN`, `MAX`, `AVG`, `SUM`, `COUNT`) without `GROUP BY`:
- Always return **exactly 1 row**
- Return **NULL** if no rows match (except `COUNT` returns 0)

```sql
-- Returns 1 row with NULL if no second highest exists
WITH cte AS (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rank
    FROM Employee
)
SELECT MIN(salary) AS SecondHighestSalary
FROM cte
WHERE rank = 2  -- If no match: returns 1 row → NULL
```

**Result when no match:**
```
SecondHighestSalary
-------------------
NULL
```

#### Non-Aggregate Queries → Return 0 rows (empty result)

**Non-aggregate queries** (`SELECT`, `SELECT DISTINCT`):
- Return **as many rows as match**
- Return **0 rows** (empty result set) if nothing matches

```sql
-- Returns 0 rows if no second highest exists
SELECT DISTINCT salary
FROM Employee
ORDER BY salary DESC
LIMIT 1 OFFSET 1  -- If not enough rows: returns 0 rows (empty)
```

**Result when no match:**
```
(empty result set - 0 rows)
```

#### Scalar Subqueries → Convert 0 rows to NULL

**Scalar subqueries** (subquery in SELECT clause):
- Must return at most 1 row, 1 column
- If returns **0 rows** → converted to **NULL**
- If returns **1 row** → uses that value
- If returns **multiple rows** → ERROR

```sql
-- The outer query always returns 1 row
SELECT (
    -- Inner query returns 0 rows if no second highest
    SELECT DISTINCT salary
    FROM Employee
    ORDER BY salary DESC
    LIMIT 1 OFFSET 1
) AS SecondHighestSalary
-- 0 rows from inner query → converted to NULL → outer returns 1 row with NULL
```

**How it works:**
1. Inner query executes → 0 rows (if no second highest)
2. SQL converts 0 rows → NULL
3. Outer query returns 1 row with NULL

**Result when no match:**
```
SecondHighestSalary
-------------------
NULL
```

---

### Summary Table

| Query Type | No Matching Rows | Result |
|------------|------------------|---------|
| Aggregate (`MIN`, `MAX`, etc.) | NULL | 1 row with NULL |
| Non-aggregate (`SELECT`, `SELECT DISTINCT`) | Empty | 0 rows |
| Scalar subquery in SELECT | NULL | 1 row with NULL |
| `COUNT(*)` with no matches | 0 | 1 row with 0 |

---

### Scalar Subqueries

A **scalar subquery** is a subquery that returns **exactly 1 column and at most 1 row** - essentially a single value.

#### Definition and Rules

**Must satisfy both:**
- ✅ Exactly **1 column** (not multiple)
- ✅ At most **1 row** (0 or 1 row)

```sql
-- ✅ Valid: 1 column, 1 row
SELECT (SELECT MAX(salary) FROM Employee) AS max_salary

-- ✅ Valid: 1 column, 0 rows → NULL
SELECT (SELECT salary FROM Employee WHERE id = 999) AS result

-- ❌ ERROR: Multiple columns
SELECT (SELECT name, salary FROM Employee LIMIT 1)
-- Error: Operand should contain 1 column(s)

-- ❌ ERROR: Multiple rows
SELECT (SELECT salary FROM Employee)
-- Error: Subquery returns more than 1 row
```

#### Where Scalar Subqueries Can Be Used

Scalar subqueries can appear **almost anywhere a single value can**:

**✅ SELECT clause** (most common)
```sql
SELECT 
    name,
    salary,
    (SELECT AVG(salary) FROM Employee) AS company_avg
FROM Employee
```

**✅ WHERE clause**
```sql
SELECT name, salary
FROM Employee
WHERE salary > (SELECT AVG(salary) FROM Employee)
```

**✅ HAVING clause**
```sql
SELECT department, AVG(salary) AS avg_sal
FROM Employee
GROUP BY department
HAVING AVG(salary) > (SELECT AVG(salary) FROM Employee)
```

**✅ ORDER BY clause**
```sql
SELECT name, salary
FROM Employee
ORDER BY salary - (SELECT AVG(salary) FROM Employee) DESC
```

**✅ In expressions**
```sql
SELECT 
    name,
    salary,
    salary * 100.0 / (SELECT SUM(salary) FROM Employee) AS pct_of_total
FROM Employee
```

#### Correlated vs Non-Correlated

**Non-correlated** (executes once):
```sql
SELECT 
    name,
    (SELECT AVG(salary) FROM Employee) AS avg  -- Runs once
FROM Employee
```

**Correlated** (executes once per row):
```sql
SELECT 
    e.name,
    (SELECT AVG(salary) 
     FROM Employee e2 
     WHERE e2.dept_id = e.dept_id) AS dept_avg  -- Runs per row
FROM Employee e
```

#### Common Use Cases

**1. Finding Nth highest**
```sql
-- Second highest salary (returns NULL if doesn't exist)
SELECT (
    SELECT DISTINCT salary
    FROM Employee
    ORDER BY salary DESC
    LIMIT 1 OFFSET 1
) AS SecondHighestSalary
```

**2. Comparing to aggregates**
```sql
-- Employees earning more than average
SELECT name, salary
FROM Employee
WHERE salary > (SELECT AVG(salary) FROM Employee)
```

**3. Adding computed columns**
```sql
SELECT 
    name,
    salary,
    salary - (SELECT AVG(salary) FROM Employee) AS diff_from_avg
FROM Employee
```

#### Scalar Subquery vs Other Subquery Types

| Type | Columns | Rows | Example Use |
|------|---------|------|-------------|
| **Scalar Subquery** | Exactly 1 | 0 or 1 | `(SELECT MAX(salary) FROM Employee)` |
| **Derived Table** | Any | Any | `FROM (SELECT * FROM Employee) sub` |
| **IN Subquery** | 1 | Any | `WHERE id IN (SELECT id FROM Employee)` |

#### Important: Multiple Columns Needs Derived Table

```sql
-- ❌ Cannot use scalar subquery for multiple columns
SELECT (SELECT name, salary FROM Employee LIMIT 1)

-- ✅ Use derived table in FROM clause instead
SELECT sub.name, sub.salary
FROM (
    SELECT name, salary 
    FROM Employee
    WHERE department = 'IT'
) sub

-- ✅ Or use multiple scalar subqueries
SELECT 
    (SELECT MAX(salary) FROM Employee) AS max_sal,
    (SELECT MIN(salary) FROM Employee) AS min_sal
```

---

### Stored Functions and RETURN Scalar Subqueries

#### What is a Stored Function?

A **stored function** is saved in the database and can be reused across queries, similar to defining a function in programming.

```sql
-- Create function (saved in database)
DELIMITER $$
CREATE FUNCTION getNthHighestSalary(N INT) RETURNS INT
BEGIN
    DECLARE m INT;
    SET m = N - 1;
    RETURN (
        SELECT DISTINCT salary
        FROM Employee
        ORDER BY salary DESC
        LIMIT m, 1
    );
END$$
DELIMITER ;

-- Use it multiple times
SELECT getNthHighestSalary(2);  -- 2nd highest
SELECT getNthHighestSalary(5);  -- 5th highest
```

#### RETURN Creates Scalar Subquery Context

**Key insight:** `RETURN (subquery)` automatically wraps the query as a **scalar subquery**, giving you NULL conversion for free!

```sql
CREATE FUNCTION getNthHighestSalary(N INT) RETURNS INT
BEGIN
    RETURN (
        -- This entire query is a SCALAR SUBQUERY
        WITH cte AS (
            SELECT DISTINCT 
                salary,
                DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
            FROM Employee
        )
        SELECT salary  -- No MIN() needed!
        FROM cte
        WHERE rnk = N
        -- If no match: 0 rows → NULL automatically
    );
END
```

**Why no MIN() needed:**
- `RETURN (...)` creates scalar subquery context
- If query returns 0 rows → automatically converts to NULL
- Same behavior as `SELECT (subquery)` in standalone queries

#### Comparison: Standalone Query vs Function

**Standalone query (needs MIN or scalar subquery wrapper):**

```sql
-- ❌ Without aggregate: Returns 0 rows (empty result)
WITH cte AS (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM Employee
)
SELECT salary
FROM cte
WHERE rnk = 2  -- If no match: returns 0 rows

-- ✅ With MIN: Returns 1 row with NULL
WITH cte AS (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM Employee
)
SELECT MIN(salary) AS SecondHighestSalary
FROM cte
WHERE rnk = 2  -- If no match: returns NULL

-- ✅ With scalar subquery wrapper: Returns 1 row with NULL
SELECT (
    WITH cte AS (
        SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
        FROM Employee
    )
    SELECT salary
    FROM cte
    WHERE rnk = 2
) AS SecondHighestSalary  -- If no match: returns NULL
```

**Function RETURN (no MIN needed):**

```sql
-- ✅ RETURN automatically handles it
CREATE FUNCTION getNthHighestSalary(N INT) RETURNS INT
BEGIN
    RETURN (
        -- Scalar subquery context - no MIN() needed
        WITH cte AS (
            SELECT DISTINCT salary,
                   DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
            FROM Employee
        )
        SELECT salary
        FROM cte
        WHERE rnk = N  -- If no match: returns NULL automatically
    );
END
```

#### Three Ways to Get NULL When No Match

| Method | Context | Syntax |
|--------|---------|--------|
| **Aggregate Function** | Standalone query | `SELECT MIN(salary) FROM ... WHERE ...` |
| **Scalar Subquery** | Standalone query | `SELECT (SELECT salary FROM ... WHERE ...)` |
| **Function RETURN** | Stored function | `RETURN (SELECT salary FROM ... WHERE ...)` |

**All three convert 0 rows → NULL when no match!**

#### How to Create and Use Functions

**1. Create the function (one time):**
```sql
DELIMITER $$
CREATE FUNCTION getNthHighestSalary(N INT) RETURNS INT
BEGIN
    RETURN (
        SELECT DISTINCT salary
        FROM Employee
        ORDER BY salary DESC
        LIMIT N-1, 1
    );
END$$
DELIMITER ;
```

**2. Call the function (many times):**
```sql
-- Direct call
SELECT getNthHighestSalary(2);

-- In WHERE clause
SELECT name, salary
FROM Employee
WHERE salary = getNthHighestSalary(1);

-- In expressions
SELECT 
    name,
    salary,
    salary - getNthHighestSalary(1) AS diff_from_highest
FROM Employee;
```

**3. View existing functions:**
```sql
SHOW FUNCTION STATUS WHERE Db = 'your_database';
SHOW CREATE FUNCTION getNthHighestSalary;
```

**4. Drop function when done:**
```sql
DROP FUNCTION IF EXISTS getNthHighestSalary;
```

#### Stored Functions vs Python Functions

| Aspect | MySQL Stored Function | Python Function |
|--------|----------------------|-----------------|
| **Stored in** | Database server | .py file on disk |
| **Runs on** | Database server | Your computer/app server |
| **Accessible by** | Anyone with DB access | Only your Python app |
| **Persists** | Until DROP FUNCTION | While file exists |
| **Can call from** | Any SQL query, any client | Only from Python code |
| **Network overhead** | No extra round-trips | Query sent over network |

#### MySQL LIMIT Restriction

**Why use a variable for LIMIT?**

```sql
-- ❌ MySQL doesn't allow expressions in LIMIT
LIMIT N-1, 1  -- ERROR: Can't use expression

-- ✅ Must use variable
DECLARE m INT;
SET m = N - 1;
LIMIT m, 1  -- Works with variable
```

MySQL's LIMIT clause requires a constant or variable, not an expression.

#### When to Use Stored Functions

**✅ Good use cases:**
- Complex calculations reused across queries
- Finding Nth highest/lowest values
- Encapsulating business logic (tax rates, bonuses)
- Functions needed by multiple applications

**❌ When to avoid:**
- Simple operations (just use regular SQL)
- Frequently changing logic (harder to update than app code)
- Heavy processing (can slow down database)

---

### Key Takeaways

1. **Window functions** are evaluated during SELECT → use CTE/subquery to filter on them
2. **Aliases** are created during SELECT → can only use in ORDER BY (and LIMIT)
3. **Aggregate functions** always return 1 row → NULL if no data
4. **Scalar subqueries** must return exactly 1 column and at most 1 row → 0 rows converts to NULL
5. **Non-aggregate queries** can return 0 rows → empty result set
6. **RETURN (subquery) in functions** creates scalar subquery context → automatic NULL conversion

---
