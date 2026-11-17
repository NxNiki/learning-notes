-- A singular test: one query, about specific models. Fails if it returns rows.
SELECT bet_id, bet_amount, payout
FROM {{ ref('fct_bets') }}
WHERE payout > 10 * bet_amount
