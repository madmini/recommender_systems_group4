from itertools import cycle
from numbers import Number
from typing import Callable, Iterable, List


class Combined:

    def __init__(self, methods: List[Callable], weights: Iterable[Number] = None):
        self.methods = methods
        self.sum_weights = sum(weights) if weights is not None else len(methods)
        self.weights = weights if weights is not None else cycle([1])

    def __call__(self, movie_id: int, n: int = 5):
        result = None
        for method, weight in zip(self.methods, self.weights):
            score = method(movie_id, n)
            score = score * weight
            if result is None:
                result = score
            else:
                result += score

        return result / self.sum_weights
