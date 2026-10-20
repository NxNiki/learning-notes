# solution 1:

select
    'Low Salary' as category,
    (select count(*) from Accounts where income < 20000) as accounts_count
union all
select
    'Average Salary' as category,
    (select count(*) from Accounts where income <=50000 and income >= 20000) as accounts_count
union all
select
    'High Salary' as category,
    (select count(*) from Accounts where income > 50000)


# solution 2:

with accounts_cat as (
  select
    *,
    case
      when income < 20000 then 'Low Salary'
      when income > 50000 then 'High Salary'
      else 'Average Salary'
    end as category
  from
    Accounts
),

category_table as (
  select 'Low Salary' as category
  union all
  select 'Average Salary' as category
  union all
  select 'High Salary' as category
)

select
  category_table.category,
  coalesce(count(accounts_cat.category), 0) as accounts_count
from
  category_table
left join
  accounts_cat
on
  category_table.category = accounts_cat.category
group by
  category

