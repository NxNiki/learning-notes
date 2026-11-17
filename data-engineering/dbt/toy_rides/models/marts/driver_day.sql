{#- Per driver and day: count plus avg / median / min / max of every metric in trip_metrics(). -#}
{%- set metrics = trip_metrics() -%}

WITH trips AS (
    SELECT
        *,
        EXTRACT(EPOCH FROM started_at - LAG(started_at) OVER (
            PARTITION BY driver_id, trip_date ORDER BY started_at
        )) AS gap_seconds
    FROM {{ ref('fct_trips') }}
)

SELECT
    driver_id,
    trip_date,
    COUNT(*) AS n_trips,
{%- for alias, expr in metrics %}
    {{ metric_stats(alias, expr) }}{{ ',' if not loop.last }}
{%- endfor %}
FROM trips
GROUP BY driver_id, trip_date
