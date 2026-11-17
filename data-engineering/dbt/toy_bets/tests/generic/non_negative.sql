{#- A generic test: the query returns the failing rows; zero rows = pass. -#}
{% test non_negative(model, column_name) %}
SELECT *
FROM {{ model }}
WHERE {{ column_name }} < 0
{% endtest %}
