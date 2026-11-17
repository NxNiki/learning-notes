{#- One row per bet: its latest version among the rows loaded by var('as_of'). -#}
WITH arrived AS (
    SELECT *
    FROM {{ source('raw', 'raw_bets') }}
    WHERE loaded_at <= '{{ var("as_of") }}'
),

latest AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY bet_id ORDER BY loaded_at DESC) AS version_rank
    FROM arrived
)

SELECT
    bet_id,
    user_id,
    {{ ab_group_case('user_id') }} AS ab_group,
    bet_amount,
    payout,
    status,
    created_at,
    CAST(created_at AS DATE) AS bet_date,
    loaded_at
FROM latest
WHERE version_rank = 1
