# pipenv install numpy

import numpy as np

array = np.array([1, 2, 3])

array = np.array([[1, 2, 3], [4, 5, 6]])

print(array.shape)

array = np.zeros((3, 4))
array = np.zeros((3, 4), dtype=int)
array = np.ones((3, 4), dtype=int)
array = np.full((3, 4), 5, dtype=int)
array = np.random.random((3, 4))

array[0, 0]

array > 0.2

array[array > 0.2]

np.sum(array)

np.floor(array)

np.ceil(array)

np.round(array)

first = np.array([1,2,3])
second = np.array[1,2,3])

x = first + second
x = first + 2





