"""Builds toy_rides with dbt + DuckDB and checks the lab (Section 1.6) and every table of README.md Chapters 5-8 and 11.

Skipped when dbt-duckdb is not installed (pip install -r data-engineering/dbt/requirements.txt).
Everything dbt writes (database, target/, logs/) goes to a temporary folder.
"""
import json
import shutil
from pathlib import Path

import pytest
import yaml

duckdb = pytest.importorskip("duckdb")
dbt_main = pytest.importorskip("dbt.cli.main")

from render import Renderer  # noqa: E402

PROJECT = Path(__file__).parent / "toy_rides"
DAY1 = '{as_of: "2026-01-01 23:59:59"}'

# (trip_id, experiment_group, tip, status, total, tip_rate) after each run, README Section 5.2
AFTER_DAY1 = [
    (1, "A", 0, "completed", 12, 0.0),
    (2, "A", 5, "completed", 30, 0.2),
    (3, "A", 0, "completed", 18, 0.0),
    (4, "B", 0, "completed", 30, 0.0),
    (5, "B", 0, "cancelled", 0, None),
]
AFTER_DAY2 = [
    (1, "A", 0, "completed", 12, 0.0),
    (2, "A", 5, "completed", 30, 0.2),
    (3, "A", 0, "completed", 18, 0.0),
    (4, "B", 6, "completed", 36, 0.2),
    (5, "B", 0, "cancelled", 0, None),
    (6, "A", 3, "completed", 18, 0.2),
    (7, "holdout", 0, "completed", 40, 0.0),
    (8, "holdout", 4, "completed", 26, 0.18),
]
FCT = "SELECT trip_id, experiment_group, tip, status, total, ROUND(tip_rate, 2) FROM fct_trips ORDER BY trip_id"


class Toy:
    def __init__(self, tmp, monkeypatch, name):
        self.db = tmp / f"{name}.duckdb"
        self.tmp = tmp
        monkeypatch.setenv("TOY_RIDES_DB", str(self.db))
        monkeypatch.setenv("DBT_SEND_ANONYMOUS_USAGE_STATS", "false")

    def dbt(self, *args, project=PROJECT, ok=True):
        common = ["--project-dir", str(project), "--profiles-dir", str(project),
                  "--target-path", str(self.tmp / "target"), "--log-path", str(self.tmp / "logs")]
        result = dbt_main.dbtRunner().invoke([args[0], *common, *args[1:]])
        assert result.success == ok, f"dbt {' '.join(args)}: success={result.success}, {result.exception}"
        return result

    def query(self, sql):
        with duckdb.connect(str(self.db), read_only=True) as con:
            return con.sql(sql).fetchall()


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """The lab, Section 1.6: seed, run + snapshot as of Jan 1, run + snapshot as of Jan 2."""
    mp = pytest.MonkeyPatch()
    toy = Toy(tmp_path_factory.mktemp("incremental"), mp, "toy_rides")
    toy.dbt("seed")
    toy.dbt("run", "--vars", DAY1)
    toy.after_day1 = toy.query(FCT)
    run_sql = toy.tmp / "target" / "run" / "toy_rides" / "models" / "marts" / "fct_trips.sql"
    toy.run_sql_day1 = run_sql.read_text()
    toy.dbt("snapshot")
    toy.dbt("run")
    toy.run_sql_day2 = run_sql.read_text()
    toy.dbt("snapshot")
    yield toy
    mp.undo()


def test_first_run_builds_everything(built):     # 5.2, run 1
    assert built.after_day1 == AFTER_DAY1


def test_incremental_run_replaces_trip_4(built):  # 5.2, run 2
    assert built.query(FCT) == AFTER_DAY2


def test_incremental_equals_full_refresh(built, tmp_path, monkeypatch):  # 5.2
    fresh = Toy(tmp_path, monkeypatch, "fresh")
    fresh.dbt("seed")
    fresh.dbt("run", "--full-refresh")
    assert fresh.query(FCT) == built.query(FCT)
    assert fresh.query("SELECT * FROM driver_day ORDER BY 1, 2") == built.query("SELECT * FROM driver_day ORDER BY 1, 2")


def test_driver_day(built):                      # 6.3
    rows = built.query(
        "SELECT driver_id, CAST(trip_date AS VARCHAR), n_trips, ROUND(fare_avg, 2), tip_median, total_min, total_max,"
        " ROUND(tip_rate_avg, 3), gap_seconds_avg, gap_seconds_max FROM driver_day ORDER BY 1, 2")
    assert rows == [
        (101, "2026-01-01", 3, 18.33, 0.0, 12, 30, 0.067, 2100.0, 2400.0),
        (101, "2026-01-02", 1, 15.0, 3.0, 18, 18, 0.2, None, None),
        (102, "2026-01-01", 2, 15.0, 3.0, 0, 36, 0.2, 2700.0, 2700.0),
        (103, "2026-01-02", 2, 31.0, 2.0, 26, 40, 0.091, 3000.0, 3000.0),
    ]


def test_all_tests_pass(built):                  # 7.3
    results = built.dbt("test").result.results
    assert len(results) == 8
    assert {r.status for r in results} == {"pass"}


def test_run_operation(built):                   # 3.6
    built.dbt("run-operation", "row_count", "--args", "{model_name: fct_trips}")


def test_render_py_matches_dbt_compile(built):   # 9.2
    built.dbt("compile", "-s", "stg_trips", "driver_day")
    compiled = built.tmp / "target" / "compiled" / "toy_rides" / "models"
    vars = yaml.safe_load((PROJECT / "dbt_project.yml").read_text())["vars"]
    r = Renderer(PROJECT / "macros", vars=vars)
    driver_day = r.render_file(PROJECT / "models" / "marts" / "driver_day.sql")
    assert driver_day.replace("fct_trips", '"toy_rides"."main"."fct_trips"') == (compiled / "marts" / "driver_day.sql").read_text()
    stg = r.render_file(PROJECT / "models" / "staging" / "stg_trips.sql")
    assert stg.replace("raw.raw_trips", '"toy_rides"."main"."raw_trips"') == (compiled / "staging" / "stg_trips.sql").read_text()


def test_build_on_empty_database_fails(tmp_path, monkeypatch):  # 1.6, step 2
    toy = Toy(tmp_path, monkeypatch, "empty")
    results = {r.node.name: r.status for r in toy.dbt("build", ok=False).result.results}
    assert results["stg_trips"] == "error"
    assert results["raw_trips"] == "success"
    assert results["fct_trips"] == results["driver_day"] == results["trips_snapshot"] == "skipped"


def test_first_run_creates_then_deletes_and_inserts(built):  # 1.6, steps 4 and 6
    day1, day2 = (" ".join(sql.split()) for sql in (built.run_sql_day1, built.run_sql_day2))
    assert "create table" in day1 and "delete from" not in day1
    assert "delete from" in day2 and "insert into" in day2


def test_snapshot_keeps_both_versions_of_trip_4(built):  # 1.6 step 7, 8.3
    rows = built.query(
        "SELECT fare, tip, CAST(dbt_valid_from AS VARCHAR), CAST(dbt_valid_to AS VARCHAR)"
        " FROM snapshots.trips_snapshot WHERE trip_id = 4 ORDER BY dbt_valid_from")
    assert rows == [(30, 0, "2026-01-01 23:00:00", "2026-01-02 23:00:00"),
                    (30, 6, "2026-01-02 23:00:00", None)]
    assert built.query("SELECT COUNT(*) FROM snapshots.trips_snapshot WHERE dbt_valid_to IS NULL") == [(8,)]


def test_failing_test_skips_downstream(built, tmp_path):  # 1.6, step 8
    project = tmp_path / "toy_rides"
    shutil.copytree(PROJECT, project, ignore=shutil.ignore_patterns("target", "logs", "*.duckdb*"))
    test = project / "tests" / "assert_tip_at_most_fare.sql"
    test.write_text(test.read_text().replace("WHERE tip > fare", "WHERE tip > 0.1 * fare"))
    results = {r.node.name: r for r in built.dbt("build", project=project, ok=False).result.results}
    assert results["assert_tip_at_most_fare"].status == "fail"
    assert results["assert_tip_at_most_fare"].failures == 4
    assert results["driver_day"].status == "skipped"


def test_state_modified(built, tmp_path):  # 11.3, 11.4
    project = tmp_path / "toy_rides"
    shutil.copytree(PROJECT, project, ignore=shutil.ignore_patterns("target", "logs", "*.duckdb*"))
    built.dbt("parse", project=project)
    manifest = json.loads((built.tmp / "target" / "manifest.json").read_text())
    assert manifest["nodes"]["model.toy_rides.driver_day"]["depends_on"] == {
        "macros": ["macro.toy_rides.trip_metrics", "macro.toy_rides.metric_stats"],
        "nodes": ["model.toy_rides.fct_trips"]}
    state = tmp_path / "prod-state"
    shutil.copytree(built.tmp / "target", state)
    model = project / "models" / "staging" / "int_trip_amounts.sql"
    model.write_text(model.read_text().replace("AS has_tip", "AS has_tip,\n    status = 'cancelled' AS is_cancelled"))

    def ls(selector, *extra):
        result = built.dbt("ls", "-s", selector, "--state", str(state), *extra, project=project)
        return sorted(result.result)

    assert ls("state:modified") == ["toy_rides.staging.int_trip_amounts"]
    assert ls("state:modified+", "--resource-type", "model") == [
        "toy_rides.marts.driver_day", "toy_rides.marts.fct_trips", "toy_rides.staging.int_trip_amounts"]
