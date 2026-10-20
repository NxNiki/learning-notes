# Write your MySQL query statement below

with daily_amount as (
    select
        visited_on,
        sum(amount) as amount
    from
        Customer
    group by visited_on
)

select
    t1.visited_on,
    sum(t2.amount) as amount,
    round(sum(t2.amount)/7, 2) as average_amount
from 
    daily_amount t1, daily_amount t2
where
    datediff(t1.visited_on, t2.visited_on) between 0 and 6
group by
    t1.visited_on
having
    count(*) = 7


-- solution 2:

with cte as (
    select
        visited_on,
        sum(amount) over (order by visited_on range between interval 6 day preceding  and current row) as amount,
        min(visited_on) over() as 1st_date
    from Customer
)

select distinct visited_on, amount, round(amount/7, 2) average_amount 
from cte
where visited_on >= 1st_date + 6

