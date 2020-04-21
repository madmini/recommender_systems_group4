import numpy as np
import pandas as pd

user_id_colname = 'UserID'
movie_id_colname = 'MovieID'
rating_colname = 'Rating'


def recommend_movies(ratings: pd.DataFrame, target_user_id: int,
                     n_recommendations: int = 30, n_neighbors: int = 30) -> pd.Series:
    """
    Recommends movies for a given user based on ratings by other users.

    Finds users with similar rating history, then recommends movies based on those users' other ratings.
    :param ratings: a dataframe containing ratings, with columns 'UserID','MovieID' and 'Rating'
    :param target_user_id: the id of the user to find recommendations for
    :param n_recommendations: the number of recommendations requested
    :param n_neighbors: the number of neighbors to take into account
    :return: a sorted pandas.Series containing the recommendations
    """
    # create a new (pivot) table where:
    #   the columns are the users
    #   the rows are the movies
    #   the values are the ratings
    table = pd.pivot_table(ratings, values=rating_colname, index=movie_id_colname, columns=user_id_colname)

    # find n most similar neighbors
    # might be more than n_neighbors, since keep='all' will retain users with the same similarity,
    # but does not really matter
    neighbors_similarity: pd.Series = get_similarity(table, target_user_id).nlargest(n_neighbors, keep='all')

    # filter pivot table to only contain neighbors, and exclude all movies that the target user has already rated
    new_table: pd.DataFrame = table[neighbors_similarity.keys()][np.isnan(table[target_user_id])]
    # remove rows that are just NaN
    new_table.dropna(axis='rows', how='all', inplace=True)

    # count weighted sum for each row, and retain the n movies with the largest weighted sum
    #   for mul: set axis='columns' to match neighbors_similarity index against columns of new_table
    recommended_movies: pd.Series = new_table \
        .mul(neighbors_similarity, axis='columns') \
        .apply(np.sum, axis='columns') \
        .nlargest(n_recommendations, keep='all').head(n_recommendations)

    # give pandas.Series a name, so it can be joined to pandas.DataFrame
    return recommended_movies.rename('RecommendationScore')


def get_similarity(table: pd.DataFrame, target_user_id: int) -> pd.Series:
    """
    Calculate the similarity to the target user for all users.

    The distance is calculated as <number of common rated movies> / <euclidean distance>
    :param table: pandas.DataFrame formatted as table with user ids as columns, movie ids as rows and ratings as value
    :param target_user_id: the id of the user to compare to
    :return: the similarities for users as a pandas.Series
    """
    # trim the table to only include the movies that the target user has rated
    trimmed_table: pd.DataFrame = table[~np.isnan(table[target_user_id])]

    # in each column (for each user) count the number of not-NaN values
    # this is the number of movies rated by both the target and the actual user
    overlap_count: pd.Series = trimmed_table.count('index')

    # calculate "euclidean" distances: sqrt(sum((actual_rating - target_rating)^2))
    distances: pd.Series = trimmed_table \
        .sub(trimmed_table[target_user_id], axis='rows') \
        .apply(np.square) \
        .apply(np.sum, axis='rows') \
        .apply(np.sqrt)

    # distances is only calculated for dimensions, where actual_rating is not NaN.
    # thus, distances over fewer dimensions will be lower and need to be corrected.
    # -> calculate similarity as <number of dimensions> / <euclidean distance>
    similarity: pd.Series = overlap_count / distances
    # where the distance is 0, take the number of dimensions instead, as this would otherwise result in "inf" similarity
    similarity[distances == 0] = overlap_count

    return similarity
