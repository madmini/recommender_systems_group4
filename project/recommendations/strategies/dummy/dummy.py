import pandas as pd

from util.data import Data


def sample(movie_id: int, n: int = 5) -> pd.Series:
    # just return the movies with default ordering
    return -Data.movie_meta()['movielens_id']
