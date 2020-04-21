import pandas as pd

df = pd.DataFrame({'x': [1.0, 2.0, 3.0], 'y': [4.0, 5.0, 6.0],
                   'dx': [0.25, 0.25, 0.25], 'dy': [0.5, 0.5, 0.5]})

print(df)

df = df.sub(df['x'], axis='rows')

print(df)

exit()

df = pd.DataFrame({'angles': [0, 3, 4],
                   'degrees': [360, 180, 360]},
                  index=['circle', 'triangle', 'rectangle'])

print(df)

df = df.sub([1, 2, 3], axis='rows')

# df = df - df[['x']]
print(df)

# print(df[['x']])
