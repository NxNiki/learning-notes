with insurance_aug as (
    select 
        *,
        count(pid) over (partition by lat, lon) as city_count,
        count(pid) over (partition by tiv_2015) as tiv_2015_count
    from
        Insurance
)

select
  round(sum(tiv_2016), 2) as tiv_2016
from insurance_aug
where tiv_2015_count > 1 and city_count = 1


## correlated subquery:

select
  round(sum(tiv_2016), 2) as tiv_2016
from
  Insurance
where
  tiv_2015 in ( select tiv_2015 from Insurance group by tiv_2015 having count(*) > 1 ) and
  (lat, lon) in ( select lat, lon from Insurance group by lat, lon having count(*) = 1)
