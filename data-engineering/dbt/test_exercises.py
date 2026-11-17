"""Applies the solution of each exercise of README.md Chapter 13 to a copy of toy_rides and checks its answer.

Skipped when dbt-duckdb is not installed. Each test edits its own copy, so toy_rides/ is never changed.
"""
import datetime
import shutil
from pathlib import Path

import pytest

duckdb = pytest.importorskip("duckdb")
dbt_main = pytest.importorskip("dbt.cli.main")

from render import CompilerError, Renderer  # noqa: E402

PROJECT = Path(__file__).parent / "toy_rides"
DAY1 = '{as_of: "2026-01-01 23:59:59"}'


class Copy:
    """A copy of toy_rides in a temporary folder, with its own database."""

    def __init__(self, tmp, monkeypatch):
        self.dir = tmp / "toy_rides"
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
        self.monkeypatch.setenv("TOY_RIDES_DB", str(self.db))    # profiles.yml reads it
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


def test_1_tipped_metric(toy):
    toy.edit("macros/trip_metrics.sql", "('gap_seconds', 'gap_seconds'),",
             "('gap_seconds', 'gap_seconds'),\n        ('tipped', 'has_tip'),")
    toy.two_runs()
    columns = [c for (c,) in toy.query("SELECT column_name FROM information_schema.columns"
                                       " WHERE table_name = 'driver_day' AND column_name LIKE 'tipped%'")]
    assert sorted(columns) == ["tipped_avg", "tipped_max", "tipped_median", "tipped_min"]
    assert toy.query("SELECT driver_id, CAST(trip_date AS VARCHAR), ROUND(tipped_avg, 2), tipped_max FROM driver_day ORDER BY 1, 2") == [
        (101, "2026-01-01", 0.33, 1), (101, "2026-01-02", 1.0, 1), (102, "2026-01-01", 0.5, 1), (103, "2026-01-02", 0.5, 1)]


def test_2_gap_across_days(toy):
    toy.edit("models/marts/driver_day.sql", "PARTITION BY driver_id, trip_date ORDER BY", "PARTITION BY driver_id ORDER BY")
    toy.two_runs()
    assert toy.query("SELECT driver_id, CAST(trip_date AS VARCHAR), gap_seconds_avg, gap_seconds_max"
                     " FROM driver_day ORDER BY 1, 2") == [
        (101, "2026-01-01", 2100.0, 2400.0), (101, "2026-01-02", 78600.0, 78600.0),
        (102, "2026-01-01", 2700.0, 2700.0), (103, "2026-01-02", 3000.0, 3000.0)]


def test_3_no_unique_key(toy):
    toy.edit("models/marts/fct_trips.sql", "unique_key='trip_id',\n", "")
    toy.two_runs("--full-refresh")
    assert toy.query("SELECT tip, status FROM fct_trips WHERE trip_id = 4 ORDER BY loaded_at") == [
        (0, "completed"), (6, "completed")]
    assert toy.query("SELECT n_trips, fare_avg * n_trips FROM driver_day WHERE driver_id = 102") == [(3, 60.0)]
    failed = [r for r in toy.dbt("test", ok=False).result.results if r.status == "fail"]
    assert [(r.node.name, r.failures) for r in failed] == [("unique_fct_trips_trip_id", 1)]


def test_4_between_op(toy):
    toy.edit("macros/experiment_group_case.sql", "    {%- else -%}",
             "    {%- elif rule['op'] == 'between' -%}\n"
             "        {%- set condition = column ~ ' BETWEEN ' ~ rule['values'][0] ~ ' AND ' ~ rule['values'][1] -%}\n"
             "    {%- else -%}")
    toy.edit("dbt_project.yml", "    - {label: holdout, op: in, values: [103]}\n",
             "    - {label: holdout, op: in, values: [103]}\n    - {label: early, op: between, values: [100, 101]}\n")
    toy.two_runs()
    assert toy.query("SELECT DISTINCT driver_id, experiment_group FROM fct_trips ORDER BY 1") == [
        (101, "early"), (102, "B"), (103, "holdout")]
    toy.edit("dbt_project.yml", "op: between", "op: betwen")
    result = toy.dbt("compile", "-s", "stg_trips", ok=False)
    assert "experiment_rules[1]: unknown op 'betwen'" in str(result.exception)


@pytest.mark.parametrize("across_days", [False, True])
def test_5_incremental_driver_day(toy, tmp_path, monkeypatch, across_days):
    if across_days:
        toy.edit("models/marts/driver_day.sql", "PARTITION BY driver_id, trip_date ORDER BY", "PARTITION BY driver_id ORDER BY")
    full = Copy(tmp_path / "full", monkeypatch)       # the table version, same partitioning
    shutil.rmtree(full.dir)
    shutil.copytree(toy.dir, full.dir)
    toy.edit("models/marts/driver_day.sql", "{%- set metrics",
             "{{ config(materialized='incremental', unique_key=['driver_id', 'trip_date'],"
             " incremental_strategy='delete+insert') }}\n{%- set metrics")
    toy.edit("models/marts/driver_day.sql", "    FROM {{ ref('fct_trips') }}\n",
             "    FROM {{ ref('fct_trips') }}\n    {% if is_incremental() %}\n"
             "    WHERE trip_date >= (SELECT MAX(trip_date) FROM {{ this }})\n    {% endif %}\n")
    toy.two_runs()
    incremental = toy.query("SELECT * FROM driver_day ORDER BY 1, 2")
    full.two_runs()
    assert full.query("SELECT * FROM driver_day ORDER BY 1, 2") == incremental


def test_6_at_most(toy):
    (toy.dir / "tests" / "generic" / "at_most.sql").write_text(
        "{% test at_most(model, column_name, value) %}\nSELECT *\nFROM {{ model }}\n"
        "WHERE {{ column_name }} > {{ value }}\n{% endtest %}\n")
    toy.edit("models/marts/_marts.yml", "      - name: experiment_group\n",
             "      - name: tip_rate\n        tests:\n          - at_most:\n              value: 1\n      - name: experiment_group\n")
    toy.two_runs()
    assert toy.query("SELECT MAX(tip_rate) FROM fct_trips") == [(0.2,)]
    results = toy.dbt("test").result.results
    assert len(results) == 9 and {r.status for r in results} == {"pass"}


def test_7_render_own_rules():
    rules = [{"label": "control", "op": "last_digit_in", "values": [0]},
             {"label": "treat", "op": "in", "values": [7, 8]}]
    assert Renderer(PROJECT / "macros", vars={"experiment_rules": rules}).call("experiment_group_case", "customer_id") == (
        "CASE\n"
        "    WHEN customer_id % 10 IN (0) THEN 'control'\n"
        "    WHEN customer_id IN (7, 8) THEN 'treat'\n"
        "END")
    with pytest.raises(CompilerError):
        Renderer(PROJECT / "macros", vars={"experiment_rules": [{"label": "x", "op": "?", "values": []}]}).call("experiment_group_case", "c")


def test_8_check_strategy(toy):
    toy.edit("snapshots/trips_snapshot.sql", "updated_at='loaded_at'", "check_cols=['status', 'tip']")
    toy.edit("snapshots/trips_snapshot.sql", "strategy='timestamp'", "strategy='check'")
    toy.dbt("seed")
    toy.dbt("run", "--vars", DAY1)
    toy.dbt("snapshot")
    toy.dbt("run")
    toy.dbt("snapshot")
    rows = toy.query("SELECT tip, CAST(dbt_valid_from AS DATE) FROM snapshots.trips_snapshot"
                     " WHERE trip_id = 4 ORDER BY dbt_valid_from")
    assert [tip for tip, _ in rows] == [0, 6]
    # the run time, not the data's loaded_at (2026-01-01 / 2026-01-02)
    assert all(valid_from > datetime.date(2026, 1, 2) for _, valid_from in rows)
