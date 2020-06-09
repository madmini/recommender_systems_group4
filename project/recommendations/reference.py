from util.data import Data, Column
from util.data_helper import get_movielens_id


def recommend_movies(movie_id: int, n: int):
    movie = Data.movie_meta().loc[movie_id]
    similar_tmdb = eval(movie[Column.tmdb_similar.value])

    similar = map(lambda tmdb_id: get_movielens_id(tmdb_id=tmdb_id), similar_tmdb)

    return similar
