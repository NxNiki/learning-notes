# cmoparison operators:
10 > 3
10 == "10"


"bag" > "apple" # comparison is based on how the characters are sorted or ord(x).

# get the ascii code of characters:
ord("b")

# condition statements:
temperature = 35
if temperature > 30: 
  return True
elif temperature > 20:
  print("it's code)
else:
  print("...")

# ternary operator:
age = 22
if age >= 18:
  message = "eligible"
else:
  message = "not eligible"

print(message)

message = "eligible" if age >=19 else "not eligible"

# logical operators:
high_income = True
good_credit = True
student = True

if high_income and good_credit:
  print("eligible")
else:
  print)"not eligible")

if high_income or good_credit:
  print("eligible")
else:
  print)"not eligible") 

if not student:
  print("eligible")
else:
  print("not eligible")

if (high_income or good_credit) and not student:
  print("eligible")
else:
  print)"not eligible") 

# short-circuit evaluation:
# if high_income is False, the remaining arguments is not evaludated.
if high_income and good_credit and not student:
  print("eligible")

# if high_income is True, the remaining arguments is not evaludated.
if high_income or good_credit and or not student:
  print("eligible")

# chaining comparison operators:
age = 22
if age >= 10 and age < 65:
  print("eligible")

if 18 <= age < 65:
  print("eligible")

# for loops:
for number in range(3):
  print("attempt", number, (number + 1) * ".")

for number in range(1, 4):
  print("attempt", number, (number) * ".")

# add third variable as step to skip:
for number in range(1, 10, 2):
  print("attempt", number, (number) * ".")

# for...else:
successful = True
for number in range(3):
  print("attempt")
  if successful:
    print("successful")
    break

successful = False
for number in range(3):
  print("attempt")
  if successful:
    print("successful")
    break
else:
  # this is executed when for loop is finished without break
  print("attempted 3 times and fail")

# nested loops:
for x in range(5):
  # outer loop:
  for y in range(3):
    # inner loop:
    print(f"({x}, {y})")

# iterables:
print(type(range(5)))

for x in "python":
  print(x)

# while loop:
number = 100
while number > 0:
  print(number)
  number //= 2
  

command = ""
while command != "quit" and command != "QUIT":
  command = input(">")
  print("ECHO", command)

while command.lower() != "quit":
  command = input(">")
  print("ECHO", command)

# infinite loop:
while True:
  command = input(">")
  print("ECHO", command)
  if command.lower() == "quit":
    break
