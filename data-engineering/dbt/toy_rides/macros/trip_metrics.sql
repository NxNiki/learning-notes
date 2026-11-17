{#- The metrics of driver_day, as (alias, SQL expression). A "config macro": it
    renders nothing and only hands back a value with return(). Adding a pair
    here adds four columns to driver_day. -#}
{% macro trip_metrics() %}
    {{ return([
        ('fare', 'fare'),
        ('tip', 'tip'),
        ('total', 'total'),
        ('tip_rate', 'tip_rate'),
        ('gap_seconds', 'gap_seconds'),
    ]) }}
{% endmacro %}

{#- avg / median / min / max of one expression, as four comma-separated columns -#}
{% macro metric_stats(alias, expr) -%}
    AVG({{ expr }}) AS {{ alias }}_avg,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {{ expr }}) AS {{ alias }}_median,
    MIN({{ expr }}) AS {{ alias }}_min,
    MAX({{ expr }}) AS {{ alias }}_max
{%- endmacro %}
