from typing import Tuple

import numpy as np
from pandas import DataFrame, Series, read_csv, MultiIndex, Index
import matplotlib

import movielens as ml
from recommender import Recommender


def export_mask(mask: np.ndarray):
    Series(mask).to_csv('training_mask.csv.bz2')


def import_mask() -> np.ndarray:
    df: DataFrame = read_csv('training_mask.csv.bz2', usecols=[1])
    s: Series = df.squeeze(axis='columns')
    a: np.ndarray = s.to_numpy()
    return a


def export_similarities(similarities: DataFrame):
    similarities.to_csv('similarities.csv.bz2')


def import_similarities() -> DataFrame:
    print('loading similarities... ', end='')
    similarities = read_csv('similarities.csv.bz2', index_col='UserID')
    similarities.columns = ratings.index.levels[0].values
    print('done.')
    return similarities


def split_data(data: Series, p: float = .8, mask=None) -> Tuple[Series, Series, np.ndarray]:
    """
    Split a DataFrame in two.

    :param data: the DataFrame to split
    :param p: fraction of samples that should be in the first set
    :return: the two DataFrames as a tuple
    """
    if mask is None:
        # generate an array with the same size as data
        # with values True and False, with frequency p and 1-p respectively
        mask = np.random.choice([True, False], len(data), p=[p, 1 - p])

    # apply mask
    train = data.iloc[mask]
    # invert mask to get inverted selection
    test = data.iloc[~mask]
    return train, test, mask


print('loading ratings... ', end='')
ratings = ml.load_ratings_series()
print('done.')

similarities = None
# similarities = import_similarities()

# split into training and test sets
train, test, mask = split_data(ratings)#, mask=import_mask())

r = Recommender(train, ml.rating, ml.user_id, ml.movie_id, similarities)

for samplesize in [10, 100, 1000]:
    sample = test.sample(samplesize)
    ks = [3, 5, 7, 10, 15, 20, 25, 30, 50, 75, 100, 150, 200, 250]
    results: list = []
    for k in ks:
        print(k)
        result = r.test1(train, sample, k)
        results.append(result)
        # results[k] = result
        # for metric in ['mae', 'rsme', 'precision', 'recall']:
        #     results[(k, metric)] = result[metric]

    print(results)
    results: DataFrame = DataFrame(results, index=ks)
    # results: DataFrame = DataFrame(list(results.values()), index=MultiIndex.from_tuples(results.keys())).unstack()
    results.index.rename('k', inplace=True)
    print(results.to_string())

    results.to_csv('results'+str(samplesize)+'.csv')
    plot = results.plot().get_figure().savefig('results'+str(samplesize))


#
# r = Recommender(train, ml.rating, ml.user_id, ml.movie_id, similarities)
# similarities = r.pre_calculate_similarities()
# export_similarities(similarities)

# print(similarities)

# exit()
#
# print('loading similarities... ', end='')
# similarities = read_csv('similarities.csv.bz2', index_col='UserID')
# similarities.columns = ratings.first_valid_index.values
# print('done.')
# print(similarities)
#
#
# exit()
#
#
#
# r.recommend_movies(1)
