{#- dbt run-operation row_count --args '{model_name: fct_bets}'
    Runs a query at compile time and logs the answer. -#}
{% macro row_count(model_name) %}
    {% set query %}
        SELECT COUNT(*) FROM {{ ref(model_name) }}
    {% endset %}
    {% if execute %}
        {% set n = run_query(query).columns[0].values()[0] %}
        {{ log(model_name ~ ' has ' ~ n ~ ' rows', info=True) }}
    {% endif %}
{% endmacro %}
