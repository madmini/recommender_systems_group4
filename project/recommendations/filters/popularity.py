from typing import Callable

import pandas as pd

from util.data_helper import get_normalized_popularity


class PopularityBias:
    def __init__(self, method: Callable[[int, int], pd.Series], score_weight: int = 1):
        self.method = method
        self.score_weight = score_weight

    def __call__(self, movie_id: int, n: int = 5):
        popularity = get_normalized_popularity()
        scores = self.method(movie_id, n)
        return (scores ** self.score_weight) * popularity
