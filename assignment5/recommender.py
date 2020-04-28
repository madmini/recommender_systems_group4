from typing import Callable, Optional

import numpy as np
import pandas as pd


class Recommender:
    """

    """

    ratings: pd.Series
    " A pandas.DataFrame containing ratings. With multi-index (user, movie). "

    pivot: pd.DataFrame
    " A pandas.DataFrame pivot table of ratings. Columns: users, Index/Rows: movies, Values: ratings. "

    rating_colname: str
    " The column name for the rating in the ratings DataFrame. "

    user_id_colname: str
    " The column name for the user_id in the ratings DataFrame. "

    movie_id_colname: str
    " The column name for the movie_id in the movie_genres and ratings DataFrames. "

    similarities: pd.DataFrame = None
    " A pandas.Series containing the similarities between users. Calculated as needed. "

    def __init__(self, ratings: pd.Series, rating_colname: str, user_id_colname: str,
                 movie_id_colname: str, similarities: pd.DataFrame = None):
        self.ratings = ratings
        self.similarities = similarities

        # print('mem_usage: ratings')
        # print(ratings.memory_usage())

        self.rating_colname = rating_colname
        self.user_id_colname = user_id_colname
        self.movie_id_colname = movie_id_colname

        print('creating pivot table... ', end='')
        # since ratings are a pandas.Series with multiindex, simply use unstack to create pivot table
        # this turns the second level index (movie_id) into columns
        self.pivot = self.ratings.unstack()

        # store as sparse data structure (only non-nan values will be stored).
        # self.pivot = self.pivot.astype(pd.SparseDtype("float", np.nan))
        print('done.')

        # print('pivot table:')
        # print(self.pivot)

        # print(self.calculate_similarities(self.pivot, 1))
        # exit()

        # data[~np.isnan(data[target_index])]

        # print(self.pivot.loc[1].notna().rename('MovieID'))
        # print(self.pivot[self.pivot.columns[self.pivot.loc[1].notna()]])
        # exit()

        # print('mem_usage: pivot')
        # print(self.pivot.memory_usage().sum())
        # print('sparsity: pivot')
        # print(self.pivot.sparse.density)

    def test1(self, train: pd.Series, test: pd.Series, k: int):
        expected_ratings_dict = dict()

        training_movies = self.pivot.columns

        for user, target_ratings in test.groupby(self.user_id_colname):
            # print(user)

            target_ratings: pd.Series = target_ratings.loc[user]
            target_movies = target_ratings.filter(training_movies).index.values

            # print(target_ratings)
            # print(target_movies)

            trimmed_table: pd.DataFrame = self.pivot.filter(target_movies, axis='columns')
            # trimmed_table = self.pivot[self.pivot.columns[self.pivot.columns.isin(target_movies)]]

            # print(trimmed_table.tail(10).to_string())

            neighbors = self.get_k_nearest_neighbors(self.pivot, user, k=k)

            trimmed_table = trimmed_table.filter(neighbors.index.values, axis='index')

            # print(trimmed_table.to_string())

            scores: pd.DataFrame = trimmed_table.mul(neighbors, axis='index')

            # print(scores.to_string())
            # print(neighbors.sort_index())

            for movie in target_movies:
                relevant_scores: pd.Series = scores[movie]

                if relevant_scores.isna().all():
                    expected_rating = np.nan
                else:
                    # print(relevant_scores)
                    # print(neighbors[relevant_scores.notna()])
                    expected_rating = relevant_scores.sum() / neighbors[relevant_scores.notna()].sum()
                    # print(expected_rating)

                expected_ratings_dict[(user, movie)] = expected_rating

        expected_ratings = pd.Series(expected_ratings_dict)
        expected_ratings.index.rename([self.user_id_colname, self.movie_id_colname], inplace=True)

        difference: pd.Series = test - expected_ratings

        mae = difference.abs().sum() / difference.count()
        rsme = np.sqrt((difference ** 2).sum() / difference.count())

        # print('mae:  ', mae)
        # print('rsme: ', rsme)

        relevant = test > 3
        expected_relevant = expected_ratings > 3.5

        tp = sum(relevant & expected_relevant)
        fp = sum(~relevant & expected_relevant)
        fn = sum(relevant & ~expected_relevant)

        precision = tp / (tp + fp)
        recall = tp / (tp + fn)

        # print('precision: ', precision)
        # print('recall:    ', recall)

        # return mae, rsme, precision, recall
        return {'mae': mae, 'rsme': rsme, 'precision': precision, 'recall': recall}

    def recommend_movies(self, target_user_id: int, n_recommendations: int = 30, k: int = 30) -> pd.Series:
        """
        Recommends movies for a given user based on ratings by other users.

        Finds users with similar rating history, then recommends movies based on those users' other ratings.
        :param ratings: a dataframe containing ratings, with columns 'UserID','MovieID' and 'Rating'
        :param target_user_id: the id of the user to find recommendations for
        :param n_recommendations: the number of recommendations requested
        :param k: the number of neighbors to take into account
        :return: a sorted pandas.Series containing the recommendations
        """

        # print(table)

        # find n most similar neighbors
        print('calculating similarities... ', end='')
        neighbors: pd.Series = self.calculate_similarities(self.pivot, target_user_id).nlargest(k)
        print('done.')

        # filter pivot table to only contain neighbors, and exclude all movies that the target user has already rated
        new_table: pd.DataFrame = self.pivot[neighbors.keys()][np.isnan(self.pivot[target_user_id])]
        # remove rows that are just NaN
        new_table.dropna(axis='rows', how='all', inplace=True)

        # count weighted sum for each row, and retain the n movies with the largest weighted sum
        #   for mul: set axis='columns' to match neighbors index against columns of new_table
        recommended_movies: pd.Series = new_table \
            .mul(neighbors, axis='columns') \
            .apply(np.sum, axis='columns') \
            .nlargest(n_recommendations, keep='all')

        # give pandas.Series a name, so it can be joined to pandas.DataFrame
        return recommended_movies.rename('Score')

    def get_k_nearest_neighbors(self, data: pd.DataFrame, target_index: int, k: int):
        similarities: pd.Series = self.calculate_similarities(data, target_index, Recommender.distances_euclid)
        similarities.loc[target_index] = np.nan
        return similarities.nlargest(k)

    @staticmethod
    def distance_euclid(a: pd.Series, b: pd.Series) -> np.float64:
        # calculate "euclidean" distance: sqrt(sum((actual_rating - target_rating)^2))
        # tmp = a - b
        # print(tmp)
        # tmp = tmp ** 2
        # print(tmp)
        # tmp = sum(tmp)
        # print(tmp)
        # tmp = np.sqrt(tmp)
        # print(tmp)

        return np.sqrt(sum((a - b) ** 2))

    @staticmethod
    def distances_euclid(data: pd.DataFrame, target_index: int) -> pd.Series:
        # calculate "euclidean" distances: sqrt(sum((actual_rating - target_rating)^2))

        # print(data)
        tmp = data.sub(data.loc[target_index], axis='columns')
        # print(tmp)
        tmp = tmp ** 2
        # print(tmp)
        tmp = tmp.sum(axis='columns')
        # print(tmp)
        tmp = np.sqrt(tmp)
        # print(tmp)
        return tmp

    # def distance_cosine

    @classmethod
    def calculate_similarity(cls, a: pd.Series, b: pd.Series):
        overlap = a.notna() & b.notna()
        overlap_count = overlap.count()

        if overlap_count == 0:
            return np.nan

        distance = cls.distance_euclid(a, b)

        if distance == 0:
            distance = 0.5

        return overlap_count / distance

    def calculate_similarities(self, data: pd.DataFrame, target_index: int,
                               distance: Callable = distances_euclid.__func__) -> pd.Series:
        """
        Calculate the similarity to the target user for all users.

        The distance is calculated as <number of common rated movies> / <euclidean distance>
        :param data: pandas.DataFrame formatted as table with user ids as columns, movie ids as rows and ratings as value
        :param target_index: the id of the user to compare to
        :param distance: the distance function to use
        :return: the similarities for users as a pandas.Series
        """
        if self.similarities is not None:
            a: pd.Series = self.similarities.loc[target_index]
            b: pd.Series = self.similarities[target_index]
            return a.combine(b, lambda x, y: x if not np.isnan(x) else y)

        # trim the table to only include the movies that the target user has rated
        trimmed_table: pd.DataFrame = data[data.columns[data.loc[target_index].notna()]]

        # print(trimmed_table)

        # in each column (for each user) count the number of not-NaN values
        # this is the number of movies rated by both the target and the actual user
        overlap_count: pd.Series = trimmed_table.count(axis='columns')

        # print(overlap_count)

        distances: pd.Series = distance(trimmed_table, target_index)
        # where the distance is 0, edit the value
        # as this would otherwise result in "inf" similarity
        distances[distances == 0] = 0.5

        # print(distances)

        # distances is only calculated for dimensions, where actual_rating is not NaN.
        # thus, distances over fewer dimensions will be lower and need to be corrected.
        # -> calculate similarity as <number of dimensions> / <euclidean distance>
        similarity: pd.Series = overlap_count / distances

        return similarity

    def pre_calculate_similarities(self, persist: Optional[str] = None) -> pd.DataFrame:

        sparse_type = pd.SparseDtype("float", np.nan)
        user_index = self.pivot.index
        users = user_index.values
        similarities: pd.DataFrame = pd.DataFrame(columns=users)
        similarities = similarities.astype(sparse_type)

        # similarities.index = self.pivot.index

        # print(similarities)
        # print(similarities.memory_usage().sum())

        # print(users[0])

        for i, target_user in enumerate(users):
            print(target_user)
            tmp = self.calculate_similarities(self.pivot.loc[target_user:], target_user)
            tmp.iloc[0] = np.nan
            similarities[target_user] = tmp

            # print('tmp')
            # print(tmp)
            # print('similarities[target_user]')
            # print(similarities[target_user])

        # for i, target_user in enumerate(users):
        #     target_ratings: pd.Series = self.pivot.iloc[target_user]
        #
        #     target_ratings_filter = target_ratings.notna()
        #
        #     target_ratings = target_ratings[target_ratings_filter]
        #
        #     tmp = pd.Series(index=user_index)
        #
        #     for ref_user in users[:i]:
        #         ref_ratings: pd.Series = self.pivot.iloc[ref_user][target_ratings_filter]
        #
        #         similarity = self.calculate_similarity(target_ratings, ref_ratings)
        #
        #         tmp[ref_user] = similarity
        #
        #     similarities[target_user] = tmp
        #     print(target_user)

        self.similarities = similarities

        return similarities
