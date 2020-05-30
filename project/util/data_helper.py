from multiprocessing.pool import ThreadPool
from typing import List, Dict

import pandas as pd

from util.data import Data, Column
from util.exception import MovieNotFoundException
from util.movie_posters import Poster


def get_movie_meta_for(movie_ids: List[int]) -> List[Dict]:
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

    add_poster_urls(meta_dict)

    return meta_dict


def add_poster_urls(movies: List[Dict]) -> None:
    # fetch poster urls asynchronously
    urls: List[str]
    with ThreadPool(len(movies)) as p:
        # urls = p.map(Poster.get_poster_omdb_imdb, meta[Column.imdb_id.value].to_list())
        urls = p.map(Poster.get_poster_tmdb, [movie[Column.tmdb_id.value] for movie in movies])

    # fill poster urls into dictionary
    for index, mapping in enumerate(movies):
        mapping[Column.poster_url.value] = urls[index]