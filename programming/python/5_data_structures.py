# lists:

letters = ["a", "b", "c"]
nested_lists = [[0, 1], [2, 3]]

l = [0] * 100
x = [[0] * 100 for _ in range(10)]

# this is different from:
y = [[0] *100] * 10

combined = letters + l

# convert iterable to list:
numbers = list(range(10))

chars = list("hello world!')
len(chars)

# accessing items:
letters[0]
letters[-1]

letters[0] = "A"

# slicing a string:
letters[0:3]
letters[:3]
letters[1:]

letters[::2]

numbers = list(range(20))
numbers[::2]

# return elements in reverse order:
numbers[::-1]

# list unpacking:
numbers = [1,2,3]
first, second, third = numbers

numbers = [1,2,3, 4, 4, 4]
first, second, *other = numbers
first, *other, last = numbers

# loop over lists:
for l in letters:
  print(l)

for i, l in enmuerate(letters):
  print(i, l)

items = [0, "a"]
items = (0, "a")
index, letter = items

# Adding/removing items from list:
letters.append("d")
letters.insert(0, "-")

# remove the last item
letters.pop()
letters.pop(0) # remove first item

letters.remove("b") # remove first occurrence of "b"
del letters[0]
del letters[0:3]

letters.clear() # Remove all items in a list.

# finding items:
letters.index("a")
letters.index("z") # this will get error if "z" is not in the list

if "d" in letters:
  letter.index("d")

letters.count("d")

# sorting lists:
numbers = [3, 51, 2, 8, 6]
numbers.sort() # sort work in place so we don't need to assign it to another variable

numbers.sort(reverse=True)

nsort = sorted(numbers) # this will not modify numbers

items = [
  ("product1", 10),
  ("product2", 11),
  ("product3", 12),
]
items.sort() # This will not change anything!
items.sort(key=lambda x: x[1]) # sort only takes keyword arguments!

# lambda functions:
lambda: parameter: expression

# map functions:
prices = []
for item in items:
  prices.append(item[1])

prices = list(map(lambda x: x[1], items))

# filter function:
prices = list(filter(lambda x: x[1]>11, items))

# list comprehensions:
prices = [item[1] for item in items]
prices = [item[1] for item in items if item[1] > 11]

# zip functions:
list1 = [1,2,3]
list2 = [11,22,33]

combined_list = list(zip(list1, list2))
combined_list = list(zip("ABC", list1, list2))

# stack: LIFO last in first out
stack = [1, 2, 3]
stack.append(4)
stack.pop()

# check if stack is empty:
if not stack:
  print("stack is empty")

if stack:
  print(stack[-1]) # is stack is empty, we will have an error

# queue: FIFO first in first out
queue = [1, 2, 3]
queue.pop(0)

# Every time we remove the first item, all the following items must be moved forward. So we use deque:
from collections import deque
queue = deque([])
queue.append(1)
queue.append(2)
queue.append(3)
queue.popleft()
print(queue)

if not queue:
  print("queue is empty")

# tuple: a read-only list, cannot modify or add/remove elements to/from it
point = 1, 2
point = (1, 2)
point = 1,
point = ()
print(type(point))

point = (1, 2) + (3, 4) # (1, 2, 3, 4)
point = (1, 2) * 3 # (1, 2, 1, 2, 1, 2)

point = tuple([1, 2])
t = tuple("hello world")

point = (1, 2, 3)
point[:2]

x, y, z = point

if 10 in point:
  print("exists")

point[0] = 10 # This will throw an error as a tuple is immutable.

# swap two variables:
x = 10
y = 11

z = x
x = y
y = z

# Swap x and y by using tuple
x, y = y, x

a, b = 1, 2

# arrays: dealing with large sequences of numbers.
from array import array

numbers = array("i", [1, 2, 3])
numbers.append(4)
numbers.insert(0, 0)
numbers.pop()
numbers.remove(3)

# objects in array are typed. cannot add floats or strings to int array.

# sets:

numbers = [1, 1, 2, 3, 4]
first = set(numbers)
second = {1, 4}
second.add(5)
second.remove(5)
len(second)

first | second # union of two sets
first & second # intersection of two sets
first - second # in first but not second
first ^ second # either in first or second but not both

# sets do not support indexing as it is unordered:
first[0] # ERROR

if 1 in first:
  print("yes")

# dictionary:
point = {"x": 1, "y": 2} # keys need to be immutable
point = dict(x=1, y=2)
point["x"]
point["z"] = 30

if "a" in point:
  print(point["a"])

point.get("a")
point.get("a", 0) # return 0 if key does not exist
del point["x"]

for x in point:
  print(x)

for x in point.items():
  print(x)

for key, val in point.items():
  print(key, val)

# dictionary comprehensions:
# set:
values = {x * 2 for x in range(5)}

# dict:
values = {x: x*2 for x in range(5)}

# generator object:
# Loop over large lists can be memory inefficient. so we use generator object.
values = (x*2 for x in range(10))
for x in values:
  print(x)

from sys import getsizeof
values = (x*2 for x in range(100000))
print("gen:", getsizeof(values))

len(value) # ERROR: generator has no len()

values = [x*2 for x in range(100000)]

# unpacking operator:
numbers = [1, 2, 3]
print(numbers)

print(1, 2, 3)

print(*number)

# unpack any iterables
values = [*range(5)]
values = [*"hello"]
values = [*range, *"hello"]

first = [1, 2]
second = [2]

values = [*first, "a", *second, *"hello"]

first = {"x": 1}
second = {"x": 10, "y": 2}
combined = {**first, **second, "z": 1}
# the last x is used in this case.


print("list:", getsizeof(values))


# exercies:
from pprint import pprint
sentense = "This is a common interview question"
char_frequency = {}
for char in sentence:
  if char in char_frequency:
    char_frequency[char] += 1
  else:
    char_frequency[char] = 1

pprint(char_frequency, width=1)
# dicts are unordered collections

char_frequency_sorted = sorted(
  char_frequency.items(), 
  key=lambda x: x[1], 
  reverse=True)
