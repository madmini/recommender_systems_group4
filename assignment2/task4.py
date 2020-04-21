import pandas as pd

file_path = 'the-movies-dataset/ratings_small.csv'

# load ratings_small into a dataframe
df = pd.read_csv(file_path, encoding='utf8')

# group ratings by movieId
df_grouped = df.groupby('movieId')

# instead of iterating over groups, use built-in aggregation functions
# use NamedAgg to aggregate into specified format
# <measure name>=pd.NamedAgg(column='<column to aggregate over>', aggfunc='<aggregation function>')
# where aggfunc can be callable or a string alias
# see https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html#named-aggregation
df_grouped_measures = df_grouped.aggregate(
    rating_mean=pd.NamedAgg(column='rating', aggfunc='mean'),
    rating_median=pd.NamedAgg(column='rating', aggfunc='median'),
)

# add .to_string() to print all lines
print(df_grouped_measures)
