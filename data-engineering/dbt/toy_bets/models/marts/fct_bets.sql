{{
    config(
        materialized='incremental',
        unique_key='bet_id',
        incremental_strategy='delete+insert',
        on_schema_change='append_new_columns',
        tags=['daily']
    )
}}

SELECT *
FROM {{ ref('int_bet_outcomes') }}
{% if is_incremental() %}
-- only rows that arrived after the newest row already in this table
WHERE loaded_at > (SELECT MAX(loaded_at) FROM {{ this }})
{% endif %}
