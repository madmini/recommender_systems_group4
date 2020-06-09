import pandas as pd

from recommendations.shared.dcg import index_reverse_lookup_dict, dcg_similarity
from util.data import Data, Column
from util.data_helper import actors_as_lists
from util.timer import timer


@timer
def recommend_movies(movie_id: int, n: int):
    # actors: pd.Series = Data.movie_meta()[Column.actors.value]
    # actors = Data.movie_meta().drop_duplicates(Column.collection.value)[Column.actors.value]

    actors: pd.Series = actors_as_lists()

    reference_actors_lookup = index_reverse_lookup_dict(actors.loc[movie_id])

    actors = actors.drop(index=movie_id)

    actors_similarity = actors.apply(dcg_similarity, args=(reference_actors_lookup,))

    return list(actors_similarity.nlargest(n).index)
