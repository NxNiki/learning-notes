{#- A CASE expression that labels `column` by var('ab_rules'): an ordered list of
    {label, op, values}, first match wins, no match -> NULL. -#}
{% macro ab_group_case(column) -%}
{%- set rules = var('ab_rules') -%}
CASE
{%- for rule in rules %}
    {%- if rule['op'] == 'in' -%}
        {%- set condition = column ~ ' IN (' ~ rule['values'] | join(', ') ~ ')' -%}
    {%- elif rule['op'] == 'last_digit_in' -%}
        {%- set condition = column ~ ' % 10 IN (' ~ rule['values'] | join(', ') ~ ')' -%}
    {%- else -%}
        {{ exceptions.raise_compiler_error("ab_rules[" ~ loop.index0 ~ "]: unknown op '" ~ rule['op'] ~ "'") }}
    {%- endif %}
    WHEN {{ condition }} THEN '{{ rule["label"] }}'
{%- endfor %}
END
{%- endmacro %}
