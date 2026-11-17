-- A singular test: one query, about specific models. Fails if it returns rows.
-- A tip larger than the fare is possible but rare; here it flags bad data.
SELECT trip_id, fare, tip
FROM {{ ref('fct_trips') }}
WHERE tip > fare
