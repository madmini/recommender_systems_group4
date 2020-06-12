import os

import pandas as pd

from util.timer import timer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataset_dir = os.path.join(BASE_DIR, 'datasets')
data_dir = os.path.join(dataset_dir, 'full_meta')


@timer
def import_csv(path: str) -> pd.DataFrame:
    dtypes = {
        'tmdb.adult': 'boolean',
        'tmdb.video': 'boolean',
        'tmdb.budget': 'Int64',
        'tmdb.revenue': 'Int64',
        'tmdb.vote_count': 'Int16',
        'movielens.imdbMovieId': 'str',
        'movielens.releaseYear': 'Int16',
        'movielens.runtime': 'Int16',
    }
    df = pd.read_csv(
        path,
        index_col=0,
        dtype=dtypes, parse_dates=['movielens.releaseDate'],
        engine='c'
    )
    df.rename_axis('movieId', inplace=True)
    return df


# print('uncompressed import')
# import_csv(os.path.join(data_dir, '_movie_meta.csv'))

print('xz (7-zip) import')
df: pd.DataFrame = import_csv(os.path.join(data_dir, 'movie_meta.csv.xz'))

print(df.sample(20).to_string())

# print('number of not-nan values per col')
# print(df.notna().sum())
#
# print(df['tmdb.vote_count'].max())
# print(df.columns)

# print('xz (pandas) import')
# import_csv(os.path.join(data_dir, '_movie_meta_2.csv.xz'))

# df.to_csv(os.path.join(data_dir, '_movie_meta_s.csv'))
