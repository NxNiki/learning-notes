
## transactions:
##ACID (atomicity, consistency, isolation, durability) 

use sql_store;
start transaction;

insert into orders (customer_id, order_date, status)
values (1, '2019-01-01', 1);

insert into order_items
values (last_insert_id(), 1, 1, 1);

commit;
# rollback;

## concurrency and locking:

show variables like 'transaction_isolation%';
set transaction isolation level serializable; # only works for next transaction
set session transaction isolation level serializable; # work for all transactions in the current session.
set global transaction isolation level serializable; # all transactions in all sessions.

## read uncommitted -> dirty reads (read uncommited changes by other session)
set transaction isolation level read uncommitted;

## read committed -> unrepeatable reads (repeated read of data can change while other session changes the data)
set transaction isolation level read committed;

## repeatable read

set transaction isolation level repeatable read;

set transaction isolation level serializable; # transaction will wait for other stansactions end.
