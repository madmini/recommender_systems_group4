import pandas as pd

data = [['Toy Story', 21.946943], ['Jumanji', 17.015539], ['Grumpier Old Men', 11.7129]]

# dataframe from data with specified column names (container for two-dimensional data)
df = pd.DataFrame(data, columns=['title', 'popularity'])

# sorted by popularity, ascending (ascending=True can be omitted, as this is the default value)
df_sorted = df.sort_values(by='popularity')

print(df_sorted)
