## trigger: a block of SQL code that automatically get executed before or after an insert, update, or delete statement.
## it is often used to enforce data consistency.

# we can modify data in any tables except the payments table (otherwise it will fire itself and lead to infinite loop)

use sql_invoicing;
drop trigger if exists payments_after_insert;

delimiter $$
create trigger payments_after_insert
	after insert on payments
    for each row
begin
	update invoices
    set payment_total = payment_total + new.amount
    where invoice_id = new.invoice_id;
end $$
delimiter ;

## create another sql script and run:
insert into payments
values (default, 5, 3, '2020-10-10', 10, 1);

## we need to also update the invoice table when delete rows in payment
## so that payment_total is corrected computed. This is cumbersome wonder if better way to keep data consistency.

drop trigger if exists payments_after_delete;

delimiter $$
create trigger payments_after_delete
	after delete on payments
    for each row
begin
	update invoices
    set payment_total = payment_total - old.amount
    where invoice_id = old.invoice_id;
end $$
delimiter ;

delete
from payments
where payment_id = 14;

show triggers;
show triggers like 'payments%';

############################################ use trigger for auditing table changes: ########################################
# create a new table: payment_audit

drop trigger if exists payments_after_insert;

delimiter $$
create trigger payments_after_insert
	after insert on payments
    for each row
begin
	update invoices
    set payment_total = payment_total + new.amount
    where invoice_id = new.invoice_id;
    
    # update payment_audit:
    insert into payments_audit
    values (new.client_id, new.date, new.amount, 'Insert', now());
end $$
delimiter ;

## create another sql script and run:
insert into payments
values (default, 5, 3, '2020-10-10', 10, 1);

## we need to also update the invoice table when delete rows in payment
## so that payment_total is corrected computed. This is cumbersome wonder if better way to keep data consistency.

drop trigger if exists payments_after_delete;

delimiter $$
create trigger payments_after_delete
	after delete on payments
    for each row
begin
	update invoices
    set payment_total = payment_total - old.amount
    where invoice_id = old.invoice_id;
    
    # update payment_audit:
    insert into payments_audit
    values (old.client_id, old.date, old.amount, 'Insert', now());
end $$
delimiter ;

## run these to test:
insert into payments
values (default, 5, 2, '2020-10-10', 10, 1);

delete
from payments
where payment_id = 22;

######################################################## events: ###############################################

show variables like 'event%';

set global event_scheduler = on;
set global event_scheduler = off;

delimiter $$

create event yearly_delete_stale_audit_rows
on schedule
	-- at 2020-10-24
    every 1 year starts '2019-01-01' ends '2029-01-01'
do begin
	delete from payment_audit
    where action_date < now() - interval 1 year;
    #where action_date < dateadd(now(),  interval -1 year);
    #where action_date < datesub(now(),  interval 1 year);
end $$

delimiter ;


###

show events;
show events like 'yearly%';

drop event if exists yearly_delete_stale_audit_rows;

# alter event:
delimiter $$
alter event yearly_delete_stale_audit_rows
on schedule
	-- at 2020-10-24
    every 1 year starts '2019-01-01' ends '2029-01-01'
do begin
	delete from payment_audit
    where action_date < now() - interval 1 year;
    #where action_date < dateadd(now(),  interval -1 year);
    #where action_date < datesub(now(),  interval 1 year);
end $$
delimiter ;

alter event yearly_delete_stale_audit_rows enable;
alter event yearly_delete_stale_audit_rows disable;










