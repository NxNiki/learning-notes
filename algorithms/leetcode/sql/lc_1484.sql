
-- MySQL:
select
  sell_date,
  count(distinct product) as num_sold,
  group_concat(distinct product order by product asc separator ',') as products
from
  Activities
group by sell_date
order by sell_date asc

  
-- MS SQL Server:
with unique_activities as (
    select distinct *
    from Activities
)

select
    sell_date,
    count(product) as num_sold,
    string_agg(product, ',') within group (order by product asc) as products
from
    unique_activities
group by sell_date
order by sell_date asc
