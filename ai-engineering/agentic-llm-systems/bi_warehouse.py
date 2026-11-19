"""A toy data warehouse for the agentic BI example, with a guarded SQL runner.

The warehouse is an in-memory SQLite database standing in for Redshift. The
documents in DOCS are the knowledge base the agents search: metric definitions,
table descriptions and verified ("golden") queries, the same material a semantic
layer or data catalog holds in a real company.
"""

import json
import re
import sqlite3

SCHEMA = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    region      TEXT NOT NULL,          -- NA, EU, APAC
    signup_date TEXT NOT NULL
);
CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date  TEXT NOT NULL,          -- ISO date
    amount      REAL NOT NULL,          -- in the order's own currency
    currency    TEXT NOT NULL,          -- USD, EUR, GBP
    status      TEXT NOT NULL           -- completed, refunded, cancelled
);
CREATE TABLE fx_rates (
    currency TEXT PRIMARY KEY,
    usd_rate REAL NOT NULL              -- 1 unit of currency = usd_rate USD
);
"""

CUSTOMERS = [
    (1, "Acme", "NA", "2025-01-10"),
    (2, "Globex", "EU", "2025-03-02"),
    (3, "Initech", "EU", "2025-06-15"),
    (4, "Umbrella", "APAC", "2026-02-20"),
    (5, "Hooli", "NA", "2026-07-01"),
]

ORDERS = [
    (1, 1, "2026-10-03", 100.00, "USD", "completed"),
    (2, 2, "2026-10-05", 200.00, "EUR", "completed"),
    (3, 3, "2026-10-09", 50.00, "EUR", "refunded"),
    (4, 4, "2026-10-12", 80.00, "GBP", "completed"),
    (5, 5, "2026-10-15", 40.00, "USD", "cancelled"),
    (6, 1, "2026-10-20", 60.00, "USD", "completed"),
    (7, 2, "2026-10-28", 10.00, "EUR", "completed"),
    (8, 3, "2026-09-30", 300.00, "EUR", "completed"),
    (9, 5, "2026-11-02", 70.00, "USD", "completed"),
]

FX_RATES = [("USD", 1.00), ("EUR", 1.10), ("GBP", 1.25)]

# The knowledge base. Each document has an id, a kind (used as a metadata
# filter) and its text. Aliases are written into the metric documents on
# purpose: retrieval matches words, so "sales" only finds the revenue
# definition if the word "sales" appears in it (Section 5.3 of the guide).
DOCS = [
    {
        "id": "metric_revenue",
        "kind": "metric",
        "text": (
            "Metric: net revenue. Aliases: sales, net sales, turnover. "
            "Net revenue is the sum of order amount converted to USD "
            "(orders.amount * fx_rates.usd_rate) over orders with status = 'completed'. "
            "Refunded and cancelled orders are excluded. Always join fx_rates on currency; "
            "never sum amount across currencies."
        ),
    },
    {
        "id": "metric_active_customers",
        "kind": "metric",
        "text": (
            "Metric: active customers. Aliases: buyers, purchasing customers. "
            "The number of distinct customers with at least one order with status = 'completed' "
            "in the period."
        ),
    },
    {
        "id": "metric_aov",
        "kind": "metric",
        "text": (
            "Metric: average order value (AOV). Aliases: basket size, average ticket. "
            "Net revenue in USD divided by the number of completed orders in the period."
        ),
    },
    {
        "id": "metric_refund_rate",
        "kind": "metric",
        "text": (
            "Metric: refund rate. Aliases: return rate. "
            "Refunded orders divided by completed plus refunded orders in the period. "
            "Cancelled orders never shipped and are excluded."
        ),
    },
    {
        "id": "table_orders",
        "kind": "table",
        "text": (
            "Table orders: one row per order. Columns: order_id, customer_id, order_date (ISO date), "
            "amount (in the order's own currency, not USD), currency (USD, EUR, GBP), "
            "status (completed, refunded, cancelled). Join customers on customer_id "
            "and fx_rates on currency."
        ),
    },
    {
        "id": "table_customers",
        "kind": "table",
        "text": (
            "Table customers: one row per customer. Columns: customer_id, name, "
            "region (NA, EU, APAC), signup_date."
        ),
    },
    {
        "id": "table_fx_rates",
        "kind": "table",
        "text": (
            "Table fx_rates: exchange rates to USD. Columns: currency, usd_rate. "
            "Multiply an amount by usd_rate to convert it to USD."
        ),
    },
    {
        "id": "golden_revenue_by_region",
        "kind": "golden_query",
        "text": (
            "Verified query: net revenue by region for a month. "
            "SELECT c.region, ROUND(SUM(o.amount * f.usd_rate), 2) AS revenue_usd "
            "FROM orders o JOIN customers c ON c.customer_id = o.customer_id "
            "JOIN fx_rates f ON f.currency = o.currency "
            "WHERE o.status = 'completed' AND o.order_date BETWEEN '2026-10-01' AND '2026-10-31' "
            "GROUP BY c.region ORDER BY revenue_usd DESC"
        ),
    },
]


class SQLRejected(Exception):
    """The query was refused by a guardrail or failed in the database.

    The message is written for the model: the agent loop sends it back as an
    error tool result so the model can correct its query.
    """


def build_warehouse() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", CUSTOMERS)
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", ORDERS)
    conn.executemany("INSERT INTO fx_rates VALUES (?, ?)", FX_RATES)
    conn.commit()
    return conn


def describe_schema(conn: sqlite3.Connection) -> str:
    """Table and column names, as compact text for a prompt."""
    lines = []
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
    for (table,) in tables.fetchall():
        cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
        lines.append(f"{table}({', '.join(f'{c[1]} {c[2]}' for c in cols)})")
    return "\n".join(lines)


_READ_ACTIONS = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION,
                 sqlite3.SQLITE_RECURSIVE}
_FIRST_WORD = re.compile(r"^\s*(\w+)", re.IGNORECASE)


def _read_only(action, *_):
    return sqlite3.SQLITE_OK if action in _READ_ACTIONS else sqlite3.SQLITE_DENY


def run_readonly_sql(conn: sqlite3.Connection, sql: str, max_rows: int = 100,
                     max_steps: int = 1_000_000) -> dict:
    """Run one read-only query and return {"columns", "rows", "truncated"}.

    Three guardrails, from weakest to strongest:
    1. a text check: one statement, starting with SELECT or WITH;
    2. a row cap, so a careless query cannot flood the model's context;
    3. the database itself refuses anything but reads (an authorizer, the
       SQLite version of a read-only Redshift user) and aborts long queries
       (a progress handler, the version of statement_timeout).
    The text check only gives the model a clearer error message; the
    authorizer is what actually stops a write.
    """
    statement = sql.strip().rstrip(";")
    if ";" in statement:
        raise SQLRejected("Only one statement is allowed.")
    first = _FIRST_WORD.match(statement)
    if not first or first.group(1).upper() not in {"SELECT", "WITH"}:
        raise SQLRejected("Only SELECT queries are allowed.")

    steps = 0

    def too_long():
        nonlocal steps
        steps += 1
        return steps > max_steps // 1000   # the handler runs every 1000 VM steps

    conn.set_authorizer(_read_only)
    conn.set_progress_handler(too_long, 1000)
    try:
        cursor = conn.execute(statement)
        rows = cursor.fetchmany(max_rows + 1)
    except sqlite3.DatabaseError as e:
        raise SQLRejected(f"Database error: {e}") from e
    finally:
        conn.set_authorizer(None)
        conn.set_progress_handler(None, 0)

    return {
        "columns": [d[0] for d in cursor.description],
        "rows": [list(r) for r in rows[:max_rows]],
        "truncated": len(rows) > max_rows,
    }


def check_metric_sql(sql: str, metric_id: str) -> list[str]:
    """Check a query against the rules of a metric definition.

    This is the deterministic half of the verifier: rules that can be checked
    by reading the SQL text. It catches the classic BI mistakes (summing
    across currencies, counting refunds as revenue) before a wrong number
    reaches a person. Returns a list of problems; empty means it passed.
    """
    s = re.sub(r"\s+", " ", sql.lower())
    rules = {
        "metric_revenue": [
            ("usd_rate" in s, "Revenue must convert amounts with fx_rates.usd_rate."),
            ("status = 'completed'" in s or 'status = "completed"' in s,
             "Revenue must only count orders with status = 'completed'."),
        ],
        "metric_active_customers": [
            ("distinct" in s, "Active customers must count DISTINCT customer_id."),
            ("status = 'completed'" in s, "Only completed orders make a customer active."),
        ],
    }
    if metric_id not in rules:
        raise KeyError(f"No rules for metric {metric_id!r}; known: {sorted(rules)}")
    return [message for ok, message in rules[metric_id] if not ok]


def same_result(conn: sqlite3.Connection, sql_a: str, sql_b: str) -> bool:
    """Execution accuracy: do two queries return the same rows, ignoring order?

    This is how text-to-SQL benchmarks such as Spider and BIRD grade a model:
    two differently written queries are both right if they return the same
    result.
    """
    a = run_readonly_sql(conn, sql_a, max_rows=10_000)
    b = run_readonly_sql(conn, sql_b, max_rows=10_000)

    def key(rows):
        return sorted(json.dumps(r) for r in rows)

    return key(a["rows"]) == key(b["rows"])
