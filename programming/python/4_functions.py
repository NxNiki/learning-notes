
# 1- Perform a task
def greet(name):
  print(f"Hi {name}")

print(greet("mosh"))
# this return None as greet returns no values
  
# 2- Return a value
def get_greeting(name):
  return f"Hi {name}"

message = get_greeting("Mosh")

file = open("content.txt", "w")
file.write(message)

# keyword arguments:
def increment(number, by):
  return number + by

result = increment(2, 1)
print(result)

print(increment(2, 1))

increment(2, by=1)

# default arguments:
def increment(number, by=1):
  return number + by

increment(2)

# xargs:
def multiply(*number):
  print(numbers)
  total = 1
  for n in numbers:
    total *= number
  return total

multiple(2, 3, 4, 5)

# xxargs:
def save_user(**user):
  print(user)
  print(user["id"])
  print(user["name"])

save_user(id=1, name="john", age=22)

# scope of variables:

# local variables of function:
def greet(name):
  message = "a"

# python will release the memory of local variables (garbage collection) after running the above function.

print(message) # message is undefined.
print(name) # name is undefined too.

# global variables:
g_var = "a"

def greet(name):
  message = "b"

greet("mosh")
print(message) # this is still "a" (this is only for immutable variable, for mutable variables such as list, it will be modified!)


# modify global varible inside a function (not god practice)
g_var = "a"

def greet(name):
  global message
  message = "b"

greet("mosh")
print(message) # this is "b"


