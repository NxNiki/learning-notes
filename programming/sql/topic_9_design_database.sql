# modeling tools:
## data modeling is an iterative process

# conceptual model:

-- microsoft visio
-- draw.io
-- lucidcharts

# logical model:

## primary key set null after delete in child table: orphan record (avoid)

# normalization:

-- normal form 
-- 1. each cell should have single value, no repeated column  (no table column can have tables as values (or no repeating groups).)
-- link table
-- 2. 
-- 3.  

## create database:
create database sql_store2;
create database if not exists sql_store2;

drop database if exists sql_store2;

## create tables:
create database if not exists sql_store2;
use sql_store2;

drop table if exists orders;
drop table if exists customers;
create table if not exists customers
(
	customer_id INT primary key auto_increment,
    first_name varchar(50) not null,
    points int not null default 0,
    email varchar(255) not null unique
);

## modify the table
alter table customers
	add last_name varchar(50) not null after first_name,
    add city varchar(50) not null,
    modify column first_name varchar(55) default '', ## column is not necessary same for add and drop.
    drop points;
    

## create relationship
create table orders
(
	order_id 	int primary key, # primary key is not null.
    customer_id int not null,
    foreign key fk_orders_customers (customer_id)
		references customers (customer_id)
        on update cascade # customer_id is a primary key and should not be changed, but this may happen in rare cases. whether to cascade it is an open question.
        on delete no action # reject deletion if customer_id is in orders.
);

## alter primary key and foreign key:
alter table orders
	add primary key (order_id),
    drop primary key,
    drop foreign key fk_orders_customers,
    add foreign key fk_orders_customers (customer_id)
		references customers (customer_id)
        on update cascade
        on delete no action;
        
## character set: a table to map each character to number.
show charset;

# utf8: mysql default character set.
# default collation: define how the characters are sorted.
# ci: case insensitive
# maxlen: bytes used to store each character.

create database db_name
	character set latin1;

alter database db_name
	character set latin1;
    
create table table1
(
	customer_id INT primary key auto_increment,
    first_name varchar(50) not null,
    points int not null default 0,
    email varchar(255) not null unique
)
character set latin1; 

alter table table1
character set latin1; 

create table table1
(
	customer_id INT primary key auto_increment,
    first_name varchar(50) character set latin1 not null,
    points int not null default 0,
    email varchar(255) not null unique
);

## storage engines:
show engines;

## MySQL has to rebuild the table when changing the storage engine:
alter table customers
engine = InnoDB;






