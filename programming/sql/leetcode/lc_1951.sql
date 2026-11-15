with common_follower as (
    select
        r1.user_id as user1_id,
        r2.user_id as user2_id,
        r1.follower_id as follower_id,
        count(r1.follower_id) over (partition by r1.user_id, r2.user_id) as num_followers
    from
        Relations r1
    inner join
        Relations r2
    on  r1.follower_id = r2.follower_id and r1.user_id < r2.user_id
)

select
    user1_id,
    user2_id
from common_follower
group by user1_id, user2_id
having count(*) = (select max(num_followers) from common_follower)

/*
In the having clause, we cannot simply use:
having count(*) = max(num_followers)

Due to the group by clause, max() will also apply for each group.
So all rows will be selected.
*/

-- use rank() to find user1, user2 pairs with most followers:

with common_follower as (
  select
    r1.user_id as user1_id,
    r2.user_id as user2_id,
    rank() over(order by count(*) desc) as follower_rank
  from
    Relations r1
  inner join
    Relations r2
  on r1.follower_id = r2.follower_id and r1.user_id < r2.user_id
  group by user1_id, user2_id
)

select
  user1_id,
  user2_id
from
  common_follower
where
  follower_rank = 1
