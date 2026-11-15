with bus_weight as (
    select
        person_name,
        sum(weight) over(order by turn asc) as curr_weight
    from
        Queue
)

select
    person_name
from
    bus_weight
where
    curr_weight = (select max(curr_weight) from bus_weight where curr_weight <= 1000)


-- use `order by` and `limit` to select the row with max weight:

with bus_weight as (
    select
        person_name,
        sum(weight) over(order by turn asc) as curr_weight
    from
        Queue
)

select
    person_name
from
    bus_weight
where
    curr_weight <= 1000
order by curr_weight desc
limit 1
