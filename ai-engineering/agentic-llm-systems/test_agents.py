"""Checks the agent chapters (2-4, 7) of README.md: guardrails, the agent loop, the multi-agent worked example."""

import json
from types import SimpleNamespace

import pytest

from agents import (BAD_COLUMN_SQL, FINAL_ANSWER, GOOD_SQL, NAIVE_SQL, QUESTION, Agent,
                    MaxStepsExceeded, Tool, build_bi_system, scripted_llms)
from bi_warehouse import (SQLRejected, build_warehouse, check_metric_sql, run_readonly_sql,
                          same_result, DOCS)
from llm_client import ClaudeLLM, LLMError, ScriptedLLM


@pytest.fixture
def conn():
    return build_warehouse()


# --- the warehouse and its guardrails (Chapter 4.3) ---

def test_correct_and_naive_revenue(conn):
    assert run_readonly_sql(conn, GOOD_SQL)["rows"] == [["EU", 231.0], ["NA", 160.0], ["APAC", 100.0]]
    assert run_readonly_sql(conn, NAIVE_SQL)["rows"] == [["EU", 260.0], ["NA", 200.0], ["APAC", 80.0]]


def test_metric_check(conn):
    assert check_metric_sql(NAIVE_SQL, "metric_revenue") == [
        "Revenue must convert amounts with fx_rates.usd_rate.",
        "Revenue must only count orders with status = 'completed'.",
    ]
    assert check_metric_sql(GOOD_SQL, "metric_revenue") == []


@pytest.mark.parametrize("sql, message", [
    ("DROP TABLE orders", "Only SELECT queries are allowed."),
    ("SELECT 1; DELETE FROM orders", "Only one statement is allowed."),
    ("WITH x AS (SELECT 1) DELETE FROM orders", "Database error: not authorized"),
    ("WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n) SELECT count(*) FROM n",
     "Database error: interrupted"),
    (BAD_COLUMN_SQL, "Database error: no such column: o.amount_usd"),
])
def test_guardrails(conn, sql, message):
    with pytest.raises(SQLRejected, match=message):
        run_readonly_sql(conn, sql)
    assert conn.execute("SELECT count(*) FROM orders").fetchone() == (9,)


def test_row_cap(conn):
    out = run_readonly_sql(conn, "SELECT order_id FROM orders ORDER BY order_id", max_rows=3)
    assert out == {"columns": ["order_id"], "rows": [[1], [2], [3]], "truncated": True}


def test_execution_accuracy(conn):              # Chapter 7
    golden = next(d["text"] for d in DOCS if d["id"] == "golden_revenue_by_region")
    golden_sql = golden[golden.index("SELECT"):]
    assert same_result(conn, GOOD_SQL, golden_sql)
    assert not same_result(conn, NAIVE_SQL, golden_sql)


# --- the agent loop (Chapter 2) ---

def echo_tool():
    return Tool("echo", "Echo text back.", {"text": {"type": "string"}}, lambda text: text.upper())


def test_loop_runs_tools_until_answer():
    llm = ScriptedLLM([[("echo", {"text": "hi"})], "done"])
    agent = Agent("a", "system", llm, [echo_tool()])
    assert agent.run("say hi") == "done"
    result = llm.requests[1]["messages"][-1]["content"][0]
    assert result == {"type": "tool_result", "tool_use_id": "toolu_001", "content": "HI"}
    assert agent.tools["echo"].spec()["input_schema"]["additionalProperties"] is False


def test_unknown_tool_is_an_error_result_not_a_crash():
    llm = ScriptedLLM([[("delete_everything", {})], "sorry"])
    agent = Agent("a", "system", llm, [echo_tool()])
    assert agent.run("x") == "sorry"
    result = llm.requests[1]["messages"][-1]["content"][0]
    assert result["is_error"] is True and "Unknown tool" in result["content"]


def test_step_limit():
    llm = ScriptedLLM([[("echo", {"text": "again"})]] * 3)
    with pytest.raises(MaxStepsExceeded):
        Agent("a", "system", llm, [echo_tool()], max_steps=3).run("loop forever")


def test_sub_agent_giving_up_becomes_tool_error():
    inner = Agent("inner", "s", ScriptedLLM([[("echo", {"text": "x"})]] * 2), [echo_tool()], max_steps=2)
    outer_llm = ScriptedLLM([[("ask_inner", {"task": "t"})], "inner failed, telling the user"])
    outer = Agent("outer", "s", outer_llm, [inner.as_tool("inner agent")])
    assert outer.run("q") == "inner failed, telling the user"
    assert outer_llm.requests[1]["messages"][-1]["content"][0]["is_error"] is True


# --- the multi-agent worked example (Chapter 4.4) ---

def test_worked_example():
    llms = scripted_llms()
    orchestrator, trace = build_bi_system(llms)
    assert orchestrator.run(QUESTION) == FINAL_ANSWER
    assert trace.summary() == [
        ("catalog_agent", "search_docs", True),
        ("catalog_agent", "search_docs", True),
        ("orchestrator", "ask_catalog_agent", True),
        ("sql_agent", "run_sql", False),
        ("sql_agent", "check_metric_sql", True),
        ("sql_agent", "check_metric_sql", True),
        ("sql_agent", "run_sql", True),
        ("orchestrator", "ask_sql_agent", True),
    ]
    # The two parallel searches came back in one message, with the definition in it.
    catalog_results = llms["catalog_agent"].requests[1]["messages"][-1]["content"]
    assert len(catalog_results) == 2 and '<doc id="metric_revenue"' in catalog_results[0]["content"]
    # The SQL agent saw its database error and the metric check's complaints.
    sql_requests = llms["sql_agent"].requests
    assert "no such column" in sql_requests[1]["messages"][-1]["content"][0]["content"]
    assert "Problems:" in sql_requests[2]["messages"][-1]["content"][0]["content"]
    assert json.loads(trace.events[6].output)["rows"] == [["EU", 231.0], ["NA", 160.0], ["APAC", 100.0]]
    # Context isolation: the orchestrator never saw the SQL agent's failed query.
    orchestrator_history = json.dumps(llms["orchestrator"].requests[-1]["messages"])
    assert "amount_usd" not in orchestrator_history
    # Every agent got only its own tools.
    assert llms["sql_agent"].requests[0]["tools"] == ["run_sql", "check_metric_sql"]


# --- the Claude adapter, against a stand-in client (no network) ---

def fake_client(stop_reason="end_turn", content=None):
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        blocks = content or [SimpleNamespace(type="text", text="hello")]
        return SimpleNamespace(content=blocks, stop_reason=stop_reason, stop_details=None)

    return SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(create=create))), calls


def test_claude_adapter_request_shape():
    client, calls = fake_client(stop_reason="tool_use", content=[
        SimpleNamespace(type="tool_use", id="toolu_1", name="run_sql", input={"sql": "SELECT 1"})])
    reply = ClaudeLLM(client=client).complete("sys", [{"role": "user", "content": "q"}], [])
    assert reply.tool_calls[0].input == {"sql": "SELECT 1"}
    assert calls[0]["model"] == "claude-opus-5-5"
    assert calls[0]["fallbacks"] == "default"
    assert calls[0]["output_config"] == {"effort": "medium"}


def test_claude_adapter_refusal_raises():
    client, _ = fake_client(stop_reason="refusal")
    with pytest.raises(LLMError):
        ClaudeLLM(client=client).complete("sys", [{"role": "user", "content": "q"}], [])
