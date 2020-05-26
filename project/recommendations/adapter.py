from enum import Enum
from multiprocessing.pool import ThreadPool
from typing import List, Dict, Callable

import pandas as pd

from recommendations import dummy, similar_ratings
from util.data import Data, Column
from util.exception import MovieNotFoundException, MethodNotFoundException
from util.movie_posters import Poster


class Method(Enum):
    dummy = ('dummy', dummy.recommend_movies)

    # ADD METHODS HERE
    # internal_method_name = ('Display Name', package.method_name)
    # Note: if a method has the same internal name as an imported package, its name will hide the package name

    # similar user ratings
    similar_ratings_plain = ('Similar User Ratings', similar_ratings.recommend_movies)
    similar_ratings_above_avg = ('Similar above-avg User Ratings', similar_ratings.recommend_movies_filter_avg)
    similar_ratings_pop = ('Similar User Ratings + Popularity Bias', similar_ratings.recommend_movies_popularity_bias)

    @classmethod
    def default(cls):
        return cls.dummy

    def __init__(self, name: str, method: Callable[[int, int], List[int]]):
        # note: the field 'name' is reserved for enums
        self.display_name = name
        self.method = method

    def __call__(self, *args, **kwargs):
        return self.method(*args, **kwargs)

    def __str__(self):
        return self.name

    def as_dict(self):
        return {
            'name': self.name,
            'display_name': self.display_name
        }


def recommend_movies(movie_id: int, n: int, method_name: str = None, method: Method = None) -> List[Dict]:
    if method is None:
        if method_name is None or method_name not in Method.__members__:
            raise MethodNotFoundException(method_name)
        method = Method[method_name]

    # recommendations: List[int] = method.method.recommend_movies(movie_id, n)
    recommendations: List[int] = method(movie_id, n)

    return get_movie_data(recommendations)

    # meta: pd.DataFrame = Data.movie_meta().loc[recommendations]
    #
    # meta_dict: List[Dict[str, str]] = meta.to_dict(orient='records')
    #
    # with ThreadPool(n) as p:
    #     urls = p.map(get_poster_omdb_imdb, meta[Column.imdb_id.value].to_list())
    #     for index, mapping in enumerate(meta_dict):
    #         mapping[Column.poster_url.value] = urls[index]
    #
    # return meta_dict


def get_methods() -> List[Dict[str, str]]:
    return [method.as_dict() for method in Method]


# def get_movie_data(movie_id: int) -> Dict:
#     meta: pd.DataFrame = Data.movie_meta()
#     if movie_id not in meta:
#         pass
#
#     return meta.loc[movie_id].to_dict()  # orient='records')


def get_movie_data(movie_ids: List[int]) -> List[Dict]:
    # if single movie, pack into list
    if isinstance(movie_ids, int):
        movie_ids = [movie_ids]

    meta: pd.DataFrame = Data.movie_meta()

    try:
        # filter metadata
        meta = meta.loc[movie_ids]
    except KeyError as e:
        raise MovieNotFoundException(e.args)

    # fetch metadata for the movies, convert to dictionary
    # orientation='records' results in [{'col1': 'val1', 'col2': 'val2'}, {'col1': 'val1', ..}]
    meta_dict: List[Dict] = meta.to_dict(orient='records')

    # fetch poster urls asynchronously
    urls: List[str]
    with ThreadPool(len(movie_ids)) as p:
        # urls = p.map(Poster.get_poster_omdb_imdb, meta[Column.imdb_id.value].to_list())
        urls = p.map(Poster.get_poster_tmdb, meta[Column.tmdb_id.value].to_list())

    # fill poster urls into dictionary
    for index, mapping in enumerate(meta_dict):
        mapping[Column.poster_url.value] = urls[index]

    return meta_dict
