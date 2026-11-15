# SQL Learning Notes

Notes for the Mosh course for SQL:
https://codewithmosh.com/courses

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

### Key Takeaways

1. **Window functions** are evaluated during SELECT → use CTE/subquery to filter on them
2. **Aliases** are created during SELECT → can only use in ORDER BY (and LIMIT)
3. **Aggregate functions** always return 1 row → NULL if no data
4. **Scalar subqueries** convert empty results → NULL
5. **Non-aggregate queries** can return 0 rows → empty result set

---
