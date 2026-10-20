#use sql_invoicing; 

drop procedure if exists get_clients;
delimiter $$ ## this avoid MySQL to excute codes saved in the procedure by setting the whole procedure definition as a single unit
create procedure get_clients()
begin
	select * from clients;
end $$
delimiter ; #get_clients

## call procedure in other sql scripts:
call get_clients();

drop procedure if exists get_payments;

delimiter $$
create procedure get_payments (
	client_id INT,
    payment_method TINYINT
)
begin
	select *
    from payments p
    where p.client_id = ifnull(client_id, p.client_id)
		and p.payment_method = ifnull(payment_method, p.payment_method)
	;
end $$
delimiter ;

delimiter $$
## use procedure to update data:
create procedure make_payments (
	invoice_id INT
    , payment_amount DECIMAL(9, 2) # total number of digits, digits after the decimal point.
    , payment_date DATE
)
begin
	if payment_amount <= 0 then
		signal sqlstate '22003'
			set message_text = 'invalid payment amount';
	end if;
	update invoices i
		set 
			i.payment_total = payment_amount
            , i.payment_date = payment_date
		where i.invoice_id = invoice_id;
end $$
delimiter ;

## output parameters:

delimiter $$
## variables:
create procedure get_risk_factor ()
begin
	declare risk_factor decimal(9, 2) default 0;
    declare invoices_total decimal(9, 2);
    declare invoices_count int;
    
    select count(*), sum(invoice_total)
    into invoices_count, invoices_total
    from invoices;
    
    set risk_factor = invoices_total / invoices_count * 5;
    
    select risk_factor;
end $$

delimiter ;

## functions (only return a single value)
delimiter $$
CREATE FUNCTION get_client_risk_factor (
	client_id INT
)
RETURNS INTEGER
## atributes:
#deterministic
reads sql data
#modifies sql data
BEGIN
	declare risk_factor decimal(9, 2) default 0;
    declare invoices_total decimal(9, 2);
    declare invoices_count int;
    
    select count(*), sum(invoice_total)
    into invoices_count, invoices_total
    from invoices i
    where i.client_id = client_id;
    
    set risk_factor = invoices_total / invoices_count * 5;
    
    return ifnull(risk_factor, 0);

END $$

delimiter ;

select client_id, name, get_client_risk_factor(client_id) as risk_factor
from clients;

drop function if exists get_client_risk_factor;


