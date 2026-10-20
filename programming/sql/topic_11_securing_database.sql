## securing the database:

# 
create user john identified by '12345'; # password

# user can connect from any computers in this domain.
create user john@127.0.0.1;
create user john@localhost;
create user john@codewithmosh.com; # user can connect from any computers in this domain.
create user john@'%.codewithmosh.com'; # user can connect from any computers in this domain and the subdomains.

## viewing users:
select * from mysql.user;

create user bob@codewithmosh.com identified by '123';
drop user bob@codewithmosh.com;
set password for john = '1234';

# set your own password:
set password = '1234';

## granting privileges:
-- 1: web/desktop application that read and write data in database


create user moon_app identified by '1234'; # always use strong passwords
grant select, insert, update, delete, execute
on sql_store.* 
# on sql_store.customers
to moon_app;
# to moon_app@****; # host/IP/domain name.

-- 2: Admin a database

grant all
on sql_store.* # *.* # all tables in all databases.
to john;

show grants for john;

## revoke privileges:
grant create view
on sql_store.*
to moon_app;

revoke create view
on sql_store.*
from moon_app;
