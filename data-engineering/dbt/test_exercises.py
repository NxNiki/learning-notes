"""Applies the solution of each exercise of README.md Chapter 13 to a copy of toy_bets and checks its answer.

Skipped when dbt-duckdb is not installed. Each test edits its own copy, so toy_bets/ is never changed.
"""
import datetime
import shutil
from pathlib import Path

import pytest

duckdb = pytest.importorskip("duckdb")
dbt_main = pytest.importorskip("dbt.cli.main")

from render import CompilerError, Renderer  # noqa: E402

PROJECT = Path(__file__).parent / "toy_bets"
DAY1 = '{as_of: "2026-01-01 23:59:59"}'


class Copy:
    """A copy of toy_bets in a temporary folder, with its own database."""

    def __init__(self, tmp, monkeypatch):
        self.dir = tmp / "toy_bets"
        shutil.copytree(PROJECT, self.dir, ignore=shutil.ignore_patterns("target", "logs", "*.duckdb*"))
        self.db = tmp / "toy.duckdb"
        self.monkeypatch = monkeypatch
        monkeypatch.setenv("DBT_SEND_ANONYMOUS_USAGE_STATS", "false")

    def edit(self, path, old, new):
        f = self.dir / path
        text = f.read_text()
        assert old in text, f"{old!r} not in {path}"
        f.write_text(text.replace(old, new, 1))

    def dbt(self, *args, ok=True):
        self.monkeypatch.setenv("TOY_BETS_DB", str(self.db))    # profiles.yml reads it
        result = dbt_main.dbtRunner().invoke([*args, "--project-dir", str(self.dir), "--profiles-dir", str(self.dir)])
        assert result.success == ok, f"dbt {' '.join(args)}: success={result.success}, {result.exception}"
        return result

    def two_runs(self, *extra):
        """Seed, run as of Jan 1, run as of Jan 2: the lab's steps 3 and 6."""
        self.dbt("seed")
        self.dbt("run", "--vars", DAY1, *extra)
        self.dbt("run")

    def query(self, sql):
        with duckdb.connect(str(self.db), read_only=True) as con:
            return con.sql(sql).fetchall()


@pytest.fixture
def toy(tmp_path, monkeypatch):
    return Copy(tmp_path, monkeypatch)


def test_1_win_metric(toy):
    toy.edit("macros/bet_metrics.sql", "('delta_t_seconds', 'delta_t_seconds'),",
             "('delta_t_seconds', 'delta_t_seconds'),\n        ('win', 'is_win'),")
    toy.two_runs()
    columns = [c for (c,) in toy.query("SELECT column_name FROM information_schema.columns"
                                       " WHERE table_name = 'user_day' AND column_name LIKE 'win%'")]
    assert sorted(columns) == ["win_avg", "win_max", "win_median", "win_min"]
    assert toy.query("SELECT user_id, CAST(bet_date AS VARCHAR), ROUND(win_avg, 2), win_max FROM user_day ORDER BY 1, 2") == [
        (101, "2026-01-01", 0.33, 1), (101, "2026-01-02", 0.0, 0), (102, "2026-01-01", 1.0, 1), (103, "2026-01-02", 0.5, 1)]


def test_2_delta_t_across_days(toy):
    toy.edit("models/marts/user_day.sql", "PARTITION BY user_id, bet_date ORDER BY", "PARTITION BY user_id ORDER BY")
    toy.two_runs()
    assert toy.query("SELECT user_id, CAST(bet_date AS VARCHAR), delta_t_seconds_avg, delta_t_seconds_max"
                     " FROM user_day ORDER BY 1, 2") == [
        (101, "2026-01-01", 90.0, 120.0), (101, "2026-01-02", 82620.0, 82620.0),
        (102, "2026-01-01", 120.0, 120.0), (103, "2026-01-02", 300.0, 300.0)]


def test_3_no_unique_key(toy):
    toy.edit("models/marts/fct_bets.sql", "unique_key='bet_id',\n", "")
    toy.two_runs("--full-refresh")
    assert toy.query("SELECT payout, status FROM fct_bets WHERE bet_id = 4 ORDER BY loaded_at") == [
        (0, "pending"), (40, "settled")]
    assert toy.query("SELECT n_bets FROM user_day WHERE user_id = 102") == [(3,)]
    failed = [r for r in toy.dbt("test", ok=False).result.results if r.status == "fail"]
    assert [(r.node.name, r.failures) for r in failed] == [("unique_fct_bets_bet_id", 1)]


def test_4_between_op(toy):
    toy.edit("macros/ab_group_case.sql", "    {%- else -%}",
             "    {%- elif rule['op'] == 'between' -%}\n"
             "        {%- set condition = column ~ ' BETWEEN ' ~ rule['values'][0] ~ ' AND ' ~ rule['values'][1] -%}\n"
             "    {%- else -%}")
    toy.edit("dbt_project.yml", "    - {label: holdout, op: in, values: [103]}\n",
             "    - {label: holdout, op: in, values: [103]}\n    - {label: early, op: between, values: [100, 101]}\n")
    toy.two_runs()
    assert toy.query("SELECT DISTINCT user_id, ab_group FROM fct_bets ORDER BY 1") == [
        (101, "early"), (102, "B"), (103, "holdout")]
    toy.edit("dbt_project.yml", "op: between", "op: betwen")
    result = toy.dbt("compile", "-s", "stg_bets", ok=False)
    assert "ab_rules[1]: unknown op 'betwen'" in str(result.exception)


@pytest.mark.parametrize("across_days", [False, True])
def test_5_incremental_user_day(toy, tmp_path, monkeypatch, across_days):
    if across_days:
        toy.edit("models/marts/user_day.sql", "PARTITION BY user_id, bet_date ORDER BY", "PARTITION BY user_id ORDER BY")
    full = Copy(tmp_path / "full", monkeypatch)       # the table version, same partitioning
    shutil.rmtree(full.dir)
    shutil.copytree(toy.dir, full.dir)
    toy.edit("models/marts/user_day.sql", "{%- set metrics",
             "{{ config(materialized='incremental', unique_key=['user_id', 'bet_date'],"
             " incremental_strategy='delete+insert') }}\n{%- set metrics")
    toy.edit("models/marts/user_day.sql", "    FROM {{ ref('fct_bets') }}\n",
             "    FROM {{ ref('fct_bets') }}\n    {% if is_incremental() %}\n"
             "    WHERE bet_date >= (SELECT MAX(bet_date) FROM {{ this }})\n    {% endif %}\n")
    toy.two_runs()
    incremental = toy.query("SELECT * FROM user_day ORDER BY 1, 2")
    full.two_runs()
    assert full.query("SELECT * FROM user_day ORDER BY 1, 2") == incremental


def test_6_at_most(toy):
    (toy.dir / "tests" / "generic" / "at_most.sql").write_text(
        "{% test at_most(model, column_name, value) %}\nSELECT *\nFROM {{ model }}\n"
        "WHERE {{ column_name }} > {{ value }}\n{% endtest %}\n")
    toy.edit("models/marts/_marts.yml", "      - name: ab_group\n",
             "      - name: rtp\n        tests:\n          - at_most:\n              value: 10\n      - name: ab_group\n")
    toy.two_runs()
    assert toy.query("SELECT MAX(rtp) FROM fct_bets") == [(8.0,)]
    results = toy.dbt("test").result.results
    assert len(results) == 9 and {r.status for r in results} == {"pass"}


def test_7_render_own_rules():
    rules = [{"label": "control", "op": "last_digit_in", "values": [0]},
             {"label": "treat", "op": "in", "values": [7, 8]}]
    assert Renderer(PROJECT / "macros", vars={"ab_rules": rules}).call("ab_group_case", "player_id") == (
        "CASE\n"
        "    WHEN player_id % 10 IN (0) THEN 'control'\n"
        "    WHEN player_id IN (7, 8) THEN 'treat'\n"
        "END")
    with pytest.raises(CompilerError):
        Renderer(PROJECT / "macros", vars={"ab_rules": [{"label": "x", "op": "?", "values": []}]}).call("ab_group_case", "c")


def test_8_check_strategy(toy):
    toy.edit("snapshots/bets_snapshot.sql", "updated_at='loaded_at'", "check_cols=['status', 'payout']")
    toy.edit("snapshots/bets_snapshot.sql", "strategy='timestamp'", "strategy='check'")
    toy.dbt("seed")
    toy.dbt("run", "--vars", DAY1)
    toy.dbt("snapshot")
    toy.dbt("run")
    toy.dbt("snapshot")
    rows = toy.query("SELECT status, CAST(dbt_valid_from AS DATE) FROM snapshots.bets_snapshot"
                     " WHERE bet_id = 4 ORDER BY dbt_valid_from")
    assert [status for status, _ in rows] == ["pending", "settled"]
    # the run time, not the data's loaded_at (2026-01-01 / 2026-01-02)
    assert all(valid_from > datetime.date(2026, 1, 2) for _, valid_from in rows)
