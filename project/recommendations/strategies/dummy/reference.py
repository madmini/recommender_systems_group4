import pandas as pd

from util.data import Data, Column
from util.data_helper import get_movielens_id


def tmdb_reference(movie_id: int, n: int = 5):
    movie = Data.movie_meta().loc[movie_id]
    similar_tmdb = eval(movie[Column.tmdb_similar.value])

    similar = map(lambda tmdb_id: get_movielens_id(tmdb_id=tmdb_id), similar_tmdb)

    return pd.Series({item: -index for index, item in enumerate(similar)})
