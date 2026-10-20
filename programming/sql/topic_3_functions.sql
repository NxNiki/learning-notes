## mysql numeric functions

select round(5.73, 1);

select truncate(5.1234, 2);

select ceiling(1.234);

select floor(1.234);

select abs(-2);

select rand(); # random value between 0 and 1.

## strings:

select length('abc');

select upper('abc');

select lower('ABC');

select ltrim('   abc');

select rtrim('abcd   ');

select left('abcdef', 2);

select right('abcdef', 3);

select substring('abcdef', 2, 3); # start position, length
select substring('abcdef', 2); # start position, length

select locate('e', 'abcdef');
select locate('e', 'abcdEf');
select locate('q', 'abcdef');
select locate('def', 'abcdef');

select replace('abc', 'c', 'C');

select concat('abc', 'def');

use sql_store;

select concat(first_name, ' ', last_name) as full_name
from customers
;

select *
from customers
;

## date and time: mysql date format strings

select now();
select curtime();
select curdate();

select year(now());
select day(now());
select hour(now());
select minute(now());
select second(now());

select dayname(now());
select monthname(now());

select extract(year from now());

select *
from orders
where year(order_date) = year(now());

select date_format(now(), '%y');
select date_format(now(), '%M %Y');
select date_format(now(), '%M %d %Y');

select time_format(now(), '%H:%i %p');

select date_add(now(), interval 1 day);
select date_add(now(), interval 1 year);
select date_add(now(), interval -1 day);

select date_sub(now(), interval 1 year);

select datediff('2021-1-10', '2020-10-10');

select time_to_sec('09:40') - time_to_sec('09:20');

select ifnull(null, 'xxx');

select coalesce(null, null, 'xxx', 'xx');


select
	concat(first_name, ' ', last_name)
    , ifnull(phone, 'not known') as phone
    , coalesce(phone, 'not known') as phone
from
	customers;
    
## if clause:

select
	order_id
    , order_date
    , if (year(order_date) = year(now()),
		'active',
        'inactive') as category
from orders;

select
	product_id
    , name
    , count(*) as orders
    , if(count(*) > 1, 'many times', 'once') as frequency
from
	products
join order_items using (product_id)
group by product_id, name;


## case clause

select
	order_id
    , case
		when year(order_date) = year(now()) then 'active'
        when year(order_date) = year(now()) - 1 then 'last year'
        when year(order_date) < year(now()) - 1 then 'archived'
        else 'future'
	end as category
from orders;
    
    







