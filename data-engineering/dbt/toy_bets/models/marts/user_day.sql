{#- Per user and day: count plus avg / median / min / max of every metric in bet_metrics(). -#}
{%- set metrics = bet_metrics() -%}

WITH bets AS (
    SELECT
        *,
        EXTRACT(EPOCH FROM created_at - LAG(created_at) OVER (
            PARTITION BY user_id, bet_date ORDER BY created_at
        )) AS delta_t_seconds
    FROM {{ ref('fct_bets') }}
)

SELECT
    user_id,
    bet_date,
    COUNT(*) AS n_bets,
{%- for alias, expr in metrics %}
    {{ metric_stats(alias, expr) }}{{ ',' if not loop.last }}
{%- endfor %}
FROM bets
GROUP BY user_id, bet_date
