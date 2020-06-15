from itertools import cycle
from numbers import Number
from typing import Callable, Iterable, List

import pandas as pd


class Combined:
    """ Linear combination of metrics.

    If no weights are provided, assume uniform (all equal weights).

    By default, combines additively ( (result1 * weight1 + ... + result_n * weight_n) / sum(weight_i) ),
    but is also able to combine in a multiplicative way (result1 * ... * result_n)
    """

    def __init__(self, methods: List[Callable[[int, int], pd.Series]], weights: Iterable[Number] = None,
                 normalize: bool = True, multiplicative: bool = False):
        self.methods = methods
        self.sum_weights = sum(weights) if weights is not None else len(methods)
        self.weights = weights if weights is not None else cycle([1])
        self.normalize = normalize
        self.multiplicative = multiplicative

    def __call__(self, movie_id: int, n: int = 5):
        result = None
        for method, weight in zip(self.methods, self.weights):
            score: pd.Series = method(movie_id, n)

            factor = 1.0
            # multiply with weight, normalize by dividing by the max score
            if not self.multiplicative:
                factor = weight
            if self.normalize:
                normalize_factor = score.max()
                if normalize_factor != 0:
                    factor /= normalize_factor

            score *= factor

            score = score.fillna(0)

            if result is None:
                result = score
            else:
                if self.multiplicative:
                    result = result.mul(score, fill_value=0)
                else:
                    result = result.add(score, fill_value=0)

        if not self.multiplicative:
            # normalize results
            result = result / self.sum_weights

        return result
