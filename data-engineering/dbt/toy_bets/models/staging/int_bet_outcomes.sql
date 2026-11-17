{{ config(materialized='ephemeral') }}

SELECT
    *,
    payout - bet_amount AS profit,
    {{ safe_divide('payout', 'bet_amount') }} AS rtp,
    CASE WHEN payout > bet_amount THEN 1 ELSE 0 END AS is_win
FROM {{ ref('stg_bets') }}
