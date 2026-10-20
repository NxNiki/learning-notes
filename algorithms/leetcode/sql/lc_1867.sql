# Write your MySQL query statement below

with average_quantity as (
    select
        order_id,
        avg(quantity) avg_quantity
    from
        OrdersDetails
    group by
        order_id
)

select
    order_id
from
    OrdersDetails
group by
    order_id
having max(quantity) > (select max(avg_quantity) from average_quantity)


solution 2:

select 
    order_id
from (
    select
        order_id,
        max(avg(quantity)) over() as max_avg_quantity,
        max(quantity) as max_quantity
    from
        OrdersDetails
    group by 
        order_id
) t
where max_quantity > max_avg_quantity

-- The inner avg(quantity) is part of the group by aggregation. Then, the max() over() is a window function applied to the result of the group by.

