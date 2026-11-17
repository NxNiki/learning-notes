"""Checks every Jinja example of README.md (Chapters 2, 3, 6, 10) with plain Jinja2; no dbt needed."""
from pathlib import Path

import jinja2
import pytest
import yaml

from render import CompilerError, Renderer, render

HERE = Path(__file__).parent
VARS = yaml.safe_load((HERE / "toy_bets" / "dbt_project.yml").read_text())["vars"]


@pytest.mark.parametrize("template, expected", [
    # 2.1
    ("{{ 1 + 2 }} {{ 'bet' ~ '_' ~ 3 }} {{ [1, 2, 3] | length }} {{ 'abc' | upper }}", "3 bet_3 3 ABC"),
    ("a{# not in the output #}b", "ab"),
    # 2.3
    ("{% set q %}\nSELECT COUNT(*)\nFROM bets\n{% endset %}[{{ q | trim }}]", "[SELECT COUNT(*)\nFROM bets]"),
    # 2.4
    ("{% set n = 3 %}{% if n > 5 %}big{% elif n > 1 %}medium{% else %}small{% endif %}", "medium"),
    ("{{ none is none }} {{ x is defined }} {{ 4 is even }} {{ 'a' in ['a', 'b'] }}", "True False True True"),
    # 2.5
    ("{% for c in ['a', 'b', 'c'] %}{{ loop.index0 }}:{{ c }}{{ ', ' if not loop.last }}{% endfor %}", "0:a, 1:b, 2:c"),
    ("{% for c in ['a', 'b', 'c'] if c != 'b' %}{{ loop.index0 }}:{{ c }} {% endfor %}", "0:a 1:c "),
    # 2.6
    ("SELECT\n{% for c in ['a', 'b'] %}\n    {{ c }},\n{% endfor %}\n1", "SELECT\n\n    a,\n\n    b,\n\n1"),
    ("SELECT\n{%- for c in ['a', 'b'] %}\n    {{ c }},\n{%- endfor %}\n1", "SELECT\n    a,\n    b,\n1"),
    # 2.7
    ("{{ [3, 1, 2] | sort | list }} {{ ['1', '2'] | map('int') | sum }} {{ 'a_b' | replace('_', '-') }}", "[1, 2, 3] 3 a-b"),
    ("{{ [('x', 1), ('y', 2)] | rejectattr(0, 'equalto', 'x') | list }}", "[('y', 2)]"),
    ("{{ ['a', 'b'] | join(', ') }} {{ ' x ' | trim }} {{ '7' | int + 1 }}", "a, b x 8"),
    # 2.8
    ("{% set total = 0 %}{% for x in [1, 2, 3] %}{% set total = total + x %}{% endfor %}{{ total }}", "0"),
    ("{% set ns = namespace(total=0) %}{% for x in [1, 2, 3] %}{% set ns.total = ns.total + x %}{% endfor %}{{ ns.total }}", "6"),
    ("{% set cols = [] %}{% for m in ['bet', 'payout'] %}{% do cols.append(m ~ '_avg') %}{% endfor %}{{ cols | join(', ') }}",
     "bet_avg, payout_avg"),
    # 2.9
    ("{% macro pct(col, q=0.5) -%}\nPERCENTILE_CONT({{ q }}) WITHIN GROUP (ORDER BY {{ col }})\n{%- endmacro %}\n"
     "{{ pct('payout') }} | {{ pct('payout', q=0.25) }}",
     "\nPERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY payout) | PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY payout)"),
    ("{% macro two() %}2{% endmacro %}{% set v = two() %}{{ v ~ v }} {{ v is string }}", "22 True"),
    # Chapter 10, gotchas 4, 5, 11
    ("{{ none | default('x') }} {{ none | default('x', true) }} {{ y | default('x') }}", "None x x"),
    ("{{ 3 * 2 | string }}", "222"),
])
def test_example(template, expected):
    assert render(template) == expected


def test_plus_needs_strings():               # 2.1
    with pytest.raises(TypeError, match="can only concatenate str"):
        render("{{ 'bet_' + 3 }}")


def test_dict_values_is_a_method():          # 2.2, Chapter 10 gotcha 2
    template = "{% set rule = {'label': 'A', 'values': [1, 3]} %}"
    assert render(template + "{{ rule['values'] | join('/') }} {{ rule.label }} {{ rule.get('op', 'in') }}") == "1/3 A in"
    with pytest.raises(TypeError, match="not iterable"):
        render(template + "{{ rule.values | join('/') }}")


def test_sql_comment_is_rendered():          # Chapter 10 gotcha 12
    assert render("-- {{ 1 + 1 }}") == "-- 2"


# The toy project's macros, rendered with render.py (Chapters 3, 6, 9)

@pytest.fixture
def toy():
    return Renderer(HERE / "toy_bets" / "macros", vars=VARS)


def test_config_macro_returns_a_list(toy):   # 3.4, 6.2
    metrics = toy.call("bet_metrics")
    assert isinstance(metrics, list) and len(metrics) == 5
    assert metrics[0] == ("bet_amount", "bet_amount")


def test_safe_divide(toy):                   # 6.1
    assert toy.call("safe_divide", "payout", "bet_amount").strip() == "(payout) / NULLIF(bet_amount, 0)"


def test_metric_stats(toy):                  # 6.3
    assert toy.call("metric_stats", "payout", "payout") == (
        "AVG(payout) AS payout_avg,\n"
        "    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY payout) AS payout_median,\n"
        "    MIN(payout) AS payout_min,\n"
        "    MAX(payout) AS payout_max")


def test_ab_group_case(toy):                 # 6.4
    assert toy.call("ab_group_case", "user_id") == (
        "CASE\n"
        "    WHEN user_id IN (103) THEN 'holdout'\n"
        "    WHEN user_id % 10 IN (1, 3, 5, 7, 9) THEN 'A'\n"
        "    WHEN user_id % 10 IN (0, 2, 4, 6, 8) THEN 'B'\n"
        "END")


def test_ab_group_case_rejects_unknown_op():  # 6.4
    rules = VARS["ab_rules"] + [{"label": "C", "op": "betwen", "values": [1, 2]}]
    r = Renderer(HERE / "toy_bets" / "macros", vars={"ab_rules": rules})
    with pytest.raises(CompilerError, match=r"ab_rules\[3\]: unknown op 'betwen'"):
        r.call("ab_group_case", "user_id")


def test_user_day_has_20_stat_columns(toy):  # 6.3
    sql = toy.render_file(HERE / "toy_bets" / "models" / "marts" / "user_day.sql")
    stats = [line for line in sql.splitlines() if line.strip().startswith(("AVG(", "PERCENTILE_CONT(", "MIN(", "MAX("))]
    assert len(stats) == 20
    assert stats[-1].strip() == "MAX(delta_t_seconds) AS delta_t_seconds_max"


def test_missing_var_is_an_error():          # 3.3
    r = Renderer(HERE / "toy_bets" / "macros", vars={})
    with pytest.raises(CompilerError, match="ab_rules"):
        r.call("ab_group_case", "user_id")


def test_strict_undefined_in_render():
    with pytest.raises(jinja2.UndefinedError):
        render("{{ undefined_name + 1 }}")
