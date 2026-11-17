{#- a / b, or NULL when b is 0 (instead of a division-by-zero error) -#}
{% macro safe_divide(a, b) -%}
    ({{ a }}) / NULLIF({{ b }}, 0)
{%- endmacro %}
