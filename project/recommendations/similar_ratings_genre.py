from typing import List

import pandas as pd
from recommendations import genre_filter

from util.exception import MissingDataException
from util.data import Data, Column


def recommend_movies_filter_genre(movie_id: int, n: int):
    return recommend_movies_genre(movie_id, n)


def recommend_movies_filter_genre_user_bias(movie_id: int, n: int):
    return recommend_movies_genre(movie_id, n, user_bias=True)


def recommend_movies_filter_genre_popularity_bias(movie_id: int, n: int):
    return recommend_movies_genre(movie_id, n, user_bias=True, popularity_bias=True)


def recommend_movies_genre(movie_id: int, n: int, popularity_bias: bool = False, user_bias: bool = False):
    # Get similar movies based on genre
    results = genre_filter.get_movies_with_similar_genres(movie_id, n, popularity_bias=popularity_bias, user_bias=user_bias)
    top_n_results = results.nlargest(n)
    # export the list of movies
    results_as_list = top_n_results.index.to_list()
    # breakpoint()
    return results_as_list

