from itertools import cycle
from typing import Callable, List

import pandas as pd


class SlotBased:

    def __init__(self, methods: List[Callable[[int, int], pd.Series]], slots: List[int] = None):
        self.methods = methods
        self.total_slots = sum(slots) if slots is not None else len(methods)
        self.slots = slots if slots is not None else cycle([1])

    def __call__(self, movie_id: int, n: int = 5):
        scores = []
        for method, n_slots in zip(self.methods, self.slots):
            method_result = method(movie_id, self.total_slots)
            method_scores = method_result.nlargest(self.total_slots).index.tolist()
            scores.append(method_scores)

        print(scores)

        self._remove_duplicates(scores, self.slots)

        print(scores)

        result = []
        for scores_a, slots_a in zip(scores, self.slots):
            result.extend(scores_a[:slots_a])

        print(result)

        return pd.Series(data=range(len(result), 0, -1), index=result)

    @staticmethod
    def _remove_duplicates(scores, slots):
        # scores_sets = [set(s) for s in scores]

        for index, (scores_a, slots_a) in enumerate(zip(scores, slots)):

            relevant_a = set(scores_a)
            for scores_b, slots_b in zip(scores[index + 1:], slots[index + 1:]):
                # find common movies
                common = relevant_a.intersection(scores_b)
                # remove all common movies from ONE of the sets its in
                for item in common:
                    # remove it from the set that has more "surplus" space
                    # (more recommendations than it needs to fill its slots)
                    if (len(scores_a) - slots_a) > (len(scores_b) - slots_b):
                        scores_a.remove(item)
                    else:
                        scores_b.remove(item)
