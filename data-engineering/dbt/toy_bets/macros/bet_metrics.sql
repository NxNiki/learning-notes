{#- The metrics of user_day, as (alias, SQL expression). A "config macro": it
    renders nothing and only hands back a value with return(). Adding a pair
    here adds five columns to user_day. -#}
{% macro bet_metrics() %}
    {{ return([
        ('bet_amount', 'bet_amount'),
        ('payout', 'payout'),
        ('profit', 'profit'),
        ('rtp', 'rtp'),
        ('delta_t_seconds', 'delta_t_seconds'),
    ]) }}
{% endmacro %}

{#- avg / median / min / max of one expression, as four comma-separated columns -#}
{% macro metric_stats(alias, expr) -%}
    AVG({{ expr }}) AS {{ alias }}_avg,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {{ expr }}) AS {{ alias }}_median,
    MIN({{ expr }}) AS {{ alias }}_min,
    MAX({{ expr }}) AS {{ alias }}_max
{%- endmacro %}
