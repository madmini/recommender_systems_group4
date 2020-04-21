import pandas as pd

data = ['Toy Story', 'Jumanji', 'Grumpier Old Men']

# container for one-dimensional data (list, sequence)
series = pd.Series(data)

# the first element
print(series[0])

# the first two elements.
# same as [0:2], from 0 (inclusive) to 2 (exclusive, so only until series[1])
print(series[:2])

# the last two elements.
# same as [len-2:len], from second-to-last (inclusive) to len (exclusive, so only until the last element)
print(series[-2:])

# create series with predefined indices, specify index list as second parameter
series2 = pd.Series(data, ['a', 'b', 'c'])

# element 'b' of the series
print(series2['b'])
