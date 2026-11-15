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

### Key Takeaways

1. **Window functions** are evaluated during SELECT → use CTE/subquery to filter on them
2. **Aliases** are created during SELECT → can only use in ORDER BY (and LIMIT)
3. **Aggregate functions** always return 1 row → NULL if no data
4. **Scalar subqueries** must return exactly 1 column and at most 1 row → 0 rows converts to NULL
5. **Non-aggregate queries** can return 0 rows → empty result set

---
