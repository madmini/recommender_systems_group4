from typing import Tuple

import numpy as np
from pandas import DataFrame, Series

import movielens as ml


def split_data(data: DataFrame, p: float = .8) -> Tuple[DataFrame, DataFrame]:
    """
    Split a DataFrame in two.

    :param data: the DataFrame to split
    :param p: fraction of samples that should be in the first set
    :return: the two DataFrames as a tuple
    """
    # generate an array with the same size as data
    # with values True and False, with frequency p and 1-p respectively
    mask = np.random.choice([True, False], len(data), p=[p, 1 - p])

    # apply mask
    train = data.iloc[mask]
    # invert mask to get inverted selection
    test = data.iloc[~mask]
    return train, test


ratings = ml.load_ratings()
# print('data loaded')


train, test = split_data(ratings, .8)
print(train)
print(test)
