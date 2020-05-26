from typing import List


def recommend_movies(movie_id: int, n: int) -> List[int]:
    return list(range(movie_id + 1, movie_id + 1 + n))
