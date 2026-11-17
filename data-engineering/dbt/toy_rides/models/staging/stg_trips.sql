{#- One row per trip: its latest version among the rows loaded by var('as_of'). -#}
WITH arrived AS (
    SELECT *
    FROM {{ source('raw', 'raw_trips') }}
    WHERE loaded_at <= '{{ var("as_of") }}'
),

latest AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY trip_id ORDER BY loaded_at DESC) AS version_rank
    FROM arrived
)

SELECT
    trip_id,
    driver_id,
    {{ experiment_group_case('driver_id') }} AS experiment_group,
    fare,
    tip,
    status,
    started_at,
    CAST(started_at AS DATE) AS trip_date,
    loaded_at
FROM latest
WHERE version_rank = 1
