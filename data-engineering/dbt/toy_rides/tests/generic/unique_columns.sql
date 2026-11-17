{#- No two rows share the same values in all of `columns`. -#}
{% test unique_columns(model, columns) %}
SELECT {{ columns | join(', ') }}, COUNT(*) AS n
FROM {{ model }}
GROUP BY {{ columns | join(', ') }}
HAVING COUNT(*) > 1
{% endtest %}
