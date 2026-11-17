{#- History of every bet: a new row each time a bet's loaded_at moves forward
    (strategy 'timestamp'). Reads stg_bets, so it sees the world as of the
    as_of that stg_bets was last built with. -#}
{% snapshot bets_snapshot %}
{{
    config(
        target_schema='snapshots',
        unique_key='bet_id',
        strategy='timestamp',
        updated_at='loaded_at'
    )
}}
SELECT bet_id, user_id, payout, status, loaded_at
FROM {{ ref('stg_bets') }}
{% endsnapshot %}
