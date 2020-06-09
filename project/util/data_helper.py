from multiprocessing.pool import ThreadPool
from typing import List, Dict

import pandas as pd

from util.data import Data, Column
from util.exception import MovieNotFoundException, UserNotFoundException
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
    if movies is None or len(movies) == 0:
        return

    # fetch poster urls asynchronously
    urls: List[str]
    with ThreadPool(len(movies)) as p:
        # urls = p.map(Poster.get_poster_omdb_imdb, meta[Column.imdb_id.value].to_list())
        urls = p.map(Poster.get_poster_tmdb, [movie[Column.tmdb_id.value] for movie in movies])

    # fill poster urls into dictionary
    for index, mapping in enumerate(movies):
        mapping[Column.poster_url.value] = urls[index]


def get_tmdb_id(movielens_id: int) -> int:
    movies = Data.movie_meta()
    if movielens_id not in movies.index:
        raise MovieNotFoundException()

    movie = movies.loc[movielens_id]
    return movie[Column.tmdb_id.value]


def get_imdb_id(movielens_id: int) -> int:
    movies = Data.movie_meta()
    if movielens_id not in movies.index:
        raise MovieNotFoundException()

    movie = movies.loc[movielens_id]
    return movie[Column.imdb_id.value]


def get_movielens_id(tmdb_id: int = None, imdb_id: int = None) -> int:
    movies: pd.DataFrame = Data.movie_meta()

    if tmdb_id is not None:
        movie = movies.query(f'{Column.tmdb_id.value} == {tmdb_id}')
    elif imdb_id is not None:
        movie = movies.query(f'{Column.imdb_id.value} == {imdb_id}')
    else:
        return None

    if movie.empty:
        return None

    return movie.index[0]


def avg_rating_for_user(user_id: int) -> float:
    """ Calculates the average score for ratings from a specified user. """
    ratings: pd.Series = Data.ratings_as_series()

    # check if user_id exists and raise exception if it does not
    if user_id not in ratings:
        raise UserNotFoundException()

    # select ratings from specified user_id
    user_ratings: pd.Series = ratings.loc[user_id]
    # calculate average using integrated function
    return user_ratings.mean()
