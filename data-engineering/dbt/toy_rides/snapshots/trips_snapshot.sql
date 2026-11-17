{#- History of every trip: a new row each time a trip's loaded_at moves forward
    (strategy 'timestamp'). Reads stg_trips, so it sees the world as of the
    as_of that stg_trips was last built with. -#}
{% snapshot trips_snapshot %}
{{
    config(
        target_schema='snapshots',
        unique_key='trip_id',
        strategy='timestamp',
        updated_at='loaded_at'
    )
}}
SELECT trip_id, driver_id, fare, tip, status, loaded_at
FROM {{ ref('stg_trips') }}
{% endsnapshot %}
