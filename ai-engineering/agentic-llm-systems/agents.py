"""The agent loop, agents as tools, and the multi-agent BI system built from them.

    python agents.py --offline                       # replay the worked example (no API key)
    python agents.py "What was net revenue by region in October 2026?"   # real Claude

An agent here is: a system prompt, a set of tools, a model, and a loop that
lets the model call tools until it answers. A multi-agent system is several
such agents, where one agent's tools include the others.
"""

import json
import sys
from dataclasses import dataclass, field
from typing import Callable

from bi_warehouse import (DOCS, SQLRejected, build_warehouse, check_metric_sql,
                          describe_schema, run_readonly_sql)
from llm_client import ScriptedLLM
from rag import Retriever, format_context


class ToolError(Exception):
    """An expected tool failure. Its message goes back to the model as an error result."""


class MaxStepsExceeded(Exception):
    """The agent used all its steps without answering."""


@dataclass
class Tool:
    name: str
    description: str
    properties: dict
    fn: Callable[..., str]

    def spec(self) -> dict:
        """The tool definition sent to the model (Anthropic format, strict schema)."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.properties,
                "required": list(self.properties),
                "additionalProperties": False,
            },
            "strict": True,
        }


@dataclass
class TraceEvent:
    agent: str
    tool: str
    input: dict
    ok: bool
    output: str


@dataclass
class Trace:
    """Every tool call made by every agent, in order: the minimum you need to debug an agent."""

    events: list[TraceEvent] = field(default_factory=list)

    def summary(self) -> list[tuple[str, str, bool]]:
        return [(e.agent, e.tool, e.ok) for e in self.events]


class Agent:
    def __init__(self, name: str, system: str, llm, tools: list[Tool],
                 max_steps: int = 8, trace: Trace | None = None):
        self.name = name
        self.system = system
        self.llm = llm
        self.tools = {t.name: t for t in tools}
        self.max_steps = max_steps
        self.trace = trace if trace is not None else Trace()

    def run(self, task: str) -> str:
        """The agent loop: ask the model, run the tools it calls, repeat until it answers."""
        messages = [{"role": "user", "content": task}]
        specs = [t.spec() for t in self.tools.values()]
        for _ in range(self.max_steps):
            reply = self.llm.complete(self.system, messages, specs)
            messages.append({"role": "assistant", "content": reply.content})
            if not reply.tool_calls:
                return reply.text
            # All results of one turn go back in one user message, in call order.
            messages.append({"role": "user", "content": [self._call(c) for c in reply.tool_calls]})
        raise MaxStepsExceeded(f"{self.name} did not answer within {self.max_steps} steps")

    def _call(self, call) -> dict:
        tool = self.tools.get(call.name)
        try:
            if tool is None:
                raise ToolError(f"Unknown tool {call.name!r}. Available: {sorted(self.tools)}")
            output, ok = tool.fn(**call.input), True
        except ToolError as e:
            output, ok = str(e), False
        self.trace.events.append(TraceEvent(self.name, call.name, call.input, ok, output))
        result = {"type": "tool_result", "tool_use_id": call.id, "content": output}
        if not ok:
            result["is_error"] = True
        return result

    def as_tool(self, description: str) -> Tool:
        """Wrap this agent so another agent can call it like any other tool.

        The caller sees only the task it sent and the answer it got back; the
        sub-agent's own searching and retrying stays in the sub-agent's
        context. That isolation is the main reason to split work across agents.
        """
        def delegate(task: str) -> str:
            try:
                return self.run(task)
            except MaxStepsExceeded as e:
                raise ToolError(str(e)) from e

        return Tool(f"ask_{self.name}", description,
                    {"task": {"type": "string", "description": "What you need, with all context it requires."}},
                    delegate)


# --------------------------------------------------------------------------
# The agentic BI system
# --------------------------------------------------------------------------

ORCHESTRATOR_PROMPT = """You answer business questions about the company's data for non-technical users.
You do not write SQL or read documentation yourself. You have two specialists:
- ask_catalog_agent finds metric definitions, table descriptions and verified queries.
- ask_sql_agent writes, checks and runs SQL against the warehouse.
For a data question: first ask the catalog agent what the metric means and which tables hold it,
then give the SQL agent a self-contained task that includes that definition, the exact date range and the grouping.
Each specialist sees only the task you send it, not this conversation.
If the question is ambiguous (which metric, which period), ask the user instead of guessing.
In the final answer, give the numbers with units, state the definition you used, and cite document ids in brackets."""

CATALOG_PROMPT = """You find the business definitions and tables needed to answer a data question.
Search the documentation with search_docs; search more than once if the first results do not contain
the metric definition and the tables. Reply with a short brief: the metric definition (quoted from the docs),
the tables and join keys, any verified query, and the document ids you used. Do not invent definitions:
if the docs do not define the metric, say so."""

SQL_PROMPT_TEMPLATE = """You write SQLite queries against the company warehouse and run them.
Schema:
{schema}

Before running a query for a known metric, check it with check_metric_sql and fix every problem it reports.
If run_sql returns an error, read it, fix the query and try again.
Reply with the result table and the final SQL you ran."""


def build_bi_system(llms: dict, conn=None, retriever: Retriever | None = None,
                    trace: Trace | None = None) -> tuple[Agent, Trace]:
    """Wire the three agents together. `llms` maps agent name to a model client."""
    conn = conn if conn is not None else build_warehouse()
    if retriever is None:
        retriever = Retriever()
        retriever.ingest(DOCS)
    trace = trace if trace is not None else Trace()

    def search_docs(query: str, kind: str) -> str:
        chunks = retriever.search(query, k=3, kind=None if kind == "any" else kind)
        return format_context(chunks) if chunks else "No matching documents."

    def run_sql(sql: str) -> str:
        try:
            return json.dumps(run_readonly_sql(conn, sql))
        except SQLRejected as e:
            raise ToolError(str(e)) from e

    def check_sql(sql: str, metric_id: str) -> str:
        try:
            problems = check_metric_sql(sql, metric_id)
        except KeyError as e:
            raise ToolError(str(e)) from e
        return "OK: no problems found." if not problems else "Problems:\n- " + "\n- ".join(problems)

    catalog = Agent("catalog_agent", CATALOG_PROMPT, llms["catalog_agent"], [
        Tool("search_docs", "Search metric definitions, table docs and verified queries. Returns the top 3 passages with their ids.",
             {"query": {"type": "string"},
              "kind": {"type": "string", "enum": ["metric", "table", "golden_query", "any"]}},
             search_docs),
    ], trace=trace)

    sql_agent = Agent("sql_agent", SQL_PROMPT_TEMPLATE.format(schema=describe_schema(conn)),
                      llms["sql_agent"], [
        Tool("run_sql", "Run one read-only SELECT query. Returns JSON with columns, rows (max 100) and truncated.",
             {"sql": {"type": "string"}}, run_sql),
        Tool("check_metric_sql", "Check a query against the rules of a metric definition before running it.",
             {"sql": {"type": "string"},
              "metric_id": {"type": "string", "enum": ["metric_revenue", "metric_active_customers"]}},
             check_sql),
    ], trace=trace)

    orchestrator = Agent("orchestrator", ORCHESTRATOR_PROMPT, llms["orchestrator"], [
        catalog.as_tool("Ask the data-catalog specialist for metric definitions, tables and verified queries."),
        sql_agent.as_tool("Ask the SQL specialist to compute a result from the warehouse. Include the metric definition."),
    ], trace=trace)
    return orchestrator, trace


# --------------------------------------------------------------------------
# The worked example of Chapter 4, as a script the offline demo and tests replay
# --------------------------------------------------------------------------

QUESTION = "What was net revenue by region in October 2026?"

BAD_COLUMN_SQL = ("SELECT c.region, SUM(o.amount_usd) FROM orders o "
                  "JOIN customers c ON c.customer_id = o.customer_id GROUP BY c.region")

NAIVE_SQL = ("SELECT c.region, SUM(o.amount) AS revenue FROM orders o "
             "JOIN customers c ON c.customer_id = o.customer_id "
             "WHERE o.order_date BETWEEN '2026-10-01' AND '2026-10-31' "
             "GROUP BY c.region ORDER BY revenue DESC")

GOOD_SQL = ("SELECT c.region, ROUND(SUM(o.amount * f.usd_rate), 2) AS revenue_usd FROM orders o "
            "JOIN customers c ON c.customer_id = o.customer_id "
            "JOIN fx_rates f ON f.currency = o.currency "
            "WHERE o.status = 'completed' AND o.order_date BETWEEN '2026-10-01' AND '2026-10-31' "
            "GROUP BY c.region ORDER BY revenue_usd DESC")

FINAL_ANSWER = ("Net revenue in October 2026, in USD: EU 231.00, NA 160.00, APAC 100.00 (total 491.00). "
                "Net revenue counts completed orders only, converted to USD at fx_rates; "
                "refunded and cancelled orders are excluded [metric_revenue, golden_revenue_by_region].")


def scripted_llms() -> dict:
    """What a model might do on QUESTION, including two mistakes it recovers from."""
    return {
        "orchestrator": ScriptedLLM([
            [("ask_catalog_agent", {"task": "How is net revenue defined, and which tables and columns "
                                            "are needed to compute it by customer region?"})],
            [("ask_sql_agent", {"task": "Compute net revenue by customer region for 2026-10-01 to 2026-10-31. "
                                        "Definition (metric_revenue): sum of orders.amount * fx_rates.usd_rate "
                                        "over orders with status = 'completed'. Join customers on customer_id "
                                        "and fx_rates on currency."})],
            FINAL_ANSWER,
        ]),
        "catalog_agent": ScriptedLLM([
            [("search_docs", {"query": "net revenue definition", "kind": "metric"}),
             ("search_docs", {"query": "revenue by region", "kind": "golden_query"})],
            "Net revenue (metric_revenue): sum of orders.amount * fx_rates.usd_rate over orders with "
            "status = 'completed'. Tables: orders, customers (region), fx_rates. "
            "Verified query: golden_revenue_by_region.",
        ]),
        "sql_agent": ScriptedLLM([
            [("run_sql", {"sql": BAD_COLUMN_SQL})],                       # mistake 1: invented column
            [("check_metric_sql", {"sql": NAIVE_SQL, "metric_id": "metric_revenue"})],  # mistake 2: wrong metric
            [("check_metric_sql", {"sql": GOOD_SQL, "metric_id": "metric_revenue"}),
             ("run_sql", {"sql": GOOD_SQL})],
            "region | revenue_usd\nEU | 231.0\nNA | 160.0\nAPAC | 100.0\n\nSQL: " + GOOD_SQL,
        ]),
    }


def main(argv: list[str]) -> None:
    if argv[1:] == ["--offline"]:
        llms, question = scripted_llms(), QUESTION
    elif len(argv) == 2:
        from llm_client import ClaudeLLM
        llms, question = {name: ClaudeLLM() for name in ("orchestrator", "catalog_agent", "sql_agent")}, argv[1]
    else:
        sys.exit(__doc__)
    orchestrator, trace = build_bi_system(llms)
    answer = orchestrator.run(question)
    for e in trace.events:
        print(f"[{e.agent}] {e.tool}({json.dumps(e.input)[:90]}) -> {'ok' if e.ok else 'ERROR'}")
    print("\n" + answer)


if __name__ == "__main__":
    main(sys.argv)
