-- solution 1:
with cte as (
    select
        id,
        num,
        lead(num) over(order by id) as num_lead,
        lag(num) over(order by id) as num_lag
    from
        Logs
)

select 
    distinct num as ConsecutiveNums
from
    cte
where num = num_lead and num = num_lag

-- solution 2:

with cte as (
    select num,
    lead(num,1) over() num1,
    lead(num,2) over() num2
    from logs

)

select distinct num ConsecutiveNums from cte where (num=num1) and (num=num2)
