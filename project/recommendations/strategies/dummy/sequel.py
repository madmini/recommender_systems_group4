import pandas as pd

from recommendations.filters.collection import get_collection


def sequels(movie_id: int, n: int = 5) -> pd.Series:
    # get the movies that are in the same collection
    # then extract a slice starting at the base movie (exclusive)
    c = get_collection(movie_id).loc[movie_id + 1:]
    # put the list of movies in the right format by extracting the index
    return pd.Series(data=range(len(c), 0, -1), index=c.index)


def prequels(movie_id: int, n: int = 5) -> pd.Series:
    c = get_collection(movie_id).loc[:movie_id - 1]
    return pd.Series(data=range(len(c), 0, -1), index=c.index)
