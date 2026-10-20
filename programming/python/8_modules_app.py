from 8_modules_sales import calc_shipping, calc_tax
from 8_modules_sales import * # this is not recommend as this may overwite functions or variables in the current module.

calc_shipping()

import 8_modules_sales

8_modules_sales.calc_shipping()


# python search for modules in the following directories:
import sys
import(sys.path)

# import modules in a subdirectory (packages)
# A package is a container for one or more modules.
# A package is mapped to a directory and a module is mapped to a file

import ecommerce.sales
from ecommerce.sales import calc_tax

# sub-packages:
# shopping is a sub-directory under ecommerce
import ecommerce.shopping.sales

# intra-package reference:

from ecommerce.customer import contract
from ..customer import contact

# show all the attributes and methods to find in an object.
print(dir(sales))

print(sales.__name__)
print(sales.__package__)
print(sales.__file__)

# execute modules as scripts:

