import pandas as pd

from recommendations.shared.dcg import index_reverse_lookup_dict, dcg_similarity
from util.data_helper import directors_as_lists
from util.timer import timer


@timer
def recommend_movies(movie_id: int, n: int= None):
    # actors: pd.Series = Data.movie_meta()[Column.actors.value]
    # actors = Data.movie_meta().drop_duplicates(Column.collection.value)[Column.actors.value]

    directors: pd.Series = directors_as_lists()

    reference_directors_lookup = index_reverse_lookup_dict(directors.loc[movie_id])

    directors = directors.drop(index=movie_id)

    directors_similarity = directors.apply(dcg_similarity, args=(reference_directors_lookup,))

    return directors_similarity
