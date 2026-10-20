print("Sales initialized", __name__)

# every module has a built in name attribute that is automatically created.

def calc_tax():
  pass


def calc_shipping():
  pass

# if we import this module into another module, __name__ will be 'ecommerce'.
# if we run this module directly, __name__ will be '__main__'.

if __name__ == '__main__':
  print("Sales started")
  calc_tax()


