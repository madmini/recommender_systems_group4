import pandas as pd

from util.data import Data


def recommend_movies(movie_id: int, n: int = None) -> pd.Series:
    return -Data.movie_meta()['movielens_id']
