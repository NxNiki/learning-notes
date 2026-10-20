## JSON data type:

# for multiple key: value pairs

-- ALTER TABLE `sql_store`.`products` 
-- ADD COLUMN `properties` JSON NULL AFTER `unit_price`;


update products
set properties = '
{
	"dimension": [1, 2, 3],
    "weight": 10,
    "manufacturer": {"name": "sony"}
}
'
where product_id = 1;

update products
set properties = json_object(
	'weight', 10, 
	'dimension', json_array(1, 2, 3),
    'manufacturer', json_object('name', 'sony')
)
where product_id = 1;

select product_id, json_extract(properties, '$.weight') as weight
from products
where product_id = 1;

select product_id, properties -> '$.weight' as weight
from products
where product_id = 1;

select product_id, properties -> '$.dimension[0]' as weight
from products
where product_id = 1;

select product_id, properties -> '$.manufacturer.name' as weight # this returns: "sony"
from products
where product_id = 1;

select product_id, properties ->> '$.manufacturer.name' as weight # remove " in result. this returns: sony
from products
where product_id = 1;

update products
set properties = json_set(
	properties,
    '$.weight', 20,
    '$.age', 10
)
where product_id = 1;

select product_id, properties
from products
where properties ->> '$.manufacturer.name' = 'sony';

update products
set properties = json_remove(
	properties,
    '$.age'
)
where product_id = 1;

