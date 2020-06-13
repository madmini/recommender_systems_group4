import pandas as pd

from recommendations.strategies.shared.dcg import index_reverse_lookup_dict, dcg_similarity
from util.data_helper import actors_as_lists, directors_as_lists
from util.timer import timer


def apply_dcg_to_series(movie_id: int, data: pd.Series):
    # create lookup table (look up index in list given the item)
    lookup = index_reverse_lookup_dict(data.loc[movie_id])
    # remove base movie from results
    data = data.drop(index=movie_id)
    # apply dcg similarity over the data
    return data.apply(dcg_similarity, args=(lookup,))


@timer
def same_actors(movie_id: int, n: int = None):
    actors: pd.Series = actors_as_lists()
    return apply_dcg_to_series(movie_id, actors)


@timer
def same_directors(movie_id: int, n: int = None):
    directors: pd.Series = directors_as_lists()
    return apply_dcg_to_series(movie_id, directors)
