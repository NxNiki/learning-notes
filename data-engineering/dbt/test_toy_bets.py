"""Builds toy_bets with dbt + DuckDB and checks the lab (Section 1.6) and every table of README.md Chapters 5-8 and 11.

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

PROJECT = Path(__file__).parent / "toy_bets"
DAY1 = '{as_of: "2026-01-01 23:59:59"}'

# (bet_id, ab_group, payout, status, profit, rtp) after each run, README Section 5.2
AFTER_DAY1 = [
    (1, "A", 0, "settled", -10, 0.0),
    (2, "A", 25, "settled", 15, 2.5),
    (3, "A", 0, "settled", -20, 0.0),
    (4, "B", 0, "pending", -5, 0.0),
    (5, "B", 15, "settled", 10, 3.0),
]
AFTER_DAY2 = [
    (1, "A", 0, "settled", -10, 0.0),
    (2, "A", 25, "settled", 15, 2.5),
    (3, "A", 0, "settled", -20, 0.0),
    (4, "B", 40, "settled", 35, 8.0),
    (5, "B", 15, "settled", 10, 3.0),
    (6, "A", 10, "settled", 0, 1.0),
    (7, "holdout", 0, "settled", -50, 0.0),
    (8, "holdout", 120, "settled", 70, 2.4),
]
FCT = "SELECT bet_id, ab_group, payout, status, profit, rtp FROM fct_bets ORDER BY bet_id"


class Toy:
    def __init__(self, tmp, monkeypatch, name):
        self.db = tmp / f"{name}.duckdb"
        self.tmp = tmp
        monkeypatch.setenv("TOY_BETS_DB", str(self.db))
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
    toy = Toy(tmp_path_factory.mktemp("incremental"), mp, "toy")
    toy.dbt("seed")
    toy.dbt("run", "--vars", DAY1)
    toy.after_day1 = toy.query(FCT)
    run_sql = toy.tmp / "target" / "run" / "toy_bets" / "models" / "marts" / "fct_bets.sql"
    toy.run_sql_day1 = run_sql.read_text()
    toy.dbt("snapshot")
    toy.dbt("run")
    toy.run_sql_day2 = run_sql.read_text()
    toy.dbt("snapshot")
    yield toy
    mp.undo()


def test_first_run_builds_everything(built):     # 5.2, run 1
    assert built.after_day1 == AFTER_DAY1


def test_incremental_run_replaces_bet_4(built):  # 5.2, run 2
    assert built.query(FCT) == AFTER_DAY2


def test_incremental_equals_full_refresh(built, tmp_path, monkeypatch):  # 5.2
    fresh = Toy(tmp_path, monkeypatch, "fresh")
    fresh.dbt("seed")
    fresh.dbt("run", "--full-refresh")
    assert fresh.query(FCT) == built.query(FCT)
    assert fresh.query("SELECT * FROM user_day ORDER BY 1, 2") == built.query("SELECT * FROM user_day ORDER BY 1, 2")


def test_user_day(built):                        # 6.3
    rows = built.query(
        "SELECT user_id, CAST(bet_date AS VARCHAR), n_bets, ROUND(bet_amount_avg, 2), payout_median,"
        " profit_min, profit_max, delta_t_seconds_avg, delta_t_seconds_max FROM user_day ORDER BY 1, 2")
    assert rows == [
        (101, "2026-01-01", 3, 13.33, 0.0, -20, 15, 90.0, 120.0),
        (101, "2026-01-02", 1, 10.0, 10.0, 0, 0, None, None),
        (102, "2026-01-01", 2, 5.0, 27.5, 10, 35, 120.0, 120.0),
        (103, "2026-01-02", 2, 50.0, 60.0, -50, 70, 300.0, 300.0),
    ]


def test_all_tests_pass(built):                  # 7.3
    results = built.dbt("test").result.results
    assert len(results) == 8
    assert {r.status for r in results} == {"pass"}


def test_run_operation(built):                   # 3.6
    built.dbt("run-operation", "row_count", "--args", "{model_name: fct_bets}")


def test_render_py_matches_dbt_compile(built):   # 9.2
    built.dbt("compile", "-s", "stg_bets", "user_day")
    compiled = built.tmp / "target" / "compiled" / "toy_bets" / "models"
    vars = yaml.safe_load((PROJECT / "dbt_project.yml").read_text())["vars"]
    r = Renderer(PROJECT / "macros", vars=vars)
    user_day = r.render_file(PROJECT / "models" / "marts" / "user_day.sql")
    assert user_day.replace("fct_bets", '"toy"."main"."fct_bets"') == (compiled / "marts" / "user_day.sql").read_text()
    stg = r.render_file(PROJECT / "models" / "staging" / "stg_bets.sql")
    assert stg.replace("raw.raw_bets", '"toy"."main"."raw_bets"') == (compiled / "staging" / "stg_bets.sql").read_text()


def test_build_on_empty_database_fails(tmp_path, monkeypatch):  # 1.6, step 2
    toy = Toy(tmp_path, monkeypatch, "empty")
    results = {r.node.name: r.status for r in toy.dbt("build", ok=False).result.results}
    assert results["stg_bets"] == "error"
    assert results["raw_bets"] == "success"
    assert results["fct_bets"] == results["user_day"] == results["bets_snapshot"] == "skipped"


def test_first_run_creates_then_deletes_and_inserts(built):  # 1.6, steps 4 and 6
    day1, day2 = (" ".join(sql.split()) for sql in (built.run_sql_day1, built.run_sql_day2))
    assert "create table" in day1 and "delete from" not in day1
    assert "delete from" in day2 and "insert into" in day2


def test_snapshot_keeps_both_versions_of_bet_4(built):  # 1.6 step 7, 8.3
    rows = built.query(
        "SELECT payout, status, CAST(dbt_valid_from AS VARCHAR), CAST(dbt_valid_to AS VARCHAR)"
        " FROM snapshots.bets_snapshot WHERE bet_id = 4 ORDER BY dbt_valid_from")
    assert rows == [(0, "pending", "2026-01-01 23:00:00", "2026-01-02 23:00:00"),
                    (40, "settled", "2026-01-02 23:00:00", None)]
    assert built.query("SELECT COUNT(*) FROM snapshots.bets_snapshot WHERE dbt_valid_to IS NULL") == [(8,)]


def test_failing_test_skips_downstream(built, tmp_path):  # 1.6, step 8
    project = tmp_path / "toy_bets"
    shutil.copytree(PROJECT, project, ignore=shutil.ignore_patterns("target", "logs", "*.duckdb*"))
    test = project / "tests" / "assert_payout_at_most_10x.sql"
    test.write_text(test.read_text().replace("10 * bet_amount", "2 * bet_amount"))
    results = {r.node.name: r for r in built.dbt("build", project=project, ok=False).result.results}
    assert results["assert_payout_at_most_10x"].status == "fail"
    assert results["assert_payout_at_most_10x"].failures == 4
    assert results["user_day"].status == "skipped"


def test_state_modified(built, tmp_path):  # 11.3, 11.4
    project = tmp_path / "toy_bets"
    shutil.copytree(PROJECT, project, ignore=shutil.ignore_patterns("target", "logs", "*.duckdb*"))
    built.dbt("parse", project=project)
    manifest = json.loads((built.tmp / "target" / "manifest.json").read_text())
    assert manifest["nodes"]["model.toy_bets.user_day"]["depends_on"] == {
        "macros": ["macro.toy_bets.bet_metrics", "macro.toy_bets.metric_stats"],
        "nodes": ["model.toy_bets.fct_bets"]}
    state = tmp_path / "prod-state"
    shutil.copytree(built.tmp / "target", state)
    model = project / "models" / "staging" / "int_bet_outcomes.sql"
    model.write_text(model.read_text().replace("AS is_win", "AS is_win,\n    payout = 0 AS is_loss"))

    def ls(selector, *extra):
        result = built.dbt("ls", "-s", selector, "--state", str(state), *extra, project=project)
        return sorted(result.result)

    assert ls("state:modified") == ["toy_bets.staging.int_bet_outcomes"]
    assert ls("state:modified+", "--resource-type", "model") == [
        "toy_bets.marts.fct_bets", "toy_bets.marts.user_day", "toy_bets.staging.int_bet_outcomes"]
