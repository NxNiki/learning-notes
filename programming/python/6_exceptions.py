# cost of raising exceptions:

from timeit import timeit

code1 = """
def calculate_xfactor(age):
    if age <= 0:
        raise ValueError("Age cannot be 0 or less.")
    return 10 / age

try:
    calculate_xfactor(-1)
except ValueError as err:
    print(err)
"""

code2 = """
def calculate_xfactor(age):
    if age <= 0:
        raise ValueError("Age cannot be 0 or less.")
    return 10 / age

try:
    calculate_xfactor(-1)
except ValueError as err:
    pass
"""

code3 = """
def calculate_xfactor(age):
    if age <= 0:
        return None
    return 10 / age

res = calculate_xfactor(-1)
if res is None:
    pass

"""

print("first code=", timeit(code1, number=10000))
print("second code=", timeit(code2, number=10000))
print("third code=", timeit(code3, number=10000))
