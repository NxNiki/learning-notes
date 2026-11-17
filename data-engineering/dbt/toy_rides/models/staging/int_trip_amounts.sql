{{ config(materialized='ephemeral') }}

SELECT
    *,
    fare + tip AS total,
    {{ safe_divide('tip', 'fare') }} AS tip_rate,
    CASE WHEN tip > 0 THEN 1 ELSE 0 END AS has_tip
FROM {{ ref('stg_trips') }}
