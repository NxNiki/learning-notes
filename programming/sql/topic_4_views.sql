use sql_invoicing;

create view clients_balance as
select
	c.client_id
    , c.name
    , sum(invoice_total - payment_total) as balance
from clients c
join invoices i using(client_id)
group by client_id, nameclients_balance
;

drop view clients_balance;

create or replace view sales_by_client as
select
	c.client_id
    , c.name
    , sum(invoice_total) as total_sales
from clients c
join invoices i using(client_id)
group by client_id, name
;

## udateable view  
# no following clasue in views:
# distinct
# aggregate functions (sum, avg, min, max)
# group by, having
# union

create or replace view invoices_with_balance as
select
	*
    , invoice_total - payment_total as balance
from invoices
where (invoice_total - payment_total) > 0
with check option # avoid updates delete row in the view.
;

delete from invoices_with_balance
where invoice_id = 1;

update invoices_with_balance
set due_date = date_add(due_date, interval 2 day)
where invoice_id = 2;

# for times you don't have permission to update a table, you can modify data through a view

## views provides an abstract over the database table and reduce the impact of changes.
## restrict access to the data in the underlying table





