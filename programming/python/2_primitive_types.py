# primitive types in Python include int, float, string, and boolean.

# modulus operator
10 % 3

# format strings:
x = 10
y = 's'
s = f"{x}_{y}"


x = input("x: ") # this will read x as a string
print(type(x))

# convert this to a numeric value:
int(x)
float(x)

# Other function for type conversion
bool(x)
str(x)


# Falsy values in Python:
""
0
None
# Anything else will be interpreted as True

bool("False") # is True

