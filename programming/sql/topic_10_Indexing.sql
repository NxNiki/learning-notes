## create index based on queries rather than on tables
## index are stored in binary trees

use sql_store;
explain select customer_id from customers where state = 'CA';

create index idx_state on customers (state);
create index idx_points on customers (points);

analyze table customers;
show indexes in customers;

## prefix index:
create index idx_lastname on customers (last_name(20));

# determine the lenght of characters included in index:
select
	count(distinct left(last_name, 1))
    , count(distinct left(last_name, 5))
    , count(distinct left(last_name, 10))
from customers;

use sql_blog;
## full text index:
## natural language mode:
create fulltext index idx_title_body on posts (title, body);

select *, match(title, body) against('react redux')
from posts
where match(title, body) against('react redux'); # return any posts that have one or both of these keywords in the title or body.

select *, match(title, body) against('react redux')
from posts
where match(title, body) against('react -redux' in boolean mode); # return any posts that have react but not redux

select *, match(title, body) against('react redux')
from posts
where match(title, body) against('react -redux +form' in boolean mode); # return any posts that have react but not redux, must have form in title/body.

select *, match(title, body) against('react redux')
from posts
where match(title, body) against('"handling a form"' in boolean mode); # having exactly "handling a form" in title/body.

## composite indexes:
use sql_store;

show indexes in customers;

# mutltiple indexes only do half job if filter on two columns.
# also more indexes will slow the write operations and takes more space.
explain select customer_id from customers
where state  = 'CA' and points < 1000;

# composite indexes help faster query and sort:
create index idx_state_points on customers (state, points);
explain select customer_id from customers
where state  = 'CA' and points < 1000;

# mysql allows composite index of up to 16 columns, genearlly 4 to 6 is optimized.

# drop indexes:
drop index idx_state on customers;

## order of columns in indexes:
# most frequently used columns come first
# columns with higher cardinality (number of unique values in the index) first. (not always the best practice, should always take the queries into account)
# query with more selective conditions come first in indexes.

create index idx_lastname_state on customers (last_name, state);

create index idx_state_lastname on customers (state, last_name);

explain select customer_id from customers
use index (idx_lastname_state)
where state  = 'CA' and points < 1000;

# compare the below queries:
explain select customer_id from customers
use index (idx_lastname_state)
where state = 'NY' and last_name like 'A%';

explain select customer_id from customers
use index (idx_state_lastname)
where state = 'NY' and last_name like 'A%';

## when indexes are ignored:
explain select customer_id from customers 
where state = 'CA' or points > 1000;
# all rows are scaned but it is still faster because it uses index (not reading data from disk)
# further optimization:
explain 
	select customer_id from customers 
	where state = 'CA'
	union
	select customer_id from customers 
	where points > 1000;
    
# whenever we use columns in expersion, mysql is not able to use indexes:

explain 
	select customer_id from customers 
	where points + 10 > 2000;
    
## use indexes for sorting data:
show indexes in customers;
drop index idx_points on customers;
drop index idx_state_lastname on customers;
drop index idx_lastname_state on customers;

explain select customer_id from customers order by state;

explain select customer_id from customers order by first_name;
# file sort is an expensive operation

show status;

explain select customer_id from customers order by state;
show status like 'last_query_cost';

explain select customer_id from customers 
order by state, points;

explain select customer_id from customers 
order by state, first_name, points;
# as first_name is not in index, this query will use filesort.

explain select customer_id from customers 
order by state, points desc;
show status like 'last_query_cost';
# sorting points desc is not using index but file sort so this is an expensive query.

explain select customer_id from customers 
order by state desc, points desc;
show status like 'last_query_cost';

explain select customer_id from customers 
order by points;
show status like 'last_query_cost';
# because the index (state, points) are sorted first based on state, within each state sort based on points
# we cannot rely on this index to sort points.alter. 

# but we can do the following:
explain select customer_id from customers 
where state = 'CA'
order by points;
show status like 'last_query_cost';

## covering indexes: (an index that covering all columns an query needs, mysql can execute the query without touching the table)

# selecting all columns is an expensive query:
explain select * from customers
order by state;
show status like 'last_query_cost';

## index maintenance:
# drop duplicate, reduandant and unused indexes.

# duplicate indexes: (a, b, c) (a, b, c)
# redundant indexes: (a, b) (a)
# non-redundant: (a, b) (b)
# non-redundant: (a, b) (b, a)







