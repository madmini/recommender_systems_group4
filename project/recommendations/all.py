from typing import List
from util.data import Data, Column


def recommend_movies(movie_id: int, n: int) -> List[int]:
    movies = Data.movies()
    results_as_list = movies['movie_id'].to_list()
    breakpoint()
    return results_as_list

