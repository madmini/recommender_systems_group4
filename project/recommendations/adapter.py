from enum import Enum
from multiprocessing.pool import ThreadPool
from typing import List, Dict, Callable

import pandas as pd

from recommendations import example
from util.data import Data
from util.movie_posters import get_poster_omdb_imdb


class Method(Enum):
    dummy = ('dummy', example.recommend_movies)

    # ADD METHODS HERE
    # internal_method_name = ('Display Name', package.method_name)

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

    @classmethod
    def default(cls):
        return cls.dummy


def recommend_movies(
        movie_id: int, n: int, method_name: str = None, method: Method = None) -> List[Dict[str, str]]:
    if method is None:
        if method_name is None:
            raise MethodNotFoundException
        method = Method[method_name]

    # recommendations: List[int] = method.method.recommend_movies(movie_id, n)
    recommendations: List[int] = method(movie_id, n)

    meta: pd.DataFrame = Data.movie_meta().loc[recommendations]

    meta_dict: List[Dict[str, str]] = meta.to_dict(orient='records')

    with ThreadPool(n) as p:
        urls = p.map(get_poster_omdb_imdb, meta['imdbMovieId'].to_list())
        for index, mapping in enumerate(meta_dict):
            mapping['omdbPoster'] = urls[index]

    return meta_dict


def get_methods() -> List[Dict[str, str]]:
    return [method.as_dict() for method in Method]


def get_movie_data(movie_id: int) -> Dict:
    meta: pd.DataFrame = Data.movie_meta()
    if movie_id not in meta:
        pass

    return meta.loc[movie_id].to_dict()  # orient='records')


class MovieNotFoundException(Exception):
    """ MovieID does not exist. """
    pass


class MethodNotFoundException(Exception):
    """ Method does not exist. """
    pass
