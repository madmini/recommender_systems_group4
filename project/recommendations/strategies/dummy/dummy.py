import pandas as pd

from util.data import Data


def sample(movie_id: int, n: int = 5) -> pd.Series:
    return -Data.movie_meta()['movielens_id']
