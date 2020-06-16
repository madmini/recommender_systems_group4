""" pre-processing step to compile the .json files into one CSV.

depending on the value of DROP_LONG_VALUES, some fields that we deem unnecessary will be dropped
"""

import os
from typing import List, Dict

import pandas as pd
import simplejson

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(BASE_DIR, 'datasets', 'full_meta', 'extracted_content_ml-latest')

DROP_LONG_VALUES = True


def expand_property(dct: Dict[str, List[Dict]], key: str, prop: str) -> None:
    # print(dct[key])
    dct[key] = [item[prop] for item in dct[key]]


movie_meta: Dict[int, Dict] = dict()

files = os.listdir(data_dir)
percent = len(files) / 100
percent_count = 0
ctr = 0

print('[', '-' * 23, '25%', '-' * 23, '50%', '-' * 23, '75%', '-' * 22, ']', sep='')

for fn in files:
    with open(os.path.join(data_dir, fn), encoding='utf8') as f:
        ctr += 1
        if ctr >= percent:
            percent_count += 1
            ctr = 0
            print('.', end='')  # if percent_count % 10 != 0 else percent_count // 10, end='')

        if fn[-5:] != '.json':
            continue

        j: dict = simplejson.load(f)
        # print(j.keys())
        # j_prime = {j['movielensId']: {outer_key + '.'+inner_key:inner_val for (inner_key, inner_val)
        # in outer_val for (outer_key, outer_val) in j}}

        if DROP_LONG_VALUES:

            if 'tmdb' in j:
                expand_property(j['tmdb'], 'keywords', 'name')
                expand_property(j['tmdb'], 'genres', 'name')
                expand_property(j['tmdb'], 'spoken_languages', 'iso_639_1')
                expand_property(j['tmdb'], 'production_countries', 'iso_3166_1')

                del j['tmdb']['credits']
                del j['tmdb']['reviews']
                del j['tmdb']['overview']

                del j['tmdb']['id']
                del j['tmdb']['imdb_id']
                del j['tmdb']['poster_path']
                del j['tmdb']['runtime']
                del j['tmdb']['release_date']

            if 'imdb' in j:
                del j['imdb']['reviews']
                del j['imdb']['actors']
                del j['imdb']['summaries']
                del j['imdb']['synopsis']

                del j['imdb']['imdbLink']

        movielensId = int(j['movielensId'])

        movie_meta[movielensId] = {
            ((outer_key + '_' + inner_key) if outer_key != 'movielens' else inner_key): inner_val
            for outer_key, outer_val in j.items()
            if outer_key != 'movielensId'
            for inner_key, inner_val in outer_val.items()
        }

        # print(j_dim_reduced)
        #
        # print(j_dim_reduced)

        # df = pd.DataFrame.from_dict(j_dim_reduced, orient='index')
        # print(df.to_string())

print()

df: pd.DataFrame = pd.DataFrame.from_dict(movie_meta, orient='index')
print(df)
print(df.index)
df.sort_index(kind='mergesort', inplace=True)
print(df)

filename = ('movie_meta' if DROP_LONG_VALUES else 'movie_meta_full') + '.csv'

# df.to_parquet(os.path.join(data_dir, filename), compression='brotli')
# df.to_parquet(os.path.join(data_dir, filename+'.raw'))
# df.to_parquet(os.path.join(data_dir, filename + '.snappy'), compression='snappy')
# df.to_parquet(os.path.join(data_dir, filename + '.gzip'), compression='gzip')

# has lower size
df.to_csv(os.path.join(BASE_DIR, 'datasets', 'full_meta', filename))

# import with:
# pd.read_csv(path, index_col=0, dtype={3: 'boolean', 22: 'boolean', 45: 'str', 52: 'int'}, engine='c')
