import pandas as pd

from util.data import Data, Column


def drop_collection(movie_id: int, df: pd.DataFrame = None) -> pd.DataFrame:
    if df is None:
        df = Data.movie_meta()

    return df[~get_collection_mask(movie_id, df)]


def get_collection(movie_id: int, df: pd.DataFrame = None,
                   include_base_movie: bool = True, start_from_base_movie: bool = False, wrap_to_start: bool = False
                   ) -> pd.DataFrame:
    """
    Get movies from a collection.

    :param movie_id: a movie that is in a collection
    :param df: the pandas DataFrame to search
    :param include_base_movie: whether to include movie_id itself in the result
    :param start_from_base_movie: whether to split the result and start at movie_id
    :param wrap_to_start: if start_from_base_movie: at the end of the collection, wrap over to the start and include the prequels
    :return: a DataFrame containing the movies in the collection
    """
    if df is None:
        df = Data.movie_meta()

    # select movies that are in collection
    m = df[get_collection_mask(movie_id, df)]
    # sort by release year
    m = m.sort_values(by=Column.release_date.value)

    if not include_base_movie:
        m = m.drop(movie_id)

    if start_from_base_movie:
        # split dataframe at base_movie
        sequels = m.loc[movie_id:]
        prequels = m.loc[:movie_id - 1]

        if wrap_to_start:
            # reverse order and join again
            m = pd.concat([sequels, prequels])
        else:
            # just return the movies starting with the base movie
            m = sequels

    return m


def get_collection_mask(movie_id: int, df: pd.DataFrame = None):
    collection = df.loc[movie_id][Column.collection.value]

    return df[Column.collection.value] == collection


class CollectionFilter:
    def __init__(self, method):
        self.method = method

    def __call__(self, movie_id: int, n: int = 5):
        meta = Data.movie_meta()
        collection = meta[get_collection_mask(movie_id, meta)].index.values

        results: pd.Series = self.method(movie_id, n + 10)

        results = results.drop(collection, errors='ignore')

        return results
