import pandas as pd

from recommendations.collection import get_collection


def sequels(movie_id: int, n: int = None) -> pd.Series:
    c = get_collection(movie_id).loc[movie_id + 1:]
    return pd.Series(range(len(c), 0, -1), index=c.index)


def prequels(movie_id: int, n: int = None) -> pd.Series:
    c = get_collection(movie_id).loc[:movie_id - 1]
    return pd.Series(range(len(c), 0, -1), index=c.index)
